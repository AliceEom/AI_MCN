from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd

from .channel_media import build_channel_media
from .config import CACHE_DIR, COMMENTS_CSV, DEFAULT_CONFIG, MASTER_CSV, PLOTS_DIR, REPORTS_DIR, VIDEOS_CSV, PipelineConfig
from .content_generation import generate_executive_memo, generate_strategies
from .data_prep import load_data, prepare_all
from .ml_modeling import MLArtifacts, run_ml_suite
from .network_scoring import build_channel_graph, compute_network_scores
from .ranking import RankingOutput, create_ranking, merge_semantic_scores
from .roi_simulation import simulate_roi
from .semantic_enrichment import enrich_top_candidates
from .text_scoring import BrandBrief, build_brand_brief, compute_text_scores
from .utils import ensure_dir, utc_now_iso


def _compute_bias_report(scored_df: pd.DataFrame, final_top5: pd.DataFrame) -> dict[str, Any]:
    top_n = max(1, len(final_top5))
    degree_top = scored_df.sort_values("degree_centrality", ascending=False).head(top_n)
    title_col = "channel_title" if "channel_title" in degree_top.columns else "_channel_id"
    final_set = set(final_top5["_channel_id"].astype(str).tolist())
    degree_set = set(degree_top["_channel_id"].astype(str).tolist())

    overlap = len(final_set & degree_set)
    return {
        "degree_top_overlap": overlap,
        "degree_top_channels": degree_top[[title_col, "degree_centrality"]].to_dict(orient="records"),
        "top_n": top_n,
        "n_unique_final": len(final_set),
        "n_unique_communities_topn": int(final_top5["community_id"].nunique()),
        "narrative": (
            f"Overlap between degree-only top-{top_n} and hybrid top-{top_n} is {overlap}/{top_n}. "
            "Lower overlap indicates reduced popularity bias."
        ),
    }


def _rank_for_brief(base_channels: pd.DataFrame, brief: BrandBrief, config: PipelineConfig, use_ml: bool) -> RankingOutput:
    text_scored = compute_text_scores(base_channels, brief)

    # Pre-select candidates before semantic enrichment.
    pre = text_scored.copy()
    pre["semantic_score"] = 0.0
    pre["tone_match_score"] = 0.0
    pre["red_flags"] = [[] for _ in range(len(pre))]
    pre["alignment_rationale"] = ""

    pre_ranked = create_ranking(pre, use_ml=use_ml, top_n=config.top_recommendations)
    top_candidates = pre_ranked.scored_channels.head(config.top_candidates_for_semantic)

    semantic_map = enrich_top_candidates(top_candidates, brief)
    with_semantic = merge_semantic_scores(text_scored, semantic_map)

    final_ranked = create_ranking(with_semantic, use_ml=use_ml, top_n=config.top_recommendations)
    return final_ranked


def _ml_enabled_from_results(ml: MLArtifacts) -> bool:
    cv = ml.cv_results.copy()
    valid = cv[cv["status"] == "ok"]
    base = cv[cv["model"] == "BaselineMedian"]
    if valid.empty or base.empty:
        return False

    best_rmse = float(valid["rmse_mean"].min())
    base_rmse = float(base.iloc[0]["rmse_mean"])
    if base_rmse <= 0:
        return False

    gain = (base_rmse - best_rmse) / base_rmse
    return gain >= 0.02


