from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import time

import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

from src.config import DEFAULT_CONFIG
from src.orchestrator import run_pipeline
from src.ranking import select_top_with_diversity
from src.roi_simulation import simulate_roi
from src.visualization import (
    community_figure,
    model_cv_figure,
    network_figure,
    roi_funnel_figure,
    score_breakdown_figure,
)


st.set_page_config(page_title="AI-MCN Demo", layout="wide")

MODEL_OPTIONS = ["LinearRegression", "LASSO", "Ridge", "CART", "RandomForest", "LightGBM"]


def _inject_css() -> None:
    st.markdown(
        """
<style>
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
.hero-wrap {
  border-radius: 20px;
  padding: 34px 30px;
  background: linear-gradient(140deg, #13395f 0%, #1576a3 48%, #3ab4cf 100%);
  color: #ffffff;
  border: 1px solid rgba(255,255,255,0.16);
}
.hero-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 8px; line-height: 1.1; }
.hero-sub { font-size: 1.02rem; opacity: 0.95; max-width: 860px; }
.pill {
  display: inline-block;
  margin-right: 8px;
  margin-top: 8px;
  padding: 6px 11px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: #0b4f69;
  background: #e6f8ff;
}
.panel {
  border: 1px solid #dfe7ef;
  border-radius: 14px;
  padding: 14px 16px;
  background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
}
.card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  background: #ffffff;
}
.tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  border-radius: 999px;
  padding: 3px 10px;
  margin-right: 6px;
  margin-bottom: 6px;
  border: 1px solid #dce4f5;
  background: #f4f7ff;
}
.topbar {
  border-radius: 14px;
  padding: 14px 18px;
  background: linear-gradient(130deg, #f8fafc 0%, #eef5ff 100%);
  border: 1px solid #dbe8ff;
}
.muted { color: #546173; font-size: 0.92rem; }
</style>
""",
        unsafe_allow_html=True,
    )


def _init_state() -> None:
    st.session_state.setdefault("screen", "landing")
    st.session_state.setdefault("run_request", None)
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("last_error", "")


