from __future__ import annotations

"""
Step-by-step helper functions for Colab demonstrations.

This module is intentionally explicit and verbose so reviewers can follow
each stage of the project workflow independently.
"""

from dataclasses import replace
from pathlib import Path
from typing import Any

import pandas as pd

from ai_mcn_submission.config import (
    CACHE_DIR,
    COMMENTS_CSV,
    DEFAULT_CONFIG,
    MASTER_CSV,
    PLOTS_DIR,
    VIDEOS_CSV,
)
from ai_mcn_submission.analysis_categories import get_analysis_category_table
from ai_mcn_submission.data_prep import load_data, prepare_all
from ai_mcn_submission.ml_modeling import run_ml_suite
from ai_mcn_submission.network_scoring import build_channel_graph, compute_network_scores
from ai_mcn_submission.orchestrator import run_pipeline
from ai_mcn_submission.ranking import create_ranking, merge_semantic_scores
from ai_mcn_submission.semantic_enrichment import enrich_top_candidates
from ai_mcn_submission.text_scoring import build_brand_brief, compute_text_scores
from ai_mcn_submission.visualization import (
    community_figure,
    model_cv_figure,
    network_figure,
    roi_funnel_figure,
    score_breakdown_figure,
)


def default_brand_params() -> dict[str, Any]:
    """Return the default demo campaign used in the project."""
    return {
        "brand_name": "Beauty of Joseon",
        "product_name": "Relief Sun SPF + Glow Serum",
        "category": "Skincare",
        "target_audience": "US Gen Z and Millennial users with sensitive or acne-prone skin, looking for daily lightweight skincare.",
        "campaign_goal": "Awareness + trial conversion",
        "budget_usd": 50000,
        "usp": "Gentle K-beauty skincare with strong UV care and lightweight texture for daily use.",
        "must_keywords": ["sunscreen", "spf", "sensitive skin", "k-beauty"],
        "exclude_keywords": ["music", "gaming", "movie", "trailer"],
        "market": "United States",
    }


def get_analysis_category_overview() -> pd.DataFrame:
    """
    Return the full analysis/modeling taxonomy table used in this submission.

    This table is intended for grading slides and notebook documentation.
    """
    return get_analysis_category_table()