def run_pipeline(
    brand_params: dict[str, Any] | None = None,
    mode: str = "anchor",
    run_ml: bool = True,
    run_benchmark: bool = True,
    ml_models: list[str] | None = None,
    config: PipelineConfig = DEFAULT_CONFIG,
) -> dict[str, Any]:
    ensure_dir(CACHE_DIR)
    ensure_dir(PLOTS_DIR)
    ensure_dir(REPORTS_DIR)

    videos_raw, comments_raw, _ = load_data(VIDEOS_CSV, COMMENTS_CSV, MASTER_CSV)

    brief = build_brand_brief(brand_params)
    prepared = prepare_all(
        videos_raw,
        comments_raw,
        must_keywords=brief.must_keywords,
        exclude_keywords=brief.exclude_keywords,
    )

    graph = build_channel_graph(
        prepared.channels,
        min_shared_tags=config.min_shared_tags_edge,
        max_tag_channel_ratio=config.max_tag_channel_ratio,
    )
    channels = compute_network_scores(
        prepared.channels,
        graph,
        min_community_size=config.min_community_size,
        random_state=config.random_state,
    )
    if "channel_title" not in channels.columns:
        channels["channel_title"] = channels["_channel_id"].astype(str)

    ml_artifacts: MLArtifacts | None = None
    if run_ml:
        ml_artifacts = run_ml_suite(
            prepared.videos,
            out_dir=PLOTS_DIR,
            random_state=config.random_state,
            tfidf_max_features=config.tfidf_max_features,
            svd_components=config.svd_components,
            max_rows=config.ml_max_rows,
            include_models=ml_models,
        )
        channels = channels.merge(
            ml_artifacts.channel_potential[["_channel_id", "ml_potential_score"]],
            on="_channel_id",
            how="left",
        )
    if "ml_potential_score" not in channels.columns:
        channels["ml_potential_score"] = 0.0
    else:
        channels["ml_potential_score"] = channels["ml_potential_score"].fillna(0.0)

    use_ml = _ml_enabled_from_results(ml_artifacts) if ml_artifacts else False

    ranked = _rank_for_brief(channels, brief, config=config, use_ml=use_ml)
    scored_df = ranked.scored_channels
    top5 = ranked.top5.copy()

    media_candidates = scored_df.head(max(30, config.top_recommendations)).copy()
    media_map = build_channel_media(media_candidates, CACHE_DIR)
    for target_df in (scored_df, top5):
        target_df["image_url"] = target_df["_channel_id"].astype(str).map(lambda cid: media_map.get(cid, {}).get("image_url", ""))
        target_df["channel_url"] = target_df["_channel_id"].astype(str).map(lambda cid: media_map.get(cid, {}).get("channel_url", ""))
        target_df["video_url"] = target_df["_channel_id"].astype(str).map(lambda cid: media_map.get(cid, {}).get("video_url", ""))

    roi = simulate_roi(budget_usd=brief.budget_usd).to_dict()
    strategies = generate_strategies(top5, brief, CACHE_DIR)
    memo = generate_executive_memo(top5, roi, brief, strategies)

    bias_report = _compute_bias_report(scored_df, top5)

    benchmark_summary = {}
    if run_benchmark and mode == "anchor":
        bench_params = {
            "brand_name": "CeraVe",
            "product_name": "Hydrating Cleanser + SPF Routine",
            "category": "Skincare",
            "target_audience": "US consumers seeking dermatologist-trusted daily skincare",
            "campaign_goal": "Awareness + conversion",
            "budget_usd": brief.budget_usd,
            "usp": "Accessible dermatologist-backed skincare for daily use.",
            "must_keywords": ["cerave", "cleanser", "moisturizer", "spf"],
            "exclude_keywords": brief.exclude_keywords,
            "market": brief.market,
        }
        bench_brief = build_brand_brief(bench_params)
        bench_ranked = _rank_for_brief(channels, bench_brief, config=config, use_ml=use_ml)
        bench_top1 = bench_ranked.top5.head(1)
        benchmark_summary = {
            "brand": "CeraVe",
            "top_channel": bench_top1.iloc[0]["channel_title"] if not bench_top1.empty else "N/A",
            "top_score": float(bench_top1.iloc[0]["final_score"]) if not bench_top1.empty else 0.0,
            "topn_mean_score": float(bench_ranked.top5["final_score"].mean()) if not bench_ranked.top5.empty else 0.0,
            "top5_mean_score": float(bench_ranked.top5.head(5)["final_score"].mean()) if not bench_ranked.top5.empty else 0.0,
        }

    # Persist key artifacts.
    topk_label = f"top{config.top_recommendations}"
    top5_path = REPORTS_DIR / f"{topk_label}_{brief.brand_name.replace(' ', '_').lower()}.csv"
    scored_path = REPORTS_DIR / f"scored_channels_{brief.brand_name.replace(' ', '_').lower()}.csv"
    memo_path = REPORTS_DIR / f"memo_{brief.brand_name.replace(' ', '_').lower()}.md"
    top5.to_csv(top5_path, index=False)
    scored_df.to_csv(scored_path, index=False)
    memo_path.write_text(memo, encoding="utf-8")

    cv_df = ml_artifacts.cv_results if ml_artifacts else pd.DataFrame()
    if not cv_df.empty:
        cv_path = REPORTS_DIR / "ml_cv_results.csv"
        cv_df.to_csv(cv_path, index=False)

    return {
        "timestamp_utc": utc_now_iso(),
        "brand_brief": asdict(brief),
        "videos_df": prepared.videos,
        "channels_df": channels,
        "scored_df": scored_df,
        "top5_df": top5,
        "graph": graph,
        "roi_result": roi,
        "strategy_texts": strategies,
        "executive_memo_md": memo,
        "bias_report": bias_report,
        "benchmark_summary": benchmark_summary,
        "ml_cv_results": cv_df,
        "ml_best_model": ml_artifacts.best_model_name if ml_artifacts else "N/A",
        "ml_notes": ml_artifacts.notes if ml_artifacts else [],
        "ml_plot_path": ml_artifacts.model_plot_path if ml_artifacts else None,
        "ml_pred_plot_path": ml_artifacts.pred_plot_path if ml_artifacts else None,
        "shap_plot_paths": ml_artifacts.shap_plot_paths if ml_artifacts else [],
        "artifact_paths": {
            "top5_csv": str(top5_path),
            "top_csv": str(top5_path),
            "topn_csv": str(top5_path),
            "scored_csv": str(scored_path),
            "memo_md": str(memo_path),
        },
    }
