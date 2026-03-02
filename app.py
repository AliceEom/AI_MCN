from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
import re
import time

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer

try:
    import plotly.express as px
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except Exception:
    px = None
    go = None
    PLOTLY_AVAILABLE = False

from src.config import DEFAULT_CONFIG
from src.orchestrator import run_pipeline
from src.ranking import select_top_with_diversity
from src.roi_simulation import simulate_roi


st.set_page_config(page_title="AI-MCN Demo", layout="wide")

MODEL_OPTIONS = ["LinearRegression", "LASSO", "Ridge", "CART", "RandomForest", "LightGBM"]


def _inject_css() -> None:
    st.markdown(
        """
<style>
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
:root { color-scheme: light !important; }
[data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
  background: #f5f7fb !important;
}
.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
  color: #10243f !important;
}
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
  color: #10243f !important;
  font-weight: 700;
}
.hero-wrap {
  border-radius: 20px;
  padding: 34px 30px;
  background: linear-gradient(140deg, #13395f 0%, #1576a3 48%, #3ab4cf 100%);
  color: #ffffff;
  border: 1px solid rgba(255,255,255,0.16);
  margin-bottom: 10px;
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
  color: #18324f !important;
  margin: 8px 0 14px 0;
  line-height: 1.35;
}
.card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  background: #ffffff;
  color: #18324f !important;
  margin-bottom: 12px;
  min-height: 142px;
  box-shadow: 0 1px 2px rgba(15, 35, 70, 0.04);
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
  color: #10243f !important;
}
.muted { color: #546173; font-size: 0.92rem; }
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color: #10243f !important; }
[data-testid="stDataFrame"] { border: 1px solid #dbe5f1; border-radius: 10px; }
[data-testid="stDownloadButton"] button, [data-testid="baseButton-secondary"], [data-testid="baseButton-primary"] {
  border-radius: 10px !important;
}
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


def _as_text_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if value is None:
        return []
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return []
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
    return [text]


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


def _link_button(container: st.delta_generator.DeltaGenerator, label: str, url: str) -> None:
    if not url:
        return
    btn = getattr(container, "link_button", None)
    if callable(btn):
        btn(label, url, use_container_width=True)
    else:
        container.markdown(f"[{label}]({url})")


def _kv_card(container: st.delta_generator.DeltaGenerator, title: str, value: str, subtitle: str = "") -> None:
    container.markdown(
        f"""
<div class="card">
  <div class="muted">{title}</div>
  <div style="font-size:1.1rem; font-weight:800; color:#0f2e55; margin-top:4px;">{value}</div>
  <div style="font-size:0.86rem; color:#5c6f84; margin-top:6px;">{subtitle}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _safe_plotly_chart(fig: object, key: str) -> dict | None:
    try:
        return st.plotly_chart(
            fig,
            use_container_width=True,
            key=key,
            on_select="rerun",
            selection_mode=("points",),
        )
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, key=key)
        return None


def _plotly_score_breakdown(top_df: pd.DataFrame):
    if not PLOTLY_AVAILABLE or top_df.empty:
        return None
    cols = [
        ("sna_score", "SNA"),
        ("tfidf_similarity", "TF-IDF"),
        ("semantic_score", "Semantic"),
        ("tone_match_score", "Tone"),
        ("engagement_score", "Engagement"),
        ("ml_potential_score", "ML Potential"),
    ]
    use_cols = [c for c, _ in cols if c in top_df.columns]
    if not use_cols:
        return None

    label_map = dict(cols)
    d = top_df[["channel_title"] + use_cols].copy().rename(columns=label_map)
    long_df = d.melt(id_vars=["channel_title"], var_name="signal", value_name="score")
    fig = px.bar(
        long_df,
        x="channel_title",
        y="score",
        color="signal",
        barmode="group",
        hover_data={"score": ":.3f"},
        color_discrete_sequence=["#4BA3C7", "#2E6FDC", "#4C956C", "#F59E0B", "#0EA5A4", "#A855F7"],
    )
    fig.update_layout(
        title="Top Influencer Score Breakdown (Interactive)",
        xaxis_title="Channel",
        yaxis_title="Score",
        legend_title="Signal",
        margin=dict(l=10, r=10, t=55, b=90),
    )
    fig.update_xaxes(tickangle=20)
    return fig