def run_data_preparation_step(brand_params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Load raw CSV files and run data cleaning + channel aggregation.
    """
    p = brand_params or default_brand_params()
    brief = build_brand_brief(p)

    videos_raw, comments_raw, master_raw = load_data(VIDEOS_CSV, COMMENTS_CSV, MASTER_CSV)
    prepared = prepare_all(
        videos_raw,
        comments_raw,
        must_keywords=brief.must_keywords,
        exclude_keywords=brief.exclude_keywords,
    )

    summary = {
        "videos_raw_rows": int(len(videos_raw)),
        "videos_after_cleaning": int(len(prepared.videos)),
        "channels_after_aggregation": int(prepared.channels["_channel_id"].astype(str).nunique()),
        "comments_rows": int(len(prepared.comments)),
        "videos_source": str(VIDEOS_CSV),
        "comments_source": str(COMMENTS_CSV),
        "master_source": str(MASTER_CSV),
    }
    return {
        "brand_brief": brief,
        "prepared": prepared,
        "master_raw": master_raw,
        "summary": summary,
    }


def run_network_step(
    prepared_bundle: dict[str, Any],
    min_shared_tags: int = 2,
    max_tag_channel_ratio: float = 0.20,
    min_community_size: int = 3,
) -> dict[str, Any]:
    """
    Build the channel graph and compute network/community features.
    """
    prepared = prepared_bundle["prepared"]
    graph = build_channel_graph(
        prepared.channels,
        min_shared_tags=min_shared_tags,
        max_tag_channel_ratio=max_tag_channel_ratio,
    )
    channels_with_network = compute_network_scores(
        prepared.channels,
        graph,
        min_community_size=min_community_size,
    )
    return {
        "graph": graph,
        "channels": channels_with_network,
        "meta": graph.get("meta", {}),
    }


def run_text_step(
    network_bundle: dict[str, Any],
    brand_params: dict[str, Any] | None = None,
    top_candidates_for_semantic: int = 30,
) -> dict[str, Any]:
    """
    Compute TF-IDF relevance, run semantic enrichment on top candidates,
    then create ranked output (without ML by default in this standalone step).
    """
    p = brand_params or default_brand_params()
    brief = build_brand_brief(p)
    channels = network_bundle["channels"].copy()

    text_scored = compute_text_scores(channels, brief)
    pre = text_scored.copy()
    pre["semantic_score"] = 0.0
    pre["tone_match_score"] = 0.0
    pre["red_flags"] = [[] for _ in range(len(pre))]
    pre["alignment_rationale"] = ""

    pre_ranked = create_ranking(pre, use_ml=False, top_n=max(10, top_candidates_for_semantic))
    top_candidates = pre_ranked.scored_channels.head(top_candidates_for_semantic)
    semantic_map = enrich_top_candidates(top_candidates, brief)

    merged = merge_semantic_scores(text_scored, semantic_map)
    ranked = create_ranking(merged, use_ml=False, top_n=10)
    return {
        "brief": brief,
        "text_scored": text_scored,
        "scored_df": ranked.scored_channels,
        "top_df": ranked.top5,
    }


def run_ml_step(prepared_bundle: dict[str, Any], include_models: list[str] | None = None) -> dict[str, Any]:
    """
    Run the ML benchmark suite independently on prepared video data.
    """
    prepared = prepared_bundle["prepared"]
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    ml_artifacts = run_ml_suite(
        prepared.videos,
        out_dir=PLOTS_DIR,
        include_models=include_models,
    )
    return {
        "cv_results": ml_artifacts.cv_results,
        "best_model": ml_artifacts.best_model_name,
        "pred_actual": ml_artifacts.pred_actual,
        "shap_summary": ml_artifacts.shap_summary,
        "shap_dependence": ml_artifacts.shap_dependence,
        "notes": ml_artifacts.notes,
    }


def run_full_pipeline_step(
    brand_params: dict[str, Any] | None = None,
    run_ml: bool = True,
    run_benchmark: bool = True,
) -> dict[str, Any]:
    """
    Run the same full orchestrated flow used in the application.
    """
    p = brand_params or default_brand_params()
    result = run_pipeline(
        brand_params=p,
        run_ml=run_ml,
        run_benchmark=run_benchmark,
        config=replace(
            DEFAULT_CONFIG,
            top_recommendations=10,
            top_candidates_for_semantic=30,
        ),
    )
    return result


def render_core_figures(result: dict[str, Any]) -> dict[str, Any]:
    """
    Build Matplotlib figure objects for report screenshots in Colab.
    """
    figs: dict[str, Any] = {}

    cv_df = result.get("ml_cv_results", pd.DataFrame())
    if isinstance(cv_df, pd.DataFrame) and not cv_df.empty:
        figs["model_cv"] = model_cv_figure(cv_df)

    top_df = result.get("top5_df", pd.DataFrame())
    if isinstance(top_df, pd.DataFrame) and not top_df.empty:
        figs["score_breakdown"] = score_breakdown_figure(top_df)

    scored_df = result.get("scored_df", pd.DataFrame())
    if isinstance(scored_df, pd.DataFrame) and not scored_df.empty:
        figs["community"] = community_figure(scored_df, top_k=15, include_micro=False)

    graph = result.get("graph", {})
    if graph and isinstance(scored_df, pd.DataFrame) and not scored_df.empty:
        figs["network"] = network_figure(graph, scored_df, top_nodes=120, min_edge_weight=2)

    roi = result.get("roi_result", {})
    if isinstance(roi, dict) and roi:
        figs["roi_funnel"] = roi_funnel_figure(roi)

    return figs


def save_top_outputs(result: dict[str, Any], out_dir: str = "submission_outputs") -> dict[str, str]:
    """
    Save key tables for grading materials and report appendices.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    saved: dict[str, str] = {}
    for key, fname in [
        ("top5_df", "top_recommendations.csv"),
        ("scored_df", "all_scored_channels.csv"),
        ("ml_cv_results", "ml_cv_results.csv"),
    ]:
        df = result.get(key, pd.DataFrame())
        if isinstance(df, pd.DataFrame) and not df.empty:
            p = out_path / fname
            df.to_csv(p, index=False)
            saved[key] = str(p)

    memo = result.get("executive_memo_md", "")
    if memo:
        memo_path = out_path / "executive_memo.md"
        memo_path.write_text(str(memo), encoding="utf-8")
        saved["executive_memo_md"] = str(memo_path)

    return saved
