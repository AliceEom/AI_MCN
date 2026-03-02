from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
os.environ.setdefault(
    "MPLCONFIGDIR",
    str((Path(__file__).resolve().parents[1] / "artifacts" / "cache" / "mpl")),
)
import matplotlib


def _running_in_notebook() -> bool:
    try:
        from IPython import get_ipython  # type: ignore

        shell: Any = get_ipython()
        if shell is None:
            return False
        cfg = getattr(shell, "config", {})
        return "IPKernelApp" in cfg
    except Exception:
        return False


# In notebook/Colab, keep inline backend for visible plots.
# In script/server mode, use Agg for file-safe rendering.
_backend_override = os.environ.get("AI_MCN_MPL_BACKEND", "").strip()
if _backend_override:
    matplotlib.use(_backend_override)
elif not _running_in_notebook():
    matplotlib.use("Agg")
from matplotlib import pyplot as plt


def model_cv_figure(cv_df: pd.DataFrame):
    d = cv_df[cv_df["status"].isin(["ok", "reference"])].copy()
    d = d.sort_values("rmse_mean", ascending=True)

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    colors = ["#4C9BE8" if s == "ok" else "#B0BEC5" for s in d["status"]]
    ax.bar(d["model"], d["rmse_mean"], color=colors)
    ax.set_title("5-Fold CV RMSE by Model")
    ax.set_ylabel("RMSE")
    ax.tick_params(axis="x", rotation=22)
    fig.tight_layout()
    return fig


def score_breakdown_figure(top_df: pd.DataFrame):
    cols = [
        ("sna_score", "SNA"),
        ("tfidf_similarity", "TF-IDF"),
        ("semantic_score", "Semantic"),
        ("tone_match_score", "Tone"),
        ("engagement_score", "Observed Engagement"),
        ("ml_potential_score", "ML Potential"),
    ]
    x = np.arange(len(top_df))
    width = 0.12

    fig, ax = plt.subplots(figsize=(12, 5.5))
    for i, (col, name) in enumerate(cols):
        if col not in top_df.columns:
            continue
        ax.bar(x + (i - 2.5) * width, top_df[col].fillna(0).to_numpy(), width=width, label=name)

    ax.set_xticks(x)
    ax.set_xticklabels(top_df["channel_title"].tolist(), rotation=15, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_title("Top Influencer Score Breakdown")
    ax.set_ylabel("Score")
    ax.legend(loc="upper right", ncol=3, fontsize=8)
    fig.tight_layout()
    return fig


def community_figure(scored_df: pd.DataFrame, top_k: int = 15, include_micro: bool = False):
    d = scored_df.copy()
    if "community_id" not in d.columns or d.empty:
        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        ax.text(0.5, 0.5, "No community data", ha="center", va="center")
        ax.axis("off")
        return fig

    if not include_micro:
        d = d[d["community_id"] >= 0]

    c = d.groupby("community_id", as_index=False).agg(n_channels=("_channel_id", "nunique"))
    c = c.sort_values("n_channels", ascending=False).reset_index(drop=True)

    if c.empty:
        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        ax.text(0.5, 0.5, "No communities to display", ha="center", va="center")
        ax.axis("off")
        return fig

    top_k = max(3, int(top_k))
    if len(c) > top_k:
        other_count = int(c.iloc[top_k:]["n_channels"].sum())
        c = c.head(top_k).copy()
        c.loc[len(c)] = {"community_id": "Other", "n_channels": other_count}

    labels = c["community_id"].astype(str).tolist()
    colors = ["#6EC6FF" if x != "Other" else "#B0BEC5" for x in labels]

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.bar(labels, c["n_channels"], color=colors)
    ax.set_title("Community Distribution (Top Communities)")
    ax.set_xlabel("Community")
    ax.set_ylabel("Number of Channels")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def roi_funnel_figure(roi: dict):
    stages = ["Impressions", "Clicks", "Conversions", "Revenue"]
    values = [
        roi.get("impressions", 0),
        roi.get("clicks", 0),
        roi.get("conversions", 0),
        roi.get("revenue", 0),
    ]

    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    y = np.arange(len(stages))[::-1]
    ax.barh(y, values, color=["#90CAF9", "#64B5F6", "#42A5F5", "#1E88E5"])
    ax.set_yticks(y)
    ax.set_yticklabels(stages)
    ax.set_title("ROI Funnel")
    ax.set_xlabel("Value")
    fig.tight_layout()
    return fig


def network_figure(graph: dict, scored_df: pd.DataFrame, top_nodes: int = 120, min_edge_weight: int = 2):
    nodes = graph.get("nodes", [])
    edge_df = graph.get("edges", pd.DataFrame(columns=["source", "target", "weight"]))
    if "weight" in edge_df.columns:
        edge_df = edge_df[edge_df["weight"] >= max(1, int(min_edge_weight))].copy()

    ranked_ids = scored_df.sort_values("final_score", ascending=False)["_channel_id"].astype(str).head(top_nodes)
    selected = set(ranked_ids.tolist())

    edge_sub = edge_df[edge_df["source"].isin(selected) & edge_df["target"].isin(selected)].copy()
    if edge_sub.empty:
        edge_sub = edge_df.head(400).copy()
        selected = set(edge_sub["source"].astype(str).tolist() + edge_sub["target"].astype(str).tolist())

    if not selected:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, "No graph edges available", ha="center", va="center")
        ax.axis("off")
        return fig

    sel_nodes = sorted(selected)
    idx = {n: i for i, n in enumerate(sel_nodes)}

    # Simple random-layout seeded for deterministic visualization.
    rng = np.random.default_rng(42)
    pos = {n: rng.random(2) for n in sel_nodes}

    # Pull connected nodes closer based on weight for a readable layout.
    for _ in range(120):
        for _, r in edge_sub.iterrows():
            a = str(r["source"])
            b = str(r["target"])
            w = float(r.get("weight", 1.0))
            pa = pos[a]
            pb = pos[b]
            delta = pb - pa
            pos[a] += 0.0015 * w * delta
            pos[b] -= 0.0015 * w * delta

    meta = scored_df.set_index(scored_df["_channel_id"].astype(str))

    fig, ax = plt.subplots(figsize=(9.5, 7.0))

    for _, r in edge_sub.iterrows():
        a = str(r["source"])
        b = str(r["target"])
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color="#CFD8DC", linewidth=0.4, alpha=0.65)

    xs, ys, colors, sizes = [], [], [], []
    for n in sel_nodes:
        xs.append(pos[n][0])
        ys.append(pos[n][1])
        if n in meta.index:
            colors.append(meta.loc[n].get("community_id", -1))
            sizes.append(20 + 80 * float(meta.loc[n].get("final_score", 0.0)))
        else:
            colors.append(-1)
            sizes.append(20)

    sc = ax.scatter(xs, ys, c=colors, cmap="viridis", s=np.array(sizes), alpha=0.95)
    fig.colorbar(sc, ax=ax, fraction=0.03, pad=0.02, label="Community")
    ax.set_title("Influencer Network (Top Subgraph)")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    return fig