def _plotly_community(counts: pd.DataFrame):
    if not PLOTLY_AVAILABLE or counts.empty:
        return None
    d = counts.copy()
    d["community_id"] = d["community_id"].astype(str)
    fig = px.bar(
        d,
        x="community_id",
        y="channels",
        color="channels",
        color_continuous_scale="Blues",
        hover_data={"channels": True},
    )
    fig.update_layout(
        title="Community Distribution (Interactive)",
        xaxis_title="Community",
        yaxis_title="Number of Channels",
        margin=dict(l=10, r=10, t=50, b=50),
        coloraxis_showscale=False,
    )
    return fig


def _plotly_network_chart(graph: dict, scored_df: pd.DataFrame, top_nodes: int, min_edge_weight: int) -> tuple[object | None, pd.DataFrame]:
    nodes_df = pd.DataFrame()
    if not PLOTLY_AVAILABLE:
        return None, nodes_df

    edge_df = graph.get("edges", pd.DataFrame(columns=["source", "target", "weight"])).copy()
    if edge_df.empty:
        return None, nodes_df

    edge_df["source"] = edge_df["source"].astype(str)
    edge_df["target"] = edge_df["target"].astype(str)
    if "weight" in edge_df.columns:
        edge_df["weight"] = pd.to_numeric(edge_df["weight"], errors="coerce").fillna(0)
        edge_df = edge_df[edge_df["weight"] >= max(1, int(min_edge_weight))]
    if edge_df.empty:
        return None, nodes_df

    rank_ids = scored_df.sort_values("final_score", ascending=False)["_channel_id"].astype(str).head(max(30, int(top_nodes)))
    selected = set(rank_ids.tolist())
    edge_sub = edge_df[edge_df["source"].isin(selected) & edge_df["target"].isin(selected)].copy()
    if edge_sub.empty:
        edge_sub = edge_df.head(700).copy()
        selected = set(edge_sub["source"].tolist() + edge_sub["target"].tolist())

    if not selected:
        return None, nodes_df

    sel_nodes = sorted(selected)
    rng = np.random.default_rng(42)
    pos = {n: rng.random(2) for n in sel_nodes}

    for _ in range(120):
        for _, r in edge_sub.iterrows():
            a = str(r["source"])
            b = str(r["target"])
            w = float(r.get("weight", 1.0))
            delta = pos[b] - pos[a]
            pos[a] += 0.0015 * w * delta
            pos[b] -= 0.0015 * w * delta

    meta = scored_df.copy()
    meta["_channel_id"] = meta["_channel_id"].astype(str)
    meta = meta.drop_duplicates("_channel_id").set_index("_channel_id")

    nodes = []
    for n in sel_nodes:
        row = meta.loc[n] if n in meta.index else pd.Series(dtype=object)
        nodes.append(
            {
                "_channel_id": n,
                "x": float(pos[n][0]),
                "y": float(pos[n][1]),
                "channel_title": str(row.get("channel_title", n)),
                "community_id": int(_num(row.get("community_id"), -1)),
                "final_score": float(_num(row.get("final_score"), 0)),
                "n_videos": int(_num(row.get("n_videos"), 0)),
                "median_views": int(_num(row.get("median_views"), 0)),
            }
        )
    nodes_df = pd.DataFrame(nodes).sort_values("final_score", ascending=False).reset_index(drop=True)

    ex, ey = [], []
    for _, r in edge_sub.iterrows():
        a = str(r["source"])
        b = str(r["target"])
        ex.extend([pos[a][0], pos[b][0], None])
        ey.extend([pos[a][1], pos[b][1], None])

    edge_trace = go.Scatter(
        x=ex,
        y=ey,
        mode="lines",
        line=dict(color="rgba(148,163,184,0.40)", width=0.7),
        hoverinfo="skip",
        showlegend=False,
    )
    node_trace = go.Scatter(
        x=nodes_df["x"],
        y=nodes_df["y"],
        mode="markers",
        marker=dict(
            size=(8 + 28 * nodes_df["final_score"].clip(lower=0)).tolist(),
            color=nodes_df["community_id"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Community"),
            line=dict(color="#ffffff", width=0.6),
            opacity=0.95,
        ),
        text=nodes_df["channel_title"],
        customdata=np.stack(
            [
                nodes_df["_channel_id"],
                nodes_df["final_score"].round(3).astype(str),
                nodes_df["n_videos"].astype(str),
                nodes_df["median_views"].astype(str),
            ],
            axis=-1,
        ),
        hovertemplate="<b>%{text}</b><br>Channel ID: %{customdata[0]}<br>Final Score: %{customdata[1]}<br>Videos: %{customdata[2]}<br>Median Views: %{customdata[3]}<extra></extra>",
    )
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="Influencer Network (Interactive: zoom/pan/hover)",
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        dragmode="pan",
    )
    return fig, nodes_df