def _split_csv_keywords(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def _num(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _fit_bucket(score: float) -> tuple[str, str]:
    if score >= 0.65:
        return "Very Strong Match", "#1B8F5A"
    if score >= 0.45:
        return "Strong Match", "#2E6FDC"
    if score >= 0.30:
        return "Moderate Match", "#9B6E00"
    return "Exploratory", "#9A3E3E"


def _evidence_bucket(score: float) -> tuple[str, str]:
    if score >= 0.60:
        return "High Evidence", "#1B8F5A"
    if score >= 0.35:
        return "Medium Evidence", "#2E6FDC"
    return "Low Evidence", "#9A3E3E"


def _fmt_date(value: object) -> str:
    text = str(value) if value is not None else ""
    if not text or text.lower() == "nan":
        return "N/A"
    dt = pd.to_datetime(text, errors="coerce")
    if pd.isna(dt):
        return "N/A"
    return dt.strftime("%Y-%m-%d")


def _plain_language_reason(row: pd.Series) -> str:
    parts = []
    if _num(row.get("tfidf_similarity")) >= 0.55:
        parts.append("the channel language closely matches your brand keywords")
    if _num(row.get("sna_score")) >= 0.55:
        parts.append("the creator sits near the center of the relevant creator network")
    if _num(row.get("engagement_score")) >= 0.45:
        parts.append("audience interaction quality is healthy")
    if _num(row.get("semantic_score")) >= 0.45:
        parts.append("brand tone and content style are aligned")
    if not parts:
        parts.append("it can be a test candidate, but with weaker evidence signals")
    return "Why this creator: " + ", and ".join(parts) + "."


def _ranking_weights(strategy: str, include_ml: bool) -> dict[str, float]:
    presets = {
        "Model Default": {"sna": 0.34, "tfidf": 0.24, "semantic": 0.18, "tone": 0.10, "eng": 0.14, "ml": 0.00},
        "Network-first": {"sna": 0.46, "tfidf": 0.16, "semantic": 0.14, "tone": 0.08, "eng": 0.14, "ml": 0.02},
        "Keyword-first": {"sna": 0.20, "tfidf": 0.42, "semantic": 0.18, "tone": 0.08, "eng": 0.10, "ml": 0.02},
        "Performance-first": {"sna": 0.20, "tfidf": 0.12, "semantic": 0.16, "tone": 0.08, "eng": 0.38, "ml": 0.06},
    }
    w = presets.get(strategy, presets["Model Default"]).copy()
    if not include_ml:
        w["ml"] = 0.0
    total = sum(w.values()) or 1.0
    return {k: v / total for k, v in w.items()}


def _apply_ranking_strategy(df: pd.DataFrame, strategy: str, include_ml: bool) -> pd.Series:
    if strategy == "Model Default":
        return df["final_score"].fillna(0.0)

    w = _ranking_weights(strategy, include_ml=include_ml)
    score_base = (
        w["sna"] * df["sna_score"].fillna(0.0)
        + w["tfidf"] * df["tfidf_similarity"].fillna(0.0)
        + w["semantic"] * df["semantic_score"].fillna(0.0)
        + w["tone"] * df["tone_match_score"].fillna(0.0)
        + w["eng"] * df["engagement_score"].fillna(0.0)
        + w["ml"] * df["ml_potential_score"].fillna(0.0)
    )
    credibility = df.get("credibility_multiplier", pd.Series(1.0, index=df.index)).fillna(1.0)
    return score_base * credibility


def _top_terms(channel_df: pd.DataFrame, top_n: int = 25, min_df: int = 4) -> pd.DataFrame:
    text = channel_df.get("channel_text", pd.Series([], dtype=object)).fillna("").astype(str)
    text = text[text.str.strip() != ""]
    if text.empty:
        return pd.DataFrame(columns=["term", "count"])

    min_df = max(1, int(min_df))
    try:
        vec = CountVectorizer(stop_words="english", min_df=min_df, max_features=4000, ngram_range=(1, 2))
        x = vec.fit_transform(text.tolist())
    except Exception:
        return pd.DataFrame(columns=["term", "count"])

    counts = np.asarray(x.sum(axis=0)).ravel()
    terms = np.asarray(vec.get_feature_names_out())
    order = np.argsort(counts)[::-1][: max(5, int(top_n))]
    out = pd.DataFrame({"term": terms[order], "count": counts[order].astype(int)})
    return out.reset_index(drop=True)


def _keyword_coverage(channel_df: pd.DataFrame, keywords: list[str], top_k: int = 15) -> pd.DataFrame:
    if not keywords:
        return pd.DataFrame()
    d = channel_df.head(max(3, int(top_k))).copy()
    d["channel_title"] = d["channel_title"].fillna(d["_channel_id"].astype(str))
    rows = []
    for _, r in d.iterrows():
        t = str(r.get("channel_text", "")).lower()
        row = {"channel_title": r["channel_title"]}
        for kw in keywords:
            k = kw.lower().strip()
            row[k] = 1 if k and k in t else 0
        rows.append(row)
    cov = pd.DataFrame(rows)
    if cov.empty:
        return cov
    return cov.set_index("channel_title")


def _scatter_text_alignment(scored_df: pd.DataFrame) -> plt.Figure:
    d = scored_df.copy()
    if "median_views" not in d.columns:
        d["median_views"] = 0.0
    size = 20 + 90 * (np.log1p(d["median_views"].fillna(0)) / max(np.log1p(d["median_views"].fillna(0)).max(), 1e-6))

    fig, ax = plt.subplots(figsize=(8.8, 5.6))
    sc = ax.scatter(
        d["tfidf_similarity"].fillna(0),
        d["semantic_score"].fillna(0),
        c=d.get("evidence_score", pd.Series(np.zeros(len(d)))).fillna(0),
        s=size,
        cmap="viridis",
        alpha=0.75,
    )
    ax.set_xlabel("TF-IDF Similarity")
    ax.set_ylabel("Semantic Alignment")
    ax.set_title("Text Match Map (Size: Median Views, Color: Data Reliability)")
    fig.colorbar(sc, ax=ax, fraction=0.03, pad=0.02, label="Evidence")
    fig.tight_layout()
    return fig


def _render_landing() -> None:
    st.markdown(
        """
<div class="hero-wrap">
  <div class="hero-title">Find Your Best Influencer Matches</div>
  <div class="hero-sub">
    AI-MCN combines network science, text intelligence, and predictive modeling to recommend creators your client can trust.
    Enter a campaign brief and generate shortlist, benchmark, ROI scenario, strategy, and memo in one flow.
  </div>
  <div>
    <span class="pill">SNA Centrality</span>
    <span class="pill">Text + Semantic Matching</span>
    <span class="pill">ML Benchmark + SHAP</span>
    <span class="pill">ROI Simulator</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.write("")

    with st.form("campaign_form", clear_on_submit=False):
        st.markdown("### Campaign Brief")
        c1, c2 = st.columns(2)
        brand_name = c1.text_input("Brand Name", value="Beauty of Joseon")
        product_name = c2.text_input("Product Name", value="Relief Sun SPF + Glow Serum")

        c3, c4 = st.columns(2)
        category = c3.selectbox("Product Category", ["Skincare", "Makeup", "Haircare", "Bodycare", "Fragrance"], index=0)
        campaign_goal = c4.selectbox("Campaign Goal", ["Awareness + trial conversion", "Awareness", "Conversion"], index=0)

        target_audience = st.text_area(
            "Target Audience",
            value="US Gen Z and Millennial users with sensitive or acne-prone skin, looking for daily lightweight skincare.",
            height=90,
        )
        usp = st.text_area(
            "Core Message / USP",
            value="Gentle K-beauty skincare with strong UV care and lightweight texture for daily use.",
            height=80,
        )

        c5, c6, c7 = st.columns(3)
        budget = c5.number_input("Budget (USD)", min_value=1000, max_value=500000, value=50000, step=5000)
        market = c6.text_input("Market", value="United States")
        top_reco_n = c7.slider("Top-N Default", min_value=5, max_value=20, value=10, step=1)

        must_keywords = st.text_input("Must-Have Keywords (comma-separated)", value="sunscreen, spf, sensitive skin, k-beauty")
        exclude_keywords = st.text_input("Excluded Keywords (comma-separated)", value="music, gaming, movie, trailer")

        st.markdown("### Advanced Controls")
        a1, a2, a3 = st.columns(3)
        min_shared_tags = a1.slider("Min Shared Tags per Edge", min_value=1, max_value=5, value=2, step=1)
        max_tag_ratio = a2.slider("Max Tag Coverage Ratio", min_value=0.05, max_value=0.45, value=0.20, step=0.01)
        min_community_size = a3.slider("Min Community Size", min_value=1, max_value=10, value=3, step=1)

        m1, m2 = st.columns(2)
        enable_ml = m1.checkbox("Enable ML Benchmark Block", value=True)
        run_benchmark = m2.checkbox("Run CeraVe Benchmark", value=True)

        if enable_ml:
            ml_models = st.multiselect(
                "ML Models to Train",
                MODEL_OPTIONS,
                default=["LinearRegression", "LASSO", "Ridge", "CART", "RandomForest", "LightGBM"],
                help="Choose which models to train in 5-fold CV.",
            )
        else:
            ml_models = []

        run_submit = st.form_submit_button("Find Influencers", type="primary")

    if run_submit:
        request = {
            "params": {
                "brand_name": brand_name,
                "product_name": product_name,
                "category": category,
                "target_audience": target_audience,
                "campaign_goal": campaign_goal,
                "budget_usd": float(budget),
                "usp": usp,
                "must_keywords": _split_csv_keywords(must_keywords),
                "exclude_keywords": _split_csv_keywords(exclude_keywords),
                "market": market,
            },
            "top_reco_n": int(top_reco_n),
            "enable_ml": bool(enable_ml),
            "ml_models": list(ml_models),
            "run_benchmark": bool(run_benchmark),
            "config_patch": {
                "top_recommendations": int(top_reco_n),
                "top_candidates_for_semantic": max(30, int(top_reco_n) * 3),
                "min_shared_tags_edge": int(min_shared_tags),
                "max_tag_channel_ratio": float(max_tag_ratio),
                "min_community_size": int(min_community_size),
            },
        }
        st.session_state.run_request = request
        st.session_state.last_error = ""
        st.session_state.screen = "analyzing"
        st.rerun()

    if st.session_state.last_error:
        st.error(f"Previous run failed: {st.session_state.last_error}")


def _render_analyzing() -> None:
    req = st.session_state.get("run_request")
    if not req:
        st.session_state.screen = "landing"
        st.rerun()

    st.markdown("## Analyzing Influencer Network")
    st.caption("Running data prep, network scoring, text matching, ML benchmark, and recommendation synthesis.")

    steps = [
        "Loading and cleaning source data",
        "Building channel graph and centrality scores",
        "Running text + semantic relevance scoring",
        "Training ML benchmark models (if enabled)",
        "Generating ranking, ROI, strategy, and memo artifacts",
    ]
    progress = st.progress(0)
    status = st.empty()

    for i, step in enumerate(steps[:-1], start=1):
        status.markdown(f"**Step {i}/{len(steps)}**: {step}")
        progress.progress(int((i / len(steps)) * 80))
        time.sleep(0.25)

    runtime_config = replace(DEFAULT_CONFIG, **req["config_patch"])
    try:
        status.markdown(f"**Step {len(steps)}/{len(steps)}**: {steps[-1]}")
        result = run_pipeline(
            brand_params=req["params"],
            mode="anchor",
            run_ml=req["enable_ml"],
            run_benchmark=req["run_benchmark"],
            ml_models=req["ml_models"] if req["enable_ml"] else None,
            config=runtime_config,
        )
        progress.progress(100)
        st.success("Analysis complete. Opening dashboard...")
        st.session_state.result = result
        st.session_state.screen = "dashboard"
        time.sleep(0.5)
        st.rerun()
    except Exception as e:
        st.session_state.last_error = str(e)
        st.session_state.screen = "landing"
        st.error(f"Pipeline failed: {e}")


def _render_overview(result: dict, req: dict) -> None:
    topn = result["top5_df"].copy()
    scored = result["scored_df"].copy()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Videos Analyzed", f"{len(result['videos_df']):,}")
    c2.metric("Channels Scored", f"{scored['_channel_id'].nunique():,}")
    c3.metric("Best ML Model", result["ml_best_model"])
    c4.metric(f"Top-{len(topn)} Community Count", int(topn["community_id"].nunique()))

    avg_evidence = float(topn.get("evidence_score", pd.Series(np.zeros(len(topn)))).fillna(0).mean()) if not topn.empty else 0.0
    label, color = _evidence_bucket(avg_evidence)
    st.markdown(
        f"<div class='panel'><b>Data Reliability of Current Shortlist:</b> "
        f"<span style='color:{color}; font-weight:800'>{label}</span> (avg {avg_evidence:.2f}). "
        "Low-evidence channels are automatically down-weighted.</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("### Campaign Input Snapshot")
    st.json(req["params"])
    st.markdown("### Benchmark Panel (Anchor vs CeraVe)")
    st.json(result.get("benchmark_summary", {}))


def _render_top_matches(result: dict, req: dict) -> None:
    scored = result["scored_df"].copy()
    topn = result["top5_df"].copy()
    if scored.empty:
        st.warning("No scored channels available for this run.")
        return

    if "evidence_score" not in scored.columns:
        scored["evidence_score"] = 0.0
    if "final_score_base" not in scored.columns:
        scored["final_score_base"] = scored["final_score"]
    if "credibility_multiplier" not in scored.columns:
        scored["credibility_multiplier"] = 1.0

    f1, f2, f3, f4, f5 = st.columns(5)
    min_match = f1.slider("Min Match Score", min_value=0.0, max_value=1.0, value=0.20, step=0.01)
    min_evidence = f2.slider("Min Evidence", min_value=0.0, max_value=1.0, value=0.20, step=0.01)
    ranking_strategy = f3.selectbox(
        "Ranking Strategy",
        ["Model Default", "Network-first", "Keyword-first", "Performance-first"],
        index=0,
    )
    min_n = 3 if len(scored) < 5 else 5
    max_n = min(30, max(min_n, len(scored)))
    default_n = min(max(min_n, req["top_reco_n"]), max_n)
    display_n = f4.slider("Display Top-N", min_value=min_n, max_value=max_n, value=default_n, step=1)
    diversity_preview = f5.checkbox("Diversity Preview", value=True)

    scored["display_score"] = _apply_ranking_strategy(scored, ranking_strategy, include_ml=req["enable_ml"])
    ranked = scored[(scored["display_score"] >= min_match) & (scored["evidence_score"] >= min_evidence)].copy()
    ranked = ranked.sort_values("display_score", ascending=False).reset_index(drop=True)

    if diversity_preview and not ranked.empty:
        d1, d2 = st.columns([2, 1])
        min_comms = d1.slider("Min Communities in Displayed List", min_value=2, max_value=8, value=3, step=1)
        apply_diversity = d2.checkbox("Apply guardrail now", value=True)
        if apply_diversity:
            tmp = ranked.copy()
            tmp["final_score"] = tmp["display_score"]
            ranked = select_top_with_diversity(tmp, top_n=display_n, min_communities=min_comms)
        else:
            ranked = ranked.head(display_n)
    else:
        ranked = ranked.head(display_n)

    if ranked.empty:
        st.warning("No channels match current filter thresholds.")
        return

    st.pyplot(score_breakdown_figure(ranked))
    st.download_button(
        "Download Current Top-N as CSV",
        data=ranked.to_csv(index=False),
        file_name="top_recommendations_interactive.csv",
        mime="text/csv",
    )

    for rank_idx, (_, row) in enumerate(ranked.iterrows(), start=1):
        fit_label, fit_color = _fit_bucket(_num(row.get("display_score")))
        ev_label, ev_color = _evidence_bucket(_num(row.get("evidence_score")))
        with st.container(border=True):
            cols = st.columns([1, 3])
            image_url = row.get("image_url", "")
            if image_url:
                cols[0].image(image_url, use_container_width=True)

            cols[1].markdown(f"### #{rank_idx} {row.get('channel_title', 'Unknown Channel')}")
            cols[1].markdown(
                f"<span class='tag' style='border-color:{fit_color}; color:{fit_color}'>{fit_label}</span>"
                f"<span class='tag' style='border-color:{ev_color}; color:{ev_color}'>{ev_label}</span>",
                unsafe_allow_html=True,
            )
            cols[1].markdown(f"**Final Match Score:** {_num(row.get('display_score')):.3f}")
            cols[1].write(_plain_language_reason(row))

            m1, m2, m3, m4 = cols[1].columns(4)
            m1.metric("Videos Used", f"{int(_num(row.get('n_videos'))):,}")
            m2.metric("Median Views", f"{int(_num(row.get('median_views'))):,}")
            m3.metric("Median Likes", f"{int(_num(row.get('median_likes'))):,}")
            m4.metric("Community", f"{int(_num(row.get('community_id')))}")

            with cols[1].expander("Detailed Signals"):
                st.markdown(
                    f"SNA {_num(row.get('sna_score')):.3f} | TF-IDF {_num(row.get('tfidf_similarity')):.3f} | "
                    f"Semantic {_num(row.get('semantic_score')):.3f} | Tone {_num(row.get('tone_match_score')):.3f} | "
                    f"Engagement {_num(row.get('engagement_score')):.3f} | ML {_num(row.get('ml_potential_score')):.3f}"
                )
                st.markdown(
                    f"Base Score: {_num(row.get('final_score_base')):.3f} | "
                    f"Reliability Multiplier: {_num(row.get('credibility_multiplier')):.3f}"
                )
                st.markdown(
                    f"Latest Publish Date: {_fmt_date(row.get('latest_publish'))} | "
                    f"Days Since Latest: {int(_num(row.get('days_since_latest')))}"
                )
                st.markdown(f"Rationale: {row.get('alignment_rationale', '')}")
                flags = row.get("red_flags", [])
                if isinstance(flags, list) and flags:
                    for f in flags:
                        st.warning(f)

            links = []
            if row.get("channel_url"):
                links.append(f"[Open Channel]({row['channel_url']})")
            if row.get("video_url"):
                links.append(f"[Representative Video]({row['video_url']})")
            if links:
                cols[1].markdown(" | ".join(links))

    st.markdown("### Detailed Channel Table")
    detail_cols = [
        "channel_title",
        "display_score",
        "final_score",
        "evidence_score",
        "n_videos",
        "median_views",
        "median_likes",
        "median_comments",
        "mean_engagement",
        "days_since_latest",
        "community_id",
        "channel_url",
        "video_url",
    ]
    detail_cols = [c for c in detail_cols if c in ranked.columns]
    st.dataframe(ranked[detail_cols], use_container_width=True)

    low_ev = scored[scored.get("credibility_multiplier", 1.0) < 0.40].copy()
    if not low_ev.empty:
        st.markdown("### Channels Down-weighted for Weak Evidence")
        st.caption("These channels matched keywords/network but had low observed performance evidence.")
        st.dataframe(
            low_ev.sort_values("final_score_base", ascending=False).head(12)[
                [
                    "channel_title",
                    "n_videos",
                    "median_views",
                    "median_likes",
                    "median_comments",
                    "final_score_base",
                    "credibility_multiplier",
                    "final_score",
                ]
            ],
            use_container_width=True,
        )


def _render_network_studio(result: dict) -> None:
    scored = result["scored_df"].copy()
    graph = result["graph"]

    n1, n2, n3, n4 = st.columns(4)
    top_nodes = n1.slider("Nodes in View", min_value=40, max_value=300, value=140, step=10)
    min_edge_weight = n2.slider("Min Edge Strength", min_value=1, max_value=8, value=2, step=1)
    top_comms = n3.slider("Communities to Show", min_value=5, max_value=30, value=12, step=1)
    include_micro = n4.checkbox("Include micro/isolated", value=False)

    st.pyplot(network_figure(graph, scored, top_nodes=top_nodes, min_edge_weight=min_edge_weight))
    st.pyplot(community_figure(scored, top_k=top_comms, include_micro=include_micro))

    comm_df = scored.copy()
    if not include_micro:
        comm_df = comm_df[comm_df["community_id"] >= 0]
    counts = comm_df["community_id"].value_counts().rename_axis("community_id").reset_index(name="channels")

    c1, c2 = st.columns([2, 1])
    c1.markdown("### Community Diagnostics")
    if not counts.empty:
        largest_share = float(counts["channels"].max() / max(comm_df.shape[0], 1))
        c1.caption(f"Communities shown: {counts.shape[0]}, Largest share: {largest_share:.1%}")
    c1.dataframe(counts.head(40), use_container_width=True)

    c2.markdown("### Graph Meta")
    c2.json(graph.get("meta", {}))
    st.markdown("### Bias Report")
    st.json(result["bias_report"])


def _render_text_intelligence(result: dict, req: dict) -> None:
    scored = result["scored_df"].copy().sort_values("final_score", ascending=False).reset_index(drop=True)
    if scored.empty:
        st.warning("No scored channels available for text analysis.")
        return
    st.markdown("### Text Match Explorer")
    t1, t2, t3 = st.columns(3)
    min_analysis_n = min(10, len(scored))
    max_analysis_n = max(min_analysis_n, min(300, len(scored)))
    default_analysis_n = min(max(30, min_analysis_n), max_analysis_n)
    analysis_top_n = t1.slider("Channels for Text Analysis", min_value=min_analysis_n, max_value=max_analysis_n, value=default_analysis_n, step=max(1, min(10, max_analysis_n // 15)))
    top_term_n = t2.slider("Top Terms to Show", min_value=10, max_value=50, value=25, step=5)
    min_df_terms = t3.slider("Min Document Frequency", min_value=1, max_value=12, value=4, step=1)

    subset = scored.head(analysis_top_n).copy()
    st.pyplot(_scatter_text_alignment(subset))

    terms = _top_terms(subset, top_n=top_term_n, min_df=min_df_terms)
    if not terms.empty:
        fig, ax = plt.subplots(figsize=(9.4, 5.6))
        show = terms.head(20).iloc[::-1]
        ax.barh(show["term"], show["count"], color="#4BA3C7")
        ax.set_xlabel("Frequency")
        ax.set_title("Top Frequent Terms in Candidate Channel Text")
        fig.tight_layout()
        st.pyplot(fig)

    st.markdown("### Keyword Coverage Matrix")
    kw_text = st.text_input(
        "Keywords to track (comma-separated)",
        value=", ".join(req["params"].get("must_keywords", [])),
    )
    kws = _split_csv_keywords(kw_text)
    cov = _keyword_coverage(subset, kws, top_k=min(20, len(subset)))
    if not cov.empty:
        st.dataframe(cov, use_container_width=True)
        coverage_rate = cov.mean(axis=0).sort_values(ascending=False)
        fig2, ax2 = plt.subplots(figsize=(8.8, 4.6))
        ax2.bar(coverage_rate.index.tolist(), coverage_rate.values.tolist(), color="#6BCB77")
        ax2.set_ylim(0, 1)
        ax2.set_ylabel("Coverage Rate")
        ax2.set_title("Keyword Coverage Across Top Candidate Channels")
        ax2.tick_params(axis="x", rotation=25)
        fig2.tight_layout()
        st.pyplot(fig2)
    else:
        st.caption("No keyword matrix available for current settings.")

    st.markdown("### TF-IDF / Semantic Leaderboard")
    st.dataframe(
        subset[
            [
                "channel_title",
                "tfidf_similarity",
                "semantic_score",
                "tone_match_score",
                "final_score",
            ]
        ].head(30),
        use_container_width=True,
    )


def _render_ml_studio(result: dict, req: dict) -> None:
    cv_df = result["ml_cv_results"].copy()

    st.markdown(
        "For client communication: this block validates whether advanced models materially improve prediction over a simple baseline."
    )
    st.caption("Interactive mode: choose a model set and re-run the pipeline from this tab.")

    chosen_models = st.multiselect(
        "Models for next ML run",
        MODEL_OPTIONS,
        default=req.get("ml_models") or MODEL_OPTIONS,
    )
    c1, c2 = st.columns(2)
    rerun_clicked = c1.button("Re-run Pipeline With Selected Models", type="primary")
    fast_disable_clicked = c2.button("Run Without ML (Fast)")

    if rerun_clicked:
        if not chosen_models:
            st.warning("Select at least one model before rerunning.")
        else:
            new_req = dict(req)
            new_req["enable_ml"] = True
            new_req["ml_models"] = chosen_models
            st.session_state.run_request = new_req
            st.session_state.screen = "analyzing"
            st.rerun()

    if fast_disable_clicked:
        new_req = dict(req)
        new_req["enable_ml"] = False
        new_req["ml_models"] = []
        st.session_state.run_request = new_req
        st.session_state.screen = "analyzing"
        st.rerun()

    if cv_df.empty:
        st.info("ML benchmark was not run in this session. Re-run with ML enabled to populate this tab.")
        return

    st.pyplot(model_cv_figure(cv_df))
    st.dataframe(cv_df, use_container_width=True)

    model_choice = st.selectbox("Inspect Model", cv_df["model"].tolist(), index=0)
    row = cv_df[cv_df["model"] == model_choice].head(1)
    if not row.empty:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Status", str(row.iloc[0]["status"]))
        m2.metric("RMSE", f"{_num(row.iloc[0]['rmse_mean']):.4f}")
        m3.metric("MAE", f"{_num(row.iloc[0]['mae_mean']):.4f}")
        m4.metric("R2", f"{_num(row.iloc[0]['r2_mean']):.4f}")

    for note in result.get("ml_notes", []):
        st.info(note)

    if result.get("ml_plot_path") and Path(result["ml_plot_path"]).exists():
        st.image(result["ml_plot_path"], caption="CV RMSE Comparison", use_container_width=True)
    if result.get("ml_pred_plot_path") and Path(result["ml_pred_plot_path"]).exists():
        st.image(result["ml_pred_plot_path"], caption="Predicted vs Actual", use_container_width=True)

    shap_paths = result.get("shap_plot_paths", [])
    if shap_paths:
        st.markdown("### SHAP Explainability")
        for p in shap_paths:
            if Path(p).exists():
                st.image(p, caption=Path(p).name, use_container_width=True)
    else:
        st.caption("SHAP figures were not generated in this run.")


def _render_roi_lab(result: dict, req: dict) -> None:
    base_budget = float(req["params"].get("budget_usd", 50000.0))
    base_roi = result.get("roi_result", {})

    st.markdown("### ROI Scenario Playground")
    p1, p2, p3, p4, p5 = st.columns(5)
    budget = p1.number_input("Budget (USD)", min_value=1000.0, max_value=1000000.0, value=base_budget, step=1000.0)
    cpm = p2.number_input("CPM (USD)", min_value=5.0, max_value=80.0, value=float(base_roi.get("cpm", 18.0)), step=0.5)
    ctr_pct = p3.slider("CTR (%)", min_value=0.1, max_value=10.0, value=float(base_roi.get("ctr", 0.018) * 100), step=0.1)
    cvr_pct = p4.slider("CVR (%)", min_value=0.1, max_value=15.0, value=float(base_roi.get("cvr", 0.03) * 100), step=0.1)
    aov = p5.number_input("AOV (USD)", min_value=5.0, max_value=500.0, value=float(base_roi.get("aov", 38.0)), step=1.0)

    roi = simulate_roi(
        budget_usd=float(budget),
        cpm=float(cpm),
        ctr=float(ctr_pct) / 100.0,
        cvr=float(cvr_pct) / 100.0,
        aov=float(aov),
    ).to_dict()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Impressions", f"{roi.get('impressions', 0):,}")
    c2.metric("Clicks", f"{roi.get('clicks', 0):,}")
    c3.metric("Conversions", f"{roi.get('conversions', 0):,}")
    c4.metric("Expected ROAS", f"{roi.get('roas', 0):.2f}x")
    st.pyplot(roi_funnel_figure(roi))
    st.caption(f"ROAS range: {roi.get('roas_low', 0):.2f}x to {roi.get('roas_high', 0):.2f}x (scenario estimate).")

    st.markdown("### Budget Sensitivity")
    low_b = max(1000.0, budget * 0.5)
    high_b = budget * 1.8
    budget_grid = np.linspace(low_b, high_b, 9)
    roas_grid = []
    conv_grid = []
    for b in budget_grid:
        sim = simulate_roi(budget_usd=float(b), cpm=float(cpm), ctr=float(ctr_pct) / 100.0, cvr=float(cvr_pct) / 100.0, aov=float(aov))
        roas_grid.append(sim.roas)
        conv_grid.append(sim.conversions)

    fig, ax1 = plt.subplots(figsize=(9.2, 4.8))
    ax1.plot(budget_grid, roas_grid, marker="o", color="#0E7490", label="ROAS")
    ax1.set_xlabel("Budget (USD)")
    ax1.set_ylabel("ROAS", color="#0E7490")
    ax1.tick_params(axis="y", labelcolor="#0E7490")
    ax2 = ax1.twinx()
    ax2.plot(budget_grid, conv_grid, marker="s", color="#16A34A", label="Conversions")
    ax2.set_ylabel("Conversions", color="#16A34A")
    ax2.tick_params(axis="y", labelcolor="#16A34A")
    ax1.set_title("Budget Sensitivity: ROAS and Conversions")
    fig.tight_layout()
    st.pyplot(fig)


def _render_content_strategy(result: dict, req: dict) -> None:
    topn = result["top5_df"].copy()
    strategies = result["strategy_texts"]
    if topn.empty:
        st.warning("No recommendations available for strategy generation.")
        return
    min_cards = 1 if len(topn) < 3 else 3
    max_cards = max(min_cards, len(topn))
    default_cards = min(max(min_cards, req["top_reco_n"]), max_cards)
    count = st.slider("How many strategy cards", min_value=min_cards, max_value=max_cards, value=default_cards, step=1)
    for _, row in topn.head(count).iterrows():
        cid = str(row["_channel_id"])
        st.markdown(f"## {row.get('channel_title', 'Creator')}")
        st.markdown(strategies.get(cid, "No strategy generated."))
        st.markdown("---")


def _render_memo(result: dict) -> None:
    memo = result["executive_memo_md"]
    st.markdown(memo)
    st.download_button(
        "Download Memo (Markdown)",
        data=memo,
        file_name="brand_partnership_memo.md",
        mime="text/markdown",
    )


def _render_glossary() -> None:
    glossary = [
        ("Match Score", "Overall suitability of a channel for your campaign."),
        ("Data Reliability", "How much observed evidence supports this recommendation."),
        ("SNA Score", "How central the channel is in the creator network."),
        ("TF-IDF Similarity", "How closely channel text matches your brand keywords."),
        ("Semantic Score", "Meaning-level alignment between brand and creator content."),
        ("Tone Match", "Style/voice compatibility between creator and brand."),
        ("Engagement Score", "Observed response quality from likes/comments relative to views."),
        ("ML Potential", "Predicted upside when ML benchmark is enabled."),
        ("Reliability Multiplier", "Automatic penalty for weak-evidence channels."),
        ("Community ID", "Cluster label used to preserve diversity."),
    ]
    st.write("Client-facing vocabulary for presentations:")
    for term, desc in glossary:
        st.markdown(f"**{term}**: {desc}")


def _render_dashboard() -> None:
    result = st.session_state.get("result")
    req = st.session_state.get("run_request")
    if not result or not req:
        st.session_state.screen = "landing"
        st.rerun()

    brand = req["params"].get("brand_name", "Brand")
    category = req["params"].get("category", "Category")
    audience = req["params"].get("target_audience", "Audience")
    budget = req["params"].get("budget_usd", 0)

    ctop1, ctop2 = st.columns([4, 1])
    ctop1.markdown(
        f"""
<div class="topbar">
  <b>{brand}</b> &nbsp;|&nbsp; {category} &nbsp;|&nbsp; Budget ${int(_num(budget)):,}<br/>
  <span class="muted">{audience}</span>
</div>
""",
        unsafe_allow_html=True,
    )
    if ctop2.button("New Search"):
        st.session_state.screen = "landing"
        st.session_state.result = None
        st.rerun()

    tabs = st.tabs(
        [
            "Overview",
            "Top Matches",
            "Network Studio",
            "Text Intelligence",
            "ML Studio",
            "ROI Lab",
            "Content Strategy",
            "Executive Memo",
            "Glossary",
        ]
    )

    with tabs[0]:
        _render_overview(result, req)
    with tabs[1]:
        _render_top_matches(result, req)
    with tabs[2]:
        _render_network_studio(result)
    with tabs[3]:
        _render_text_intelligence(result, req)
    with tabs[4]:
        _render_ml_studio(result, req)
    with tabs[5]:
        _render_roi_lab(result, req)
    with tabs[6]:
        _render_content_strategy(result, req)
    with tabs[7]:
        _render_memo(result)
    with tabs[8]:
        _render_glossary()

    st.markdown("### Exported Files")
    st.json(result.get("artifact_paths", {}))


def main() -> None:
    _inject_css()
    _init_state()

    if st.session_state.screen == "landing":
        _render_landing()
    elif st.session_state.screen == "analyzing":
        _render_analyzing()
    else:
        _render_dashboard()


if __name__ == "__main__":
    main()
