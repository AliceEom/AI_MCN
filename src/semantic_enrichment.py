from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .text_scoring import BrandBrief
from .utils import normalize_text


@dataclass
class SemanticResult:
    semantic_alignment_score: float
    tone_match_score: float
    red_flags: list[str]
    alignment_rationale: str


def _tone_keywords(goal: str) -> list[str]:
    g = normalize_text(goal)
    if "conversion" in g:
        return ["review", "demo", "before after", "results", "routine"]
    return ["story", "favorites", "tips", "routine", "guide"]


def enrich_top_candidates(candidates_df: pd.DataFrame, brief: BrandBrief) -> dict[str, SemanticResult]:
    if candidates_df.empty:
        return {}

    texts = candidates_df["channel_text"].fillna("").astype(str).tolist()
    query = brief.brief_md

    vec = TfidfVectorizer(max_features=1800, ngram_range=(1, 2), stop_words="english", min_df=1)
    mat = vec.fit_transform(texts + [query])
    sim = cosine_similarity(mat[:-1], mat[-1])[:, 0]

    tone_terms = _tone_keywords(brief.campaign_goal)
    must_terms = [normalize_text(x) for x in brief.must_keywords if str(x).strip()]
    exclude_terms = [normalize_text(x) for x in brief.exclude_keywords if str(x).strip()]

    results: dict[str, SemanticResult] = {}
    for idx, row in candidates_df.reset_index(drop=True).iterrows():
        cid = str(row["_channel_id"])
        text = normalize_text(row.get("channel_text", ""))

        tone_match = 0.0
        if tone_terms:
            tone_hit = sum(1 for t in tone_terms if t in text)
            tone_match = min(1.0, tone_hit / max(len(tone_terms), 1))

        must_hit = sum(1 for t in must_terms if t and t in text)
        exclude_hit = sum(1 for t in exclude_terms if t and t in text)

        semantic = float(sim[idx])
        semantic = max(0.0, min(1.0, semantic + 0.04 * must_hit - 0.08 * exclude_hit))

        red_flags: list[str] = []
        if exclude_hit > 0:
            red_flags.append("Contains excluded keyword signals")
        if semantic < 0.20:
            red_flags.append("Low semantic relevance to brand brief")
        if row.get("n_videos", 0) < 5:
            red_flags.append("Low channel activity in current dataset")

        rationale = (
            f"Semantic fit={semantic:.2f}, tone match={tone_match:.2f}, "
            f"must-keyword hits={must_hit}, exclusion hits={exclude_hit}."
        )

        results[cid] = SemanticResult(
            semantic_alignment_score=semantic,
            tone_match_score=tone_match,
            red_flags=red_flags,
            alignment_rationale=rationale,
        )

    return results