def _parse_strategy_blocks(markdown_text: str) -> list[tuple[str, str]]:
    text = str(markdown_text or "").strip()
    if not text:
        return []
    lines = text.splitlines()
    blocks: list[tuple[str, list[str]]] = []
    current_title = "Strategy"
    current_body: list[str] = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("## "):
            if current_body:
                blocks.append((current_title, current_body))
            current_title = line.replace("## ", "").strip()
            current_body = []
        else:
            current_body.append(line)

    if current_body:
        blocks.append((current_title, current_body))

    clean_blocks = []
    for title, body_lines in blocks:
        body = "\n".join([b for b in body_lines if b.strip()]).strip()
        if body:
            clean_blocks.append((title, body))
    return clean_blocks[:6]


def _thumbnail_hooks(product_name: str, must_keywords: list[str], channel_row: pd.Series) -> list[str]:
    product = str(product_name or "the product").strip()
    keywords = [str(k).strip() for k in must_keywords if str(k).strip()]
    channel = str(channel_row.get("channel_title", "creator")).strip()
    top_kw = str(channel_row.get("channel_keyword_summary", "")).split(",")
    top_kw = [x.strip() for x in top_kw if x.strip()][:2]

    hook1 = f"{product}: 7-day real test on {channel}"
    hook2 = f"Who should use {product}? Quick checklist"
    if keywords:
        hook2 = f"{product} + {keywords[0]}: what actually works"
    hook3 = f"Top mistakes before buying {product}"
    if top_kw:
        hook3 = f"{product} for {', '.join(top_kw)} viewers: before/after breakdown"
    return [hook1, hook2, hook3]


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

    params = req.get("params", {})
    st.markdown("### Campaign Input Snapshot")
    s1, s2, s3 = st.columns(3)
    _kv_card(s1, "Brand", str(params.get("brand_name", "N/A")), "Campaign owner")
    _kv_card(s2, "Product", str(params.get("product_name", "N/A")), str(params.get("category", "")))
    _kv_card(s3, "Market / Budget", f"{params.get('market', 'N/A')} / ${int(_num(params.get('budget_usd'))):,}", "Target market and total budget")

    s4, s5 = st.columns(2)
    _kv_card(s4, "Campaign Goal", str(params.get("campaign_goal", "N/A")), str(params.get("usp", ""))[:160])
    _kv_card(s5, "Target Audience", str(params.get("target_audience", "N/A"))[:180], "Audience definition used in matching")

    must = params.get("must_keywords", []) or []
    exclude = params.get("exclude_keywords", []) or []
    if must:
        st.markdown("**Must-have Keywords**")
        st.markdown(
            "".join([f"<span class='tag'>{str(k)}</span>" for k in must]),
            unsafe_allow_html=True,
        )
    if exclude:
        st.markdown("**Excluded Keywords**")
        st.markdown(
            "".join([f"<span class='tag' style='background:#fff4f4;border-color:#f2c1c1;color:#a13e3e'>{str(k)}</span>" for k in exclude]),
            unsafe_allow_html=True,
        )

    st.markdown("### Benchmark Panel (Anchor vs CeraVe)")
    bench = result.get("benchmark_summary", {}) or {}
    if not bench:
        st.info("Benchmark was disabled for this run.")
        return

    anchor_top = float(topn["final_score"].mean()) if not topn.empty else 0.0
    bench_top = float(_num(bench.get("topn_mean_score")))
    delta = anchor_top - bench_top
    verdict = "Anchor stronger" if delta >= 0 else "Benchmark stronger"
    vcolor = "#1B8F5A" if delta >= 0 else "#9A3E3E"

    b1, b2, b3, b4 = st.columns(4)
    _kv_card(b1, "Benchmark Brand", str(bench.get("brand", "N/A")), str(bench.get("top_channel", "N/A")))
    _kv_card(b2, "Anchor Mean Score", f"{anchor_top:.3f}", "Mean final score of current Top-N")
    _kv_card(b3, "Benchmark Mean Score", f"{bench_top:.3f}", "Mean final score of CeraVe Top-N")
    _kv_card(b4, "Score Gap", f"{delta:+.3f}", verdict)

    st.markdown(
        f"<div class='panel'><b>Benchmark Verdict:</b> "
        f"<span style='color:{vcolor}; font-weight:800'>{verdict}</span> "
        f"(Anchor minus Benchmark = {delta:+.3f}).</div>",
        unsafe_allow_html=True,
    )


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

    score_fig = _plotly_score_breakdown(ranked)
    if score_fig is not None:
        st.plotly_chart(score_fig, use_container_width=True, key="topmatch_score_breakdown")
    else:
        st.info("Interactive chart unavailable because Plotly is not installed.")
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
            btn1, btn2, btn3 = cols[1].columns(3)
            _link_button(btn1, "Open Channel", str(row.get("channel_url", "")))
            _link_button(btn2, "Representative Video", str(row.get("video_url", "")))
            _link_button(btn3, "Best Video", str(row.get("best_video_url", "")))
            cols[1].markdown(
                f"<span class='tag' style='border-color:{fit_color}; color:{fit_color}'>{fit_label}</span>"
                f"<span class='tag' style='border-color:{ev_color}; color:{ev_color}'>{ev_label}</span>",
                unsafe_allow_html=True,
            )
            cols[1].markdown(f"**Final Match Score:** {_num(row.get('display_score')):.3f}")
            cols[1].write(_plain_language_reason(row))

            m1, m2, m3, m4, m5 = cols[1].columns(5)
            m1.metric("Videos Used", f"{int(_num(row.get('n_videos'))):,}")
            m2.metric("Median Views", f"{int(_num(row.get('median_views'))):,}")
            m3.metric("Median Likes", f"{int(_num(row.get('median_likes'))):,}")
            m4.metric("Subscribers (est.)", f"{int(_num(row.get('est_subscribers'))):,}")
            m5.metric("Comments Collected", f"{int(_num(row.get('comment_samples_n', row.get('comments_n')))):,}")

            cols[1].markdown(
                f"**Signal Breakdown:** SNA {_num(row.get('sna_score')):.3f} | TF-IDF {_num(row.get('tfidf_similarity')):.3f} | "
                f"Semantic {_num(row.get('semantic_score')):.3f} | Tone {_num(row.get('tone_match_score')):.3f} | "
                f"Engagement {_num(row.get('engagement_score')):.3f} | ML {_num(row.get('ml_potential_score')):.3f}"
            )
            cols[1].markdown(
                f"**Score Controls:** Base {_num(row.get('final_score_base')):.3f} | "
                f"Reliability x{_num(row.get('credibility_multiplier')):.3f} | "
                f"Community {int(_num(row.get('community_id')))}"
            )
            cols[1].markdown(
                f"**Freshness:** Latest publish {_fmt_date(row.get('latest_publish'))} | "
                f"Days since latest {int(_num(row.get('days_since_latest')))}"
            )

            channel_profile = str(row.get("channel_profile_text", "")).strip()
            if channel_profile and channel_profile.lower() != "nan":
                cols[1].markdown(f"**Channel Snapshot:** {channel_profile}")

            keyword_summary = str(row.get("channel_keyword_summary", "")).strip()
            if keyword_summary and keyword_summary.lower() != "nan":
                cols[1].markdown(f"**Channel Keywords:** {keyword_summary}")

            best_video_title = str(row.get("best_video_title", "")).strip()
            if best_video_title and best_video_title.lower() != "nan":
                cols[1].markdown(
                    f"**Best Video in Dataset:** {best_video_title} ({int(_num(row.get('best_video_views'))):,} views)"
                )

            recent_videos = _as_text_list(row.get("recent_video_titles"))
            if recent_videos:
                cols[1].markdown("**Recent Video Titles**")
                for item in recent_videos[:5]:
                    cols[1].markdown(f"- {item}")

            top_liked_comment = str(row.get("top_liked_comment", "")).strip()
            if top_liked_comment and top_liked_comment.lower() != "nan":
                cols[1].markdown(f"**Top Liked Audience Comment:** {top_liked_comment}")

            recent_comments = _as_text_list(row.get("recent_comments"))
            if recent_comments:
                cols[1].markdown("**Recent Audience Comments**")
                for item in recent_comments[:3]:
                    cols[1].markdown(f"- {item}")

            cols[1].markdown(f"**Model Rationale:** {row.get('alignment_rationale', '')}")
            flags = row.get("red_flags", [])
            if isinstance(flags, list) and flags:
                for f in flags:
                    cols[1].warning(f)

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
        "est_subscribers",
        "est_video_count",
        "channel_profile_text",
        "channel_keyword_summary",
        "best_video_title",
        "best_video_views",
        "top_liked_comment",
        "channel_url",
        "video_url",
        "best_video_url",
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

    net_fig, net_nodes = _plotly_network_chart(graph, scored, top_nodes=top_nodes, min_edge_weight=min_edge_weight)
    if net_fig is not None:
        st.caption("Interactive network: pan/zoom/hover enabled. Use node picker below for detailed channel stats.")
        _safe_plotly_chart(net_fig, key="network_studio_plotly")
    else:
        st.info("Interactive network unavailable because Plotly is not installed.")

    if not net_nodes.empty:
        node_options = net_nodes["_channel_id"].tolist()
        selected_node = st.selectbox(
            "Inspect Node Details",
            options=node_options,
            format_func=lambda cid: f"{net_nodes.loc[net_nodes['_channel_id'] == cid, 'channel_title'].iloc[0]} ({cid})",
        )
        node_row = net_nodes[net_nodes["_channel_id"] == selected_node].iloc[0]
        z1, z2, z3, z4 = st.columns(4)
        z1.metric("Selected Channel", node_row["channel_title"])
        z2.metric("Community", int(_num(node_row.get("community_id"), -1)))
        z3.metric("Final Score", f"{_num(node_row.get('final_score')):.3f}")
        z4.metric("Median Views", f"{int(_num(node_row.get('median_views'))):,}")

    comm_df = scored.copy()
    if not include_micro:
        comm_df = comm_df[comm_df["community_id"] >= 0]
    counts = comm_df["community_id"].value_counts().rename_axis("community_id").reset_index(name="channels")

    comm_fig = _plotly_community(counts)
    if comm_fig is not None:
        st.plotly_chart(comm_fig, use_container_width=True, key="community_plotly")
    else:
        st.info("Interactive community chart unavailable because Plotly is not installed.")

    c1, c2 = st.columns([2, 1])
    c1.markdown("### Community Diagnostics")
    if not counts.empty:
        largest_share = float(counts["channels"].max() / max(comm_df.shape[0], 1))
        c1.caption(f"Communities shown: {counts.shape[0]}, Largest share: {largest_share:.1%}")
    c1.dataframe(counts.head(40), use_container_width=True)

    c2.markdown("### Graph Meta")
    meta = graph.get("meta", {})
    _kv_card(c2, "Nodes", f"{int(_num(meta.get('n_nodes'))):,}", "Unique channels in graph")
    _kv_card(c2, "Edges", f"{int(_num(meta.get('n_edges'))):,}", "Connections after tag filtering")
    _kv_card(c2, "Dropped Tags", f"{int(_num(meta.get('dropped_tags_too_common'))):,}", "Over-common tags removed")

    st.markdown("### Bias Report")
    bias = result.get("bias_report", {}) or {}
    b1, b2, b3 = st.columns(3)
    _kv_card(b1, "Degree Top Overlap", f"{int(_num(bias.get('degree_top_overlap'))):,}/{int(_num(bias.get('top_n'))):,}", "Lower overlap implies reduced popularity bias")
    _kv_card(b2, "Unique Communities in Top-N", f"{int(_num(bias.get('n_unique_communities_topn'))):,}", "Diversity signal")
    _kv_card(b3, "Unique Channels in Top-N", f"{int(_num(bias.get('n_unique_final'))):,}", "De-duplicated shortlist size")
    narrative = str(bias.get("narrative", "")).strip()
    if narrative:
        st.markdown(f"<div class='panel'>{narrative}</div>", unsafe_allow_html=True)
    degree_top = pd.DataFrame(bias.get("degree_top_channels", []))
    if not degree_top.empty:
        st.dataframe(degree_top.head(15), use_container_width=True)


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
    if PLOTLY_AVAILABLE:
        p = subset.copy()
        median_views = p["median_views"].fillna(0) if "median_views" in p.columns else pd.Series(np.zeros(len(p)), index=p.index)
        p["marker_size"] = 10 + 36 * (np.log1p(median_views) / max(np.log1p(median_views).max(), 1e-6))
        fig = px.scatter(
            p,
            x="tfidf_similarity",
            y="semantic_score",
            color=p.get("evidence_score", pd.Series(np.zeros(len(p)))),
            size="marker_size",
            hover_name="channel_title",
            hover_data={
                "final_score": ":.3f",
                "median_views": True,
                "n_videos": True,
                "marker_size": False,
            },
            color_continuous_scale="Viridis",
        )
        fig.update_layout(
            title="Text Match Map (Interactive)",
            xaxis_title="TF-IDF Similarity",
            yaxis_title="Semantic Alignment",
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig, use_container_width=True, key="text_scatter_plotly")
    else:
        st.info("Interactive scatter unavailable because Plotly is not installed.")

    terms = _top_terms(subset, top_n=top_term_n, min_df=min_df_terms)
    if not terms.empty:
        if PLOTLY_AVAILABLE:
            show = terms.head(25).copy().sort_values("count", ascending=True)
            fig_terms = px.bar(
                show,
                x="count",
                y="term",
                orientation="h",
                color="count",
                color_continuous_scale="Blues",
            )
            fig_terms.update_layout(
                title="Top Frequent Terms in Candidate Channel Text (Interactive)",
                xaxis_title="Frequency",
                yaxis_title="Term",
                margin=dict(l=10, r=10, t=50, b=10),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_terms, use_container_width=True, key="text_terms_plotly")
        else:
            st.info("Interactive term chart unavailable because Plotly is not installed.")

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
        if PLOTLY_AVAILABLE:
            cov_df = pd.DataFrame({"keyword": coverage_rate.index.tolist(), "coverage_rate": coverage_rate.values.tolist()})
            fig_cov = px.bar(
                cov_df,
                x="keyword",
                y="coverage_rate",
                color="coverage_rate",
                color_continuous_scale="Teal",
                hover_data={"coverage_rate": ":.2%"},
            )
            fig_cov.update_layout(
                title="Keyword Coverage Across Top Candidate Channels (Interactive)",
                xaxis_title="Keyword",
                yaxis_title="Coverage Rate",
                yaxis=dict(range=[0, 1]),
                margin=dict(l=10, r=10, t=50, b=40),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_cov, use_container_width=True, key="keyword_coverage_plotly")
        else:
            st.info("Interactive keyword coverage chart unavailable because Plotly is not installed.")
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
    if not PLOTLY_AVAILABLE:
        st.error("Plotly is required for interactive ML charts. Please install dependencies from requirements.txt.")
        return

    cv_df = result["ml_cv_results"].copy()
    pred_df = result.get("ml_pred_actual", pd.DataFrame()).copy()
    shap_summary_df = result.get("ml_shap_summary", pd.DataFrame()).copy()
    shap_dep_df = result.get("ml_shap_dependence", pd.DataFrame()).copy()

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

    p = cv_df[cv_df["status"].isin(["ok", "reference"])].copy()
    p = p.sort_values("rmse_mean", ascending=True)
    fig = px.bar(
        p,
        x="model",
        y="rmse_mean",
        color="status",
        hover_data={"rmse_mean": ":.5f", "mae_mean": ":.5f", "r2_mean": ":.5f"},
        color_discrete_map={"ok": "#2E6FDC", "reference": "#94A3B8"},
    )
    fig.update_layout(
        title="5-Fold CV RMSE by Model (Interactive)",
        xaxis_title="Model",
        yaxis_title="RMSE",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, key="ml_cv_plotly")
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

    if not pred_df.empty and {"actual", "predicted"}.issubset(pred_df.columns):
        pred_df["error"] = (pred_df["predicted"] - pred_df["actual"]).abs()
        fig_pred = px.scatter(
            pred_df,
            x="actual",
            y="predicted",
            color="error",
            color_continuous_scale="Viridis",
            opacity=0.65,
            hover_data={"actual": ":.4f", "predicted": ":.4f", "error": ":.4f"},
        )
        minv = float(min(pred_df["actual"].min(), pred_df["predicted"].min()))
        maxv = float(max(pred_df["actual"].max(), pred_df["predicted"].max()))
        fig_pred.add_trace(
            go.Scatter(
                x=[minv, maxv],
                y=[minv, maxv],
                mode="lines",
                line=dict(color="#ef4444", dash="dash"),
                name="Perfect Fit",
                showlegend=False,
            )
        )
        fig_pred.update_layout(
            title="Predicted vs Actual Engagement Target (Interactive)",
            xaxis_title="Actual",
            yaxis_title="Predicted",
            margin=dict(l=10, r=10, t=50, b=10),
            coloraxis_colorbar=dict(title="Abs Error"),
        )
        st.plotly_chart(fig_pred, use_container_width=True, key="ml_pred_actual_plotly")

    st.markdown("### SHAP Explainability (Interactive)")
    if not shap_summary_df.empty:
        s = shap_summary_df.sort_values("mean_abs_shap", ascending=True).tail(15)
        fig_shap = px.bar(
            s,
            x="mean_abs_shap",
            y="feature",
            orientation="h",
            color="mean_abs_shap",
            color_continuous_scale="Blues",
            hover_data={"mean_abs_shap": ":.5f"},
        )
        fig_shap.update_layout(
            title="SHAP Feature Importance",
            xaxis_title="Mean |SHAP|",
            yaxis_title="Feature",
            margin=dict(l=10, r=10, t=50, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_shap, use_container_width=True, key="ml_shap_summary_plotly")
    else:
        st.caption("SHAP summary data is unavailable for this run.")

    if not shap_dep_df.empty and {"feature", "feature_value", "shap_value"}.issubset(shap_dep_df.columns):
        features = shap_dep_df["feature"].dropna().astype(str).unique().tolist()
        if features:
            fsel = st.selectbox("SHAP Dependence Feature", features, index=0)
            d = shap_dep_df[shap_dep_df["feature"] == fsel].copy()
            if not d.empty:
                fig_dep = px.scatter(
                    d,
                    x="feature_value",
                    y="shap_value",
                    color="shap_value",
                    color_continuous_scale="RdBu",
                    hover_data={"feature_value": ":.4f", "shap_value": ":.4f"},
                )
                fig_dep.update_layout(
                    title=f"SHAP Dependence: {fsel}",
                    xaxis_title="Feature Value",
                    yaxis_title="SHAP Value",
                    margin=dict(l=10, r=10, t=50, b=10),
                )
                st.plotly_chart(fig_dep, use_container_width=True, key=f"ml_shap_dep_{fsel}")


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
    if PLOTLY_AVAILABLE:
        funnel_df = pd.DataFrame(
            {
                "stage": ["Impressions", "Clicks", "Conversions", "Revenue"],
                "value": [roi.get("impressions", 0), roi.get("clicks", 0), roi.get("conversions", 0), roi.get("revenue", 0)],
            }
        )
        fig_funnel = px.bar(
            funnel_df,
            x="value",
            y="stage",
            orientation="h",
            color="stage",
            color_discrete_sequence=["#93C5FD", "#60A5FA", "#38BDF8", "#0EA5A4"],
        )
        fig_funnel.update_layout(
            title="ROI Funnel (Interactive)",
            xaxis_title="Value",
            yaxis_title="",
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_funnel, use_container_width=True, key="roi_funnel_plotly")
    else:
        st.info("Interactive ROI funnel unavailable because Plotly is not installed.")
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

    if PLOTLY_AVAILABLE:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=budget_grid, y=roas_grid, mode="lines+markers", name="ROAS", yaxis="y1", line=dict(color="#0E7490")))
        fig.add_trace(go.Scatter(x=budget_grid, y=conv_grid, mode="lines+markers", name="Conversions", yaxis="y2", line=dict(color="#16A34A")))
        fig.update_layout(
            title="Budget Sensitivity: ROAS and Conversions (Interactive)",
            xaxis=dict(title="Budget (USD)"),
            yaxis=dict(title="ROAS", side="left"),
            yaxis2=dict(title="Conversions", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.06, x=0),
            margin=dict(l=10, r=10, t=55, b=10),
        )
        st.plotly_chart(fig, use_container_width=True, key="roi_sensitivity_plotly")
    else:
        st.info("Interactive ROI sensitivity chart unavailable because Plotly is not installed.")


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
    product_name = str(req.get("params", {}).get("product_name", "Product"))
    must_keywords = req.get("params", {}).get("must_keywords", []) or []

    for idx, (_, row) in enumerate(topn.head(count).iterrows(), start=1):
        cid = str(row["_channel_id"])
        strategy_text = str(strategies.get(cid, "No strategy generated."))
        blocks = _parse_strategy_blocks(strategy_text)
        hooks = _thumbnail_hooks(product_name, must_keywords, row)

        with st.container(border=True):
            left, right = st.columns([1, 2.5])
            image_url = str(row.get("image_url", "")).strip()
            if image_url:
                left.image(image_url, use_container_width=True)
            left.markdown(f"### #{idx} {row.get('channel_title', 'Creator')}")
            left.metric("Match Score", f"{_num(row.get('final_score')):.3f}")
            left.metric("Median Views", f"{int(_num(row.get('median_views'))):,}")
            _link_button(left, "Open Channel", str(row.get("channel_url", "")))
            _link_button(left, "Representative Video", str(row.get("video_url", "")))

            right.markdown("#### Campaign Structure")
            if blocks:
                tab_labels = [b[0][:22] for b in blocks[:3]]
                tabs = right.tabs(tab_labels)
                for i, (title, body) in enumerate(blocks[:3]):
                    with tabs[i]:
                        st.markdown(f"**{title}**")
                        st.markdown(body)
            else:
                right.markdown(strategy_text)

            right.markdown("#### Creative Thumbnail Hooks")
            h1, h2, h3 = right.columns(3)
            _kv_card(h1, "Hook 1", hooks[0], "Topline headline")
            _kv_card(h2, "Hook 2", hooks[1], "Problem-solution angle")
            _kv_card(h3, "Hook 3", hooks[2], "High-intent CTA angle")


