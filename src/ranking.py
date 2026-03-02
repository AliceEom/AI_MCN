from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .utils import min_max_scale


@dataclass
class RankingOutput:
    scored_channels: pd.DataFrame
    top5: pd.DataFrame


def merge_semantic_scores(channel_df: pd.DataFrame, semantic_map: dict[str, object]) -> pd.DataFrame:
    out = channel_df.copy()

    sem = []
    tone = []
    red = []
    rationale = []
    for _, row in out.iterrows():
        cid = str(row["_channel_id"])
        item = semantic_map.get(cid)
        if item is None:
            sem.append(0.0)
            tone.append(0.0)
            red.append([])
            rationale.append("No semantic enrichment for this candidate.")
            continue
        sem.append(float(item.semantic_alignment_score))
        tone.append(float(item.tone_match_score))
        red.append(item.red_flags)
        rationale.append(item.alignment_rationale)

    out["semantic_score"] = sem
    out["tone_match_score"] = tone
    out["red_flags"] = red
    out["alignment_rationale"] = rationale
    return out


def compute_final_scores(channel_df: pd.DataFrame, use_ml: bool = True) -> pd.DataFrame:
    out = channel_df.copy()

    out["engagement_score"] = min_max_scale(out["mean_engagement"])
    for c in ["n_videos", "median_views", "median_likes", "median_comments"]:
        if c not in out.columns:
            out[c] = 0.0

    # Reliability guardrail: down-rank channels with very weak observed evidence.
    out["scale_score"] = min_max_scale(np.log1p(pd.to_numeric(out["median_views"], errors="coerce").fillna(0.0)))
    out["activity_score"] = min_max_scale(np.log1p(pd.to_numeric(out["n_videos"], errors="coerce").fillna(0.0)))
    out["interaction_score"] = min_max_scale(
        np.log1p(
            pd.to_numeric(out["median_likes"], errors="coerce").fillna(0.0)
            + pd.to_numeric(out["median_comments"], errors="coerce").fillna(0.0)
        )
    )
    out["evidence_score"] = (
        0.55 * out["scale_score"]
        + 0.30 * out["activity_score"]
        + 0.15 * out["interaction_score"]
    ).clip(0.0, 1.0)

    out["credibility_multiplier"] = (0.35 + 0.65 * out["evidence_score"]).clip(0.20, 1.0)

    low_signal_mask = (
        (pd.to_numeric(out["median_views"], errors="coerce").fillna(0.0) < 100.0)
        & (pd.to_numeric(out["median_likes"], errors="coerce").fillna(0.0) <= 1.0)
        & (pd.to_numeric(out["median_comments"], errors="coerce").fillna(0.0) <= 1.0)
    )
    out.loc[low_signal_mask, "credibility_multiplier"] = out.loc[low_signal_mask, "credibility_multiplier"] * 0.30
    out["credibility_multiplier"] = out["credibility_multiplier"].clip(0.08, 1.0)

    out["eligible_recommendation"] = (
        (out["evidence_score"] >= 0.20)
        | (pd.to_numeric(out["median_views"], errors="coerce").fillna(0.0) >= 500.0)
        | (pd.to_numeric(out["n_videos"], errors="coerce").fillna(0.0) >= 12.0)
    )

    if "ml_potential_score" not in out.columns:
        out["ml_potential_score"] = 0.0

    if use_ml:
        w = {
            "sna": 0.30,
            "tfidf": 0.20,
            "semantic": 0.15,
            "tone": 0.10,
            "eng": 0.15,
            "ml": 0.10,
        }
    else:
        w = {
            "sna": 0.34,
            "tfidf": 0.24,
            "semantic": 0.18,
            "tone": 0.10,
            "eng": 0.14,
            "ml": 0.00,
        }

    out["final_score_base"] = (
        w["sna"] * out["sna_score"].fillna(0)
        + w["tfidf"] * out["tfidf_similarity"].fillna(0)
        + w["semantic"] * out["semantic_score"].fillna(0)
        + w["tone"] * out["tone_match_score"].fillna(0)
        + w["eng"] * out["engagement_score"].fillna(0)
        + w["ml"] * out["ml_potential_score"].fillna(0)
    )
    out["final_score"] = out["final_score_base"] * out["credibility_multiplier"]

    out = out.sort_values("final_score", ascending=False).reset_index(drop=True)
    return out


def select_top_with_diversity(scored_df: pd.DataFrame, top_n: int = 5, min_communities: int = 3) -> pd.DataFrame:
    ranked = scored_df.sort_values("final_score", ascending=False).copy()
    if "eligible_recommendation" in ranked.columns:
        eligible = ranked[ranked["eligible_recommendation"] == True].copy()
        if len(eligible) >= top_n:
            ranked = eligible

    initial = ranked.head(top_n).copy()

    if initial["community_id"].nunique() >= min_communities:
        return initial.reset_index(drop=True)

    selected = []
    used_communities: set[int] = set()
    for _, row in ranked.iterrows():
        cid = int(row["community_id"])
        if len(selected) < top_n:
            if cid not in used_communities or len(used_communities) < min_communities:
                selected.append(row)
                used_communities.add(cid)
                continue

        if len(selected) >= top_n:
            break

    if len(selected) < top_n:
        selected_ids = {str(r["_channel_id"]) for r in selected}
        for _, row in ranked.iterrows():
            if str(row["_channel_id"]) in selected_ids:
                continue
            selected.append(row)
            if len(selected) >= top_n:
                break

    top = pd.DataFrame(selected).head(top_n)
    top = top.sort_values("final_score", ascending=False).reset_index(drop=True)
    return top


def create_ranking(channel_df: pd.DataFrame, use_ml: bool = True, top_n: int = 5) -> RankingOutput:
    scored = compute_final_scores(channel_df, use_ml=use_ml)
    top = select_top_with_diversity(scored, top_n=top_n)
    return RankingOutput(scored_channels=scored, top5=top)
