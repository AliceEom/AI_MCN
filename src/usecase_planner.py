from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class UseCasePlanMeta:
    awareness_cut: float
    conversion_cut: float
    evidence_cut: float
    videos_cut: float
    budget_usd: float
    clicks: float
    conversions: float
    revenue_usd: float


@dataclass(frozen=True)
class UseCasePlanResult:
    plan_df: pd.DataFrame
    meta: UseCasePlanMeta


def _num(series_or_scalar: object) -> pd.Series:
    return pd.to_numeric(series_or_scalar, errors="coerce")


def build_usecase_plan(topn_df: pd.DataFrame, roi: dict) -> UseCasePlanResult:
    plan = topn_df.copy()

    budget = float(roi.get("budget_usd", 50000.0))
    clicks = float(roi.get("clicks", 49999.0))
    conversions = float(roi.get("conversions", 1499.0))
    revenue = float(roi.get("revenue", 56962.0))

    if plan.empty:
        meta = UseCasePlanMeta(
            awareness_cut=0.0,
            conversion_cut=0.0,
            evidence_cut=0.0,
            videos_cut=0.0,
            budget_usd=budget,
            clicks=clicks,
            conversions=conversions,
            revenue_usd=revenue,
        )
        return UseCasePlanResult(plan_df=plan, meta=meta)

    # Ensure required columns exist and are numeric-safe.
    numeric_defaults = {
        "median_views": 0.0,
        "final_score": 0.0,
        "evidence_score": 0.0,
        "tfidf_similarity": 0.0,
        "semantic_score": 0.0,
        "tone_match_score": 0.0,
        "engagement_score": 0.0,
        "n_videos": 0.0,
    }
    for col, default in numeric_defaults.items():
        if col not in plan.columns:
            plan[col] = default
        plan[col] = _num(plan[col]).fillna(default)

    if "channel_title" not in plan.columns:
        plan["channel_title"] = plan.get("_channel_id", pd.Series(range(len(plan)), index=plan.index)).astype(str)
    else:
        plan["channel_title"] = plan["channel_title"].fillna(plan.get("_channel_id", pd.Series(range(len(plan)), index=plan.index)).astype(str))

    plan["_reach_index"] = np.log1p(plan["median_views"].clip(lower=0.0))
    max_reach = float(plan["_reach_index"].max()) if float(plan["_reach_index"].max()) > 0 else 1.0
    plan["_reach_index"] = plan["_reach_index"] / max_reach

    weight = (
        0.55 * plan["final_score"].fillna(0.0)
        + 0.25 * plan["evidence_score"].fillna(0.0)
        + 0.20 * plan["_reach_index"].fillna(0.0)
    ).clip(lower=0.0)
    if float(weight.sum()) <= 0:
        weight = pd.Series(np.ones(len(plan)), index=plan.index)
    weight = weight / float(weight.sum())

    plan["plan_budget_usd"] = (weight * budget).round(0)
    plan["plan_clicks"] = (weight * clicks).round(0)
    plan["plan_conversions"] = (weight * conversions).round(0)
    plan["plan_revenue_usd"] = (weight * revenue).round(0)

    plan["fit_index"] = (
        0.55 * plan["tfidf_similarity"].fillna(0.0)
        + 0.30 * plan["semantic_score"].fillna(0.0)
        + 0.15 * plan["tone_match_score"].fillna(0.0)
    ).clip(lower=0.0, upper=1.0)
    plan["awareness_index"] = (
        0.70 * plan["_reach_index"].fillna(0.0)
        + 0.30 * plan["evidence_score"].fillna(0.0)
    ).clip(lower=0.0, upper=1.0)
    plan["conversion_index"] = (
        0.50 * plan["fit_index"].fillna(0.0)
        + 0.30 * plan["engagement_score"].fillna(0.0)
        + 0.20 * plan["evidence_score"].fillna(0.0)
    ).clip(lower=0.0, upper=1.0)

    awareness_cut = float(plan["awareness_index"].median())
    conversion_cut = float(plan["conversion_index"].median())
    evidence_cut = float(plan["evidence_score"].quantile(0.20))
    videos_cut = float(plan["n_videos"].quantile(0.20))

    tiers: list[str] = []
    for _, r in plan.iterrows():
        evidence = float(r.get("evidence_score", 0.0))
        n_videos = float(r.get("n_videos", 0.0))
        aw = float(r.get("awareness_index", 0.0))
        cv = float(r.get("conversion_index", 0.0))

        if (evidence <= evidence_cut) and (n_videos <= videos_cut):
            tiers.append("Pilot/Test")
        elif (aw >= awareness_cut) and (aw > cv):
            tiers.append("Awareness-focused")
        elif cv >= conversion_cut:
            tiers.append("Conversion-focused")
        else:
            tiers.append("Balanced")

    plan["activation_tier"] = tiers

    # Readability guardrail: ensure at least one awareness and one conversion.
    if "Awareness-focused" not in set(plan["activation_tier"].tolist()):
        aw_idx = plan["awareness_index"].idxmax()
        plan.loc[aw_idx, "activation_tier"] = "Awareness-focused"

    if "Conversion-focused" not in set(plan["activation_tier"].tolist()):
        remaining = plan[plan["activation_tier"] != "Awareness-focused"]
        if not remaining.empty:
            cv_idx = remaining["conversion_index"].idxmax()
        else:
            cv_idx = plan["conversion_index"].idxmax()
        plan.loc[cv_idx, "activation_tier"] = "Conversion-focused"

    concept = []
    for _, r in plan.iterrows():
        tier = r["activation_tier"]
        tone = float(r.get("tone_match_score", 0.0))
        if tier == "Conversion-focused":
            concept.append("Concept 2 (Results Comparison)")
        elif tier == "Awareness-focused":
            concept.append("Concept 1 (Daily Routine)")
        elif tone >= 0.4:
            concept.append("Concept 3 (Q&A Conversion Hook)")
        else:
            concept.append("Concept 1 + 3 Mix")
    plan["content_concept"] = concept

    product = []
    for _, r in plan.iterrows():
        tier = str(r.get("activation_tier", "Balanced"))
        if tier == "Awareness-focused":
            product.append("Relief Sun SPF + Glow Serum (hero awareness)")
        elif tier == "Conversion-focused":
            product.append("Relief Sun SPF + Glow Serum (proof angle)")
        elif tier == "Pilot/Test":
            product.append("Relief Sun SPF + Glow Serum mini-trial CTA")
        else:
            product.append("Relief Sun SPF + Glow Serum (education + social proof)")
    plan["product_plan"] = product

    meta = UseCasePlanMeta(
        awareness_cut=awareness_cut,
        conversion_cut=conversion_cut,
        evidence_cut=evidence_cut,
        videos_cut=videos_cut,
        budget_usd=budget,
        clicks=clicks,
        conversions=conversions,
        revenue_usd=revenue,
    )
    return UseCasePlanResult(plan_df=plan, meta=meta)