def _render_memo(result: dict) -> None:
    memo = result["executive_memo_md"]
    st.markdown("### Executive Memo Dashboard")
    lines = str(memo or "").splitlines()
    sections: list[tuple[str, str]] = []
    cur_title = "Overview"
    cur_lines: list[str] = []
    for ln in lines:
        if ln.startswith("## "):
            if cur_lines:
                sections.append((cur_title, "\n".join(cur_lines).strip()))
            cur_title = ln.replace("## ", "").strip()
            cur_lines = []
        else:
            cur_lines.append(ln)
    if cur_lines:
        sections.append((cur_title, "\n".join(cur_lines).strip()))

    d1, d2 = st.columns([1, 1])
    d1.download_button(
        "Download Memo (Markdown)",
        data=memo,
        file_name="brand_partnership_memo.md",
        mime="text/markdown",
    )
    d2.download_button(
        "Download Memo (Text)",
        data=re.sub(r"[#*`]", "", memo),
        file_name="brand_partnership_memo.txt",
        mime="text/plain",
    )

    if sections:
        tab_labels = [t[:22] for t, _ in sections[:8]]
        tabs = st.tabs(tab_labels)
        for i, (title, body) in enumerate(sections[:8]):
            with tabs[i]:
                st.markdown(f"#### {title}")
                st.markdown(body)
    else:
        st.markdown(memo)


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


def _render_export_panel(result: dict) -> None:
    paths = result.get("artifact_paths", {}) or {}
    st.markdown("### Export Center")
    if not paths:
        st.info("No artifact paths were recorded for this run.")
        return

    items = [
        ("Top-N Recommendations CSV", paths.get("topn_csv") or paths.get("top_csv") or ""),
        ("All Scored Channels CSV", paths.get("scored_csv") or ""),
        ("Executive Memo", paths.get("memo_md") or ""),
    ]

    cols = st.columns(len(items))
    for i, (label, p) in enumerate(items):
        path = Path(str(p)) if p else None
        exists = bool(path and path.exists())
        subtitle = str(path.name) if exists else "Not available"
        _kv_card(cols[i], label, "Ready" if exists else "Missing", subtitle)
        if exists:
            mime = "text/csv" if path.suffix.lower() == ".csv" else "text/markdown"
            cols[i].download_button(
                f"Download {label}",
                data=path.read_bytes(),
                file_name=path.name,
                mime=mime,
                use_container_width=True,
            )

    with st.expander("Show Full Artifact Paths"):
        st.dataframe(pd.DataFrame({"artifact": [x[0] for x in items], "path": [x[1] for x in items]}), use_container_width=True)


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

    _render_export_panel(result)


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
