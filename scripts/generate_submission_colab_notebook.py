from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "submission_colab_python" / "ai_mcn_submission"
OUT_NB = ROOT / "submission_colab_python" / "AI_MCN_Analysis_ML_Submission_Colab.ipynb"
OUT_PY = ROOT / "submission_colab_python" / "AI_MCN_Analysis_ML_Submission_Colab.py"

MODULE_ORDER = [
    "utils.py",
    "config.py",
    "analysis_categories.py",
    "data_bootstrap.py",
    "data_prep.py",
    "network_scoring.py",
    "text_scoring.py",
    "semantic_enrichment.py",
    "ml_modeling.py",
    "ranking.py",
    "roi_simulation.py",
    "channel_details.py",
    "channel_media.py",
    "content_generation.py",
    "orchestrator.py",
    "visualization.py",
]


def _strip_relative_imports(code: str) -> str:
    lines: list[str] = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("from ."):
            continue
        if stripped == "from __future__ import annotations":
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def _module_code(name: str) -> str:
    src = PKG_DIR / name
    if not src.exists():
        raise FileNotFoundError(f"Missing module: {src}")

    code = _strip_relative_imports(src.read_text(encoding="utf-8"))
    if name == "config.py":
        code = code.replace(
            "BASE_DIR = Path(__file__).resolve().parents[1]",
            "BASE_DIR = Path(__file__).resolve().parent",
        )
    return f"# ===== Begin {name} =====\n{code.rstrip()}\n# ===== End {name}"


def build_core_cell() -> str:
    parts: list[str] = [
        "# Runtime guard for notebook execution\n"
        "from pathlib import Path as _NotebookPathGuard\n"
        "if '__file__' not in globals():\n"
        "    __file__ = str((_NotebookPathGuard.cwd() / 'AI_MCN_notebook_runtime.py').resolve())\n"
    ]
    for name in MODULE_ORDER:
        parts.append(_module_code(name))
    return "\n\n".join(parts).strip() + "\n"


def md(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.strip("\n") + "\n",
    }


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip("\n") + "\n",
    }


def build_notebook() -> dict:
    core_code = build_core_cell()
    cells: list[dict] = []

    # Intro
    cells.append(md(
        """
# AI-MCN Course Project Submission Notebook (Standalone)

**Course:** MSIS 521  
**Project:** AI-MCN Influencer Matching for Beauty Campaigns  
**Team:** (Fill your team member names here)

This notebook is intentionally organized in a class-style flow:
- each analysis block has a clear title,
- each block explains **why** we run it, **how** it works, and **how to read** outputs,
- each block contains multiple small code cells, so results appear directly below each step.

All core code used in the project is embedded in this notebook, so this `.ipynb` runs as a standalone submission file.
"""
    ))

    cells.append(md(
        """
## 0) Setup

### Why this step
Colab runtimes are temporary. We install dependencies and initialize plotting/runtime settings first.

### How to read the output
If setup cells run without error, the environment is ready.
"""
    ))

    cells.append(code(
        """
# Install libraries used in this submission (safe to rerun)
!pip -q install pandas numpy scikit-learn matplotlib seaborn lightgbm shap gdown
"""
    ))

    cells.append(code(
        """
# Core imports for analysis sections
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from IPython.display import display

sns.set_theme(style="whitegrid")
# Keep notebook output clean for grading by suppressing known non-critical warnings.
warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names, but LGBMRegressor was fitted with feature names",
)
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module="seaborn",
)
print("Environment ready.")
"""
    ))

    cells.append(md(
        """
## 1) Load Embedded Project Code (One-Time Initialization)

### Why this step
To keep this notebook standalone, we load all project modules directly in this notebook runtime.

### How to read the output
Run the code cell once. It defines functions/classes used in all later analysis cells.
"""
    ))

    cells.append(code(core_code))

    cells.append(code(
        """
# Ensure required runtime folders exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

print("BASE_DIR:", BASE_DIR)
print("DATA_DIR:", DATA_DIR)
print("PLOTS_DIR:", PLOTS_DIR)
print("REPORTS_DIR:", REPORTS_DIR)
"""
    ))

    # Method map
    cells.append(md(
        """
## 2) Method Map (Class Concepts)

### Why this step
This table explicitly maps implemented methods to course concepts.

### How to read the output
Rows with `class_concept=True` indicate direct alignment with class content.
"""
    ))

    cells.append(code(
        """
# Display project method taxonomy
category_df = get_analysis_category_table()
display(category_df)
"""
    ))

    # Data setup section
    cells.append(md(
        """
## 3) Data Preparation and Cleaning

### Why this analysis
Raw social data often includes duplicates, noisy/non-relevant records, and inconsistent metrics.
Careful cleaning is required to produce reliable matching and ML outputs.

### How it was done
1. Verify and bootstrap required CSV files.
2. Load raw videos/comments/master tables.
3. Define campaign brief (drives filtering and scoring).
4. Clean/aggregate data using project preprocessing pipeline.

### How to read outputs
- Row counts should decrease after filtering.
- Prepared tables should include engineered variables (engagement, recency, text fields).
"""
    ))

    cells.append(code(
        """
# Step 3.1: Ensure required data files are available
bootstrap_report = ensure_full_data_from_gdrive(DATA_DIR)
print(json.dumps(bootstrap_report, indent=2))

videos_csv, comments_csv, master_csv = resolve_data_paths()
print("Videos CSV:", videos_csv)
print("Comments CSV:", comments_csv)
print("Master CSV:", master_csv)
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 3.1
If `complete` is true, all required datasets are present for the full pipeline.
If not, check file paths or Google Drive download permissions.
"""
    ))

    cells.append(code(
        """
# Step 3.2: Load raw data and inspect schema
videos_raw, comments_raw, master_raw = load_data(videos_csv, comments_csv, master_csv)

print("videos_raw shape:", videos_raw.shape)
print("comments_raw shape:", comments_raw.shape)
print("master_raw shape:", master_raw.shape if master_raw is not None else None)

print("\\nVideo sample:")
display(videos_raw.head(2))
print("\\nComment sample:")
display(comments_raw.head(2))
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 3.2
This confirms raw table structure and data availability before preprocessing.
Any missing key columns should be fixed before continuing.
"""
    ))

    cells.append(code(
        """
# Step 3.3: Define campaign brief used in downstream scoring
brand_params = {
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
brief = build_brand_brief(brand_params)
print(brief.brief_md)
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 3.3
This brief is the business input. It directly affects keyword filtering, text relevance, and final ranking behavior.
"""
    ))

    cells.append(code(
        """
# Step 3.4: Run cleaning + feature engineering pipeline
prepared = prepare_all(
    videos_raw,
    comments_raw,
    must_keywords=brief.must_keywords,
    exclude_keywords=brief.exclude_keywords,
)

summary_df = pd.DataFrame(
    {
        "metric": [
            "Raw videos", "Prepared videos", "Raw comments", "Prepared comments", "Prepared channels"
        ],
        "value": [
            len(videos_raw), len(prepared.videos), len(comments_raw), len(prepared.comments),
            prepared.channels["_channel_id"].nunique(),
        ],
    }
)
display(summary_df)
"""
    ))

    cells.append(code(
        """
# Step 3.5: Visual quality checks on engineered features
fig, axes = plt.subplots(1, 3, figsize=(16, 4))

sns.histplot(prepared.videos["statistics__viewCount"], bins=40, ax=axes[0], color="#4C9BE8")
axes[0].set_title("View Count Distribution")

sns.histplot(prepared.videos["engagement_rate"], bins=40, ax=axes[1], color="#4CAF50")
axes[1].set_title("Engagement Rate Distribution")

sns.histplot(prepared.videos["days_since_publish"], bins=40, ax=axes[2], color="#FFB74D")
axes[2].set_title("Days Since Publish")

plt.tight_layout()
plt.show()
plt.close()

video_keep_ratio = len(prepared.videos) / max(len(videos_raw), 1)
comment_keep_ratio = len(prepared.comments) / max(len(comments_raw), 1)
print(f"Video keep ratio: {video_keep_ratio:.2%}")
print(f"Comment keep ratio: {comment_keep_ratio:.2%}")
"""
    ))

    cells.append(md(
        """
### Interpretation for Steps 3.4-3.5
The cleaned dataset should show focused, plausible distributions and a reduced noisy sample.
This confirms that downstream modeling uses better-quality inputs.
"""
    ))

    # TF-IDF section
    cells.append(md(
        """
## 4) TF-IDF Text Analysis

### Why this analysis
Influencer matching starts with language fit: does the creator's content context align with campaign intent?

### How it was done
1. Build campaign query text from the brief.
2. Compute TF-IDF vectors and cosine similarity.
3. Apply keyword boost/penalty and normalize the score.

### How to read outputs
Higher `tfidf_similarity` values indicate stronger lexical relevance.
"""
    ))

    cells.append(code(
        """
# Step 4.1: Build TF-IDF relevance explicitly (lecture-style implementation)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

text_demo = prepared.channels.copy()
corpus = text_demo["channel_text"].fillna("").astype(str).tolist()
query = normalize_text(brief.brief_md + " " + " ".join(brief.must_keywords))

vectorizer = TfidfVectorizer(
    max_features=2500,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
)
x = vectorizer.fit_transform(corpus + [query])
raw_sim = cosine_similarity(x[:-1], x[-1])[:, 0]
text_demo["tfidf_similarity_raw"] = raw_sim

must_terms = [normalize_text(k) for k in brief.must_keywords if str(k).strip()]
exclude_terms = [normalize_text(k) for k in brief.exclude_keywords if str(k).strip()]

def keyword_boost(text: str) -> float:
    t = normalize_text(text)
    if not t:
        return 0.0
    hit = sum(1 for w in must_terms if w and w in t)
    miss = sum(1 for w in exclude_terms if w and w in t)
    return (0.08 * hit) - (0.12 * miss)

text_demo["keyword_boost"] = text_demo["channel_text"].fillna("").apply(keyword_boost)
text_demo["tfidf_similarity"] = min_max_scale(text_demo["tfidf_similarity_raw"] + text_demo["keyword_boost"])

print("Rows scored:", len(text_demo))
        """
    ))

    cells.append(code(
        """
# Step 4.2: Review top lexical matches
tfidf_top = text_demo[[
    "channel_title", "tfidf_similarity_raw", "keyword_boost", "tfidf_similarity"
]].sort_values("tfidf_similarity", ascending=False).head(15)

display(tfidf_top)
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 4.2
Top rows are channels with strongest language overlap with campaign keywords and messaging.
Check whether top channels are semantically sensible (not only keyword-heavy).
"""
    ))

    cells.append(code(
        """
# Step 4.3: Compare raw similarity vs adjusted similarity
text_demo["tfidf_delta"] = text_demo["tfidf_similarity"] - text_demo["tfidf_similarity_raw"]
display(
    text_demo[["channel_title", "tfidf_similarity_raw", "keyword_boost", "tfidf_similarity", "tfidf_delta"]]
    .sort_values("tfidf_delta", ascending=False)
    .head(10)
)
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 4.3
Positive delta means the channel benefited from must-have keyword evidence.
Large negative delta often means excluded/noisy keyword contamination.
"""
    ))

    cells.append(code(
        """
# Step 4.4: Visual distribution of final TF-IDF similarity
plt.figure(figsize=(8, 4))
sns.histplot(text_demo["tfidf_similarity"], bins=30, color="#7E57C2")
plt.title("TF-IDF Similarity (Normalized)")
plt.xlabel("tfidf_similarity")
plt.show()
plt.close()

print(f"Mean={float(text_demo['tfidf_similarity'].mean()):.3f}, Median={float(text_demo['tfidf_similarity'].median()):.3f}, P90={float(text_demo['tfidf_similarity'].quantile(0.9)):.3f}")
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 4.4
The upper tail (e.g., top 10-20%) is typically a practical candidate pool for deeper screening.
"""
    ))

    cells.append(code(
        """
# Step 4.5: Top channels by TF-IDF score (bar chart)
top_plot = text_demo.sort_values("tfidf_similarity", ascending=False).head(15).copy()

plt.figure(figsize=(10, 5))
sns.barplot(
    data=top_plot,
    x="tfidf_similarity",
    y="channel_title",
    orient="h",
    color="#7E57C2",
)
plt.title("Top 15 Channels by TF-IDF Similarity")
plt.xlabel("TF-IDF Similarity")
plt.ylabel("Channel")
plt.tight_layout()
plt.show()
plt.close()
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 4.5
This chart provides an immediate shortlist view based only on lexical relevance.
Later sections add network and predictive layers on top of this baseline.
"""
    ))

    # SNA section
    cells.append(md(
        """
## 5) Social Network Analysis (SNA)

### Why this analysis
Language relevance alone ignores network structure.
SNA helps capture influencer position, connectivity, and community diversity.

### How it was done
1. Build a creator graph from shared tags.
2. Compute degree, betweenness proxy, and eigenvector proxy.
3. Detect communities and derive composite `sna_score`.

### How to read outputs
Higher `sna_score` suggests stronger structural influence or bridging potential.
"""
    ))

    cells.append(code(
        """
# Step 5.1: Build graph from shared tags explicitly (lecture-style implementation)
from collections import Counter, defaultdict
from itertools import combinations
import math

def top_tags(tags: list[str], k: int = 40) -> list[str]:
    if not tags:
        return []
    counts = Counter(tags)
    return [t for t, _ in counts.most_common(k)]

tag_map = defaultdict(list)
for _, row in prepared.channels.iterrows():
    cid = str(row["_channel_id"])
    for tag in top_tags(row.get("all_tags", []) or []):
        tag = str(tag).strip().lower()
        if tag:
            tag_map[tag].append(cid)

n_nodes = int(prepared.channels["_channel_id"].astype(str).nunique())
max_tag_channel_ratio = 0.20
max_channels_per_tag = 150
min_shared_tags = 2
max_by_ratio = max(3, int(math.ceil(max(0.01, max_tag_channel_ratio) * max(n_nodes, 1))))
max_allowed_per_tag = min(max_channels_per_tag, max_by_ratio)

edge_counts = Counter()
dropped_too_common = 0
for channels in tag_map.values():
    unique_channels = sorted(set(channels))
    if len(unique_channels) < 2:
        continue
    if len(unique_channels) > max_allowed_per_tag:
        dropped_too_common += 1
        continue
    for a, b in combinations(unique_channels, 2):
        edge_counts[(a, b)] += 1

edges = [(a, b, w) for (a, b), w in edge_counts.items() if w >= min_shared_tags]
edge_df = pd.DataFrame(edges, columns=["source", "target", "weight"])
nodes = prepared.channels["_channel_id"].astype(str).unique().tolist()

graph = {
    "nodes": nodes,
    "edges": edge_df,
    "meta": {
        "n_nodes": len(nodes),
        "n_edges": len(edge_df),
        "min_shared_tags": int(min_shared_tags),
        "max_allowed_per_tag": int(max_allowed_per_tag),
        "dropped_tags_too_common": int(dropped_too_common),
    },
}
print("Graph meta:")
print(graph["meta"])
        """
    ))

    cells.append(md(
        """
### Interpretation for Step 5.1
`n_nodes` and `n_edges` summarize graph density.
If edges are too sparse or too dense, adjust tag filtering thresholds.
"""
    ))

    cells.append(code(
        """
# Step 5.2: Compute SNA metrics explicitly (degree / betweenness proxy / eigenvector proxy)
nodes = graph.get("nodes", [])
edge_df = graph.get("edges", pd.DataFrame(columns=["source", "target", "weight"]))
idx = {n: i for i, n in enumerate(nodes)}
n = len(nodes)
adj = np.zeros((n, n), dtype=float)

if not edge_df.empty:
    for _, r in edge_df.iterrows():
        i = idx.get(str(r["source"]))
        j = idx.get(str(r["target"]))
        if i is None or j is None:
            continue
        w = float(r["weight"])
        if not np.isfinite(w):
            w = 0.0
        adj[i, j] = w
        adj[j, i] = w

adj = np.nan_to_num(adj, nan=0.0, posinf=0.0, neginf=0.0)

# Degree centrality
degree_raw = adj.astype(bool).sum(axis=1).astype(float)
degree = degree_raw / max(n - 1, 1)

# Betweenness proxy: degree * inverse-neighbor-degree tendency
inv_neighbor = np.zeros(n)
for i in range(n):
    neigh = np.where(adj[i] > 0)[0]
    if len(neigh) == 0:
        inv_neighbor[i] = 0.0
    else:
        inv_neighbor[i] = np.mean(1.0 / (degree_raw[neigh] + 1.0))
between_proxy = degree * inv_neighbor

# Eigenvector proxy: normalized weighted strength
strength = np.clip(adj, 0.0, None).sum(axis=1).astype(float)
max_strength = float(np.max(strength)) if len(strength) else 0.0
eigen_proxy = (strength / max_strength) if max_strength > 0 else np.zeros(n)

def label_propagation_communities(nodes: list[str], adj: np.ndarray, random_state: int = 42, max_iter: int = 70) -> dict[str, int]:
    n = len(nodes)
    if n == 0:
        return {}
    labels = np.arange(n, dtype=int)
    rng = np.random.default_rng(seed=random_state)
    order = np.arange(n, dtype=int)

    for _ in range(max_iter):
        rng.shuffle(order)
        changed = 0
        for i in order:
            neigh = np.where(adj[i] > 0)[0]
            if len(neigh) == 0:
                continue
            scores = {}
            for j in neigh:
                lbl = int(labels[j])
                scores[lbl] = scores.get(lbl, 0.0) + float(adj[i, j])

            cur = int(labels[i])
            best_lbl = cur
            best_score = scores.get(cur, -1.0)
            for lbl, score in scores.items():
                if score > best_score + 1e-12 or (abs(score - best_score) <= 1e-12 and lbl < best_lbl):
                    best_lbl = int(lbl)
                    best_score = float(score)
            if best_lbl != cur:
                labels[i] = best_lbl
                changed += 1
        if changed == 0:
            break

    uniq, counts = np.unique(labels, return_counts=True)
    order_idx = np.argsort(-counts)
    remap = {int(uniq[idx]): int(new_id) for new_id, idx in enumerate(order_idx)}
    return {nodes[i]: remap[int(labels[i])] for i in range(n)}

community_map = label_propagation_communities(nodes, adj, random_state=42)

channels_net = prepared.channels.copy()
channels_net["degree_centrality"] = channels_net["_channel_id"].astype(str).map(lambda x: degree[idx[x]] if x in idx else 0.0)
channels_net["betweenness_centrality"] = channels_net["_channel_id"].astype(str).map(lambda x: between_proxy[idx[x]] if x in idx else 0.0)
channels_net["eigenvector_centrality"] = channels_net["_channel_id"].astype(str).map(lambda x: eigen_proxy[idx[x]] if x in idx else 0.0)
channels_net["sna_score_raw"] = (
    0.33 * channels_net["degree_centrality"]
    + 0.34 * channels_net["betweenness_centrality"]
    + 0.33 * channels_net["eigenvector_centrality"]
)
channels_net["sna_score"] = min_max_scale(channels_net["sna_score_raw"])

channels_net["community_id_raw"] = channels_net["_channel_id"].astype(str).map(lambda x: community_map.get(x, -1)).astype(int)
size_map = channels_net["community_id_raw"].value_counts().to_dict()
channels_net["community_size"] = channels_net["community_id_raw"].map(lambda cid: int(size_map.get(int(cid), 1))).astype(int)
channels_net["community_id"] = channels_net["community_id_raw"]
channels_net.loc[channels_net["community_size"] < 3, "community_id"] = -1

valid_ids = sorted([int(x) for x in channels_net["community_id"].unique() if int(x) >= 0])
reindex = {cid: new_id for new_id, cid in enumerate(valid_ids)}
channels_net["community_id"] = channels_net["community_id"].map(lambda x: reindex.get(int(x), -1)).astype(int)

channels_net["graph_degree"] = channels_net["_channel_id"].astype(str).map(lambda x: int(degree_raw[idx[x]]) if x in idx else 0).astype(int)
channels_net["is_isolated"] = channels_net["graph_degree"] == 0

display(
    channels_net[[
        "channel_title", "degree_centrality", "betweenness_centrality",
        "eigenvector_centrality", "sna_score", "community_id"
    ]].sort_values("sna_score", ascending=False).head(15)
)
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 5.2
Degree captures breadth of direct connections.
Betweenness proxy captures bridge-like positioning.
Eigenvector proxy captures weighted connectivity strength.
"""
    ))

    cells.append(code(
        """
# Step 5.3: Community diagnostics table
community_table = (
    channels_net[channels_net["community_id"] >= 0]
    .groupby("community_id", as_index=False)
    .agg(channels=("_channel_id", "nunique"))
    .sort_values("channels", ascending=False)
)
display(community_table.head(20))
"""
    ))

    cells.append(code(
        """
# Step 5.4: Community distribution chart
fig = community_figure(channels_net, top_k=15, include_micro=False)
display(fig)
plt.close(fig)
"""
    ))

    cells.append(code(
        """
# Step 5.5: Centrality relationship plot (degree vs betweenness proxy)
plot_df = channels_net.copy()
plot_df["community_label"] = plot_df["community_id"].astype(str)

plt.figure(figsize=(8.5, 5))
sns.scatterplot(
    data=plot_df,
    x="degree_centrality",
    y="betweenness_centrality",
    hue="community_label",
    alpha=0.7,
    s=60,
    legend=False,
)
plt.title("SNA Diagnostic: Degree vs Betweenness Proxy")
plt.xlabel("Degree Centrality")
plt.ylabel("Betweenness Proxy")
plt.tight_layout()
plt.show()
plt.close()
"""
    ))

    cells.append(md(
        """
### Interpretation for Steps 5.3-5.5
If one community dominates heavily, shortlist diversity controls become more important.
Balanced community spread usually improves campaign resilience.
"""
    ))

    # Semantic section
    cells.append(md(
        """
## 6) Semantic and Tone Enrichment

### Why this analysis
TF-IDF is lexical. This stage adds campaign-tone and semantic alignment context.

### How it was done
1. Pre-rank candidates.
2. Apply semantic alignment and tone matching.
3. Attach red flags and rationale text.

### How to read outputs
Channels with high semantic/tone scores and fewer red flags are better creative-fit candidates.
"""
    ))

    cells.append(code(
        """
# Step 6.1: Recompute text scores explicitly on network-augmented table
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

text_scored = channels_net.copy()
corpus = text_scored["channel_text"].fillna("").astype(str).tolist()
query = normalize_text(brief.brief_md + " " + " ".join(brief.must_keywords))
vectorizer = TfidfVectorizer(max_features=2500, stop_words="english", ngram_range=(1, 2), min_df=2)
x = vectorizer.fit_transform(corpus + [query])
text_scored["tfidf_similarity_raw"] = cosine_similarity(x[:-1], x[-1])[:, 0]

must_terms = [normalize_text(k) for k in brief.must_keywords if str(k).strip()]
exclude_terms = [normalize_text(k) for k in brief.exclude_keywords if str(k).strip()]
def keyword_boost(text: str) -> float:
    t = normalize_text(text)
    if not t:
        return 0.0
    hit = sum(1 for w in must_terms if w and w in t)
    miss = sum(1 for w in exclude_terms if w and w in t)
    return (0.08 * hit) - (0.12 * miss)
text_scored["keyword_boost"] = text_scored["channel_text"].fillna("").apply(keyword_boost)
text_scored["tfidf_similarity"] = min_max_scale(text_scored["tfidf_similarity_raw"] + text_scored["keyword_boost"])

# Initialize optional fields for pre-ranking
pre = text_scored.copy()
pre["semantic_score"] = 0.0
pre["tone_match_score"] = 0.0
pre["red_flags"] = [[] for _ in range(len(pre))]
pre["alignment_rationale"] = ""
pre["ml_potential_score"] = 0.0

pre_rank = create_ranking(pre, use_ml=False, top_n=30)
top_candidates = pre_rank.scored_channels.head(30)

semantic_map = enrich_top_candidates(top_candidates, brief)
merged_semantic = merge_semantic_scores(text_scored, semantic_map)
print("Semantic enrichment done.")
"""
    ))

    cells.append(code(
        """
# Step 6.2: Review top semantic/tone matches
display(
    merged_semantic[[
        "channel_title", "semantic_score", "tone_match_score", "alignment_rationale"
    ]].sort_values("semantic_score", ascending=False).head(15)
)
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 6.2
This table explains *why* a creator is considered aligned, beyond simple keyword overlap.
"""
    ))

    cells.append(code(
        """
# Step 6.3: Aggregate red-flag patterns
flag_rows = []
for _, row in merged_semantic.iterrows():
    flags = row.get("red_flags", [])
    if isinstance(flags, list):
        for f in flags:
            flag_rows.append({"channel_title": row["channel_title"], "flag": str(f)})

flag_df = pd.DataFrame(flag_rows)
if flag_df.empty:
    print("No red flags found.")
else:
    display(flag_df["flag"].value_counts().rename_axis("flag").reset_index(name="count"))
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 6.3
Frequent red-flag types indicate systematic risks in the candidate pool and should influence manual review.
"""
    ))

    # ML section
    cells.append(md(
        """
## 7) ML Benchmarking (5-Fold CV) and SHAP

### Why this analysis
A benchmark suite tests whether predictive signals are robust across model classes.

### How it was done
1. Train multiple regressors (Linear, LASSO, Ridge, CART, RF, LightGBM).
2. Use GroupKFold (5-fold) by channel for fairer validation.
3. Compare RMSE/MAE/R2.
4. Use SHAP for feature-level interpretation where supported.

### How to read outputs
Lower RMSE/MAE and higher R2 indicate better generalization quality.
"""
    ))

    cells.append(code(
        """
# Step 7.1: Manual 5-fold GroupKFold benchmark (lecture-style implementation)
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

manual_df = prepared.videos.copy()
feature_cols = [
    "log_views", "log_likes", "log_comments",
    "days_since_publish", "title_len", "desc_len", "hashtag_count", "tag_count",
]
x_all = manual_df[feature_cols].fillna(0.0).copy()
y_all = manual_df["engagement_target"].to_numpy(dtype=float)
groups = manual_df["_channel_id"].astype(str).to_numpy()

scaler = StandardScaler()
x_scaled = scaler.fit_transform(x_all.to_numpy(dtype=float))
x_scaled = np.nan_to_num(x_scaled, nan=0.0, posinf=0.0, neginf=0.0)
x_all = pd.DataFrame(x_scaled, columns=feature_cols, index=manual_df.index)

models = {
    "LinearRegression": LinearRegression(),
    "LASSO": Lasso(alpha=0.0005, max_iter=2000),
    "Ridge": Ridge(alpha=1.0),
    "CART": DecisionTreeRegressor(max_depth=8, min_samples_leaf=10, random_state=42),
    "RandomForest": RandomForestRegressor(n_estimators=90, max_depth=10, min_samples_leaf=8, random_state=42, n_jobs=1),
}
try:
    from lightgbm import LGBMRegressor
    models["LightGBM"] = LGBMRegressor(
        n_estimators=350, learning_rate=0.05, max_depth=-1, num_leaves=31,
        random_state=42, objective="regression", n_jobs=1
    )
except Exception:
    pass

gkf = GroupKFold(n_splits=5)
manual_rows = []
for model_name, model in models.items():
    fold_metrics = []
    for tr_idx, te_idx in gkf.split(x_all.values, y_all, groups=groups):
        x_train = x_all.iloc[tr_idx]
        x_test = x_all.iloc[te_idx]
        model.fit(x_train, y_all[tr_idx])
        pred = model.predict(x_test)
        mse = mean_squared_error(y_all[te_idx], pred)
        fold_metrics.append({
            "mae": float(mean_absolute_error(y_all[te_idx], pred)),
            "rmse": float(np.sqrt(mse)),
            "r2": float(r2_score(y_all[te_idx], pred)),
        })
    fold_df = pd.DataFrame(fold_metrics)
    manual_rows.append({
        "model": model_name,
        "mae_mean": float(fold_df["mae"].mean()),
        "rmse_mean": float(fold_df["rmse"].mean()),
        "r2_mean": float(fold_df["r2"].mean()),
    })

cv_manual = pd.DataFrame(manual_rows).sort_values("rmse_mean", ascending=True).reset_index(drop=True)
display(cv_manual)
        """
    ))

    cells.append(md(
        """
### Interpretation for Step 7.1
The CV table is the primary model comparison artifact. Focus on stable gains over baseline.
"""
    ))

    cells.append(code(
        """
# Step 7.2: Run project ML suite (for downstream integration + SHAP artifacts)
ml_artifacts = run_ml_suite(
    prepared.videos,
    out_dir=PLOTS_DIR,
    include_models=["LinearRegression", "LASSO", "Ridge", "CART", "RandomForest", "LightGBM"],
)

cv_df = ml_artifacts.cv_results.sort_values(["status", "rmse_mean"], ascending=[True, True])
display(cv_df)

# Print compact model selection summary
print("Best model:", ml_artifacts.best_model_name)
print("ML notes:")
for note in ml_artifacts.notes:
    print("-", note)

valid_cv = cv_df[cv_df["status"] == "ok"].copy()
if not valid_cv.empty:
    best_row = valid_cv.sort_values("rmse_mean", ascending=True).iloc[0]
    print(
        f"Best row -> model={best_row['model']}, RMSE={best_row['rmse_mean']:.4f}, "
        f"MAE={best_row['mae_mean']:.4f}, R2={best_row['r2_mean']:.4f}"
    )
"""
    ))

    cells.append(code(
        """
# Step 7.3: Visual model comparison
if not ml_artifacts.cv_results.empty:
    fig = model_cv_figure(ml_artifacts.cv_results)
    display(fig)
    plt.close(fig)
"""
    ))

    cells.append(code(
        """
# Step 7.3b: Predicted vs actual diagnostics (best model)
pred_actual_df = ml_artifacts.pred_actual.copy()
if pred_actual_df.empty:
    print("No prediction diagnostics available.")
else:
    if {"actual", "predicted"}.issubset(pred_actual_df.columns):
        x_col, y_col = "actual", "predicted"
    elif {"y_true", "y_pred"}.issubset(pred_actual_df.columns):
        x_col, y_col = "y_true", "y_pred"
    else:
        raise ValueError(f"Unexpected pred_actual columns: {pred_actual_df.columns.tolist()}")

    plt.figure(figsize=(6, 6))
    sns.scatterplot(
        data=pred_actual_df,
        x=x_col,
        y=y_col,
        alpha=0.35,
        s=35,
        color="#1E88E5",
    )
    minv = float(min(pred_actual_df[x_col].min(), pred_actual_df[y_col].min()))
    maxv = float(max(pred_actual_df[x_col].max(), pred_actual_df[y_col].max()))
    plt.plot([minv, maxv], [minv, maxv], linestyle="--", color="red", linewidth=1.2)
    plt.title("Predicted vs Actual (Best Model)")
    plt.xlabel("Actual")
    plt.ylabel("Predicted")
    plt.tight_layout()
    plt.show()
    plt.close()
"""
    ))

    cells.append(md(
        """
### Interpretation for Steps 7.3-7.3b
A clear RMSE separation supports model choice confidence.
If models are tightly clustered, simpler models may be preferred.
"""
    ))

    cells.append(code(
        """
# Step 7.4: SHAP diagnostics
if not ml_artifacts.shap_summary.empty:
    print("SHAP top features:")
    display(ml_artifacts.shap_summary.head(15))
else:
    print("SHAP summary unavailable in this runtime.")

print("SHAP plot files:")
for p in ml_artifacts.shap_plot_paths:
    print("-", p)
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 7.4
SHAP identifies which engineered features drive predictions, improving interpretability for business stakeholders.
"""
    ))

    # Ranking section
    cells.append(md(
        """
## 8) Hybrid Ranking and Top-10 Recommendation

### Why this analysis
Decision makers need one shortlist integrating multiple evidence types.

### How it was done
1. Merge ML potential into network-text table.
2. Merge semantic/tone enrichment.
3. Compute final hybrid score with reliability multiplier.
4. Select top-N with diversity-aware logic.

### How to read outputs
`final_score` is the final recommendation score.
Component scores explain channel ranking logic transparently.
"""
    ))

    cells.append(code(
        """
# Step 8.1: Prepare final scoring table
channels_full = merged_semantic.merge(
    ml_artifacts.channel_potential[["_channel_id", "ml_potential_score"]],
    on="_channel_id",
    how="left",
)
channels_full["ml_potential_score"] = channels_full["ml_potential_score"].fillna(0.0)

final_rank = create_ranking(channels_full, use_ml=True, top_n=10)
scored_df = final_rank.scored_channels
top10_df = final_rank.top5.copy()

print("Scored channels:", len(scored_df))
print("Top-N returned:", len(top10_df))
"""
    ))

    cells.append(code(
        """
# Step 8.2: Review top recommendations and component scores
display(
    top10_df[[
        "channel_title", "final_score", "sna_score", "tfidf_similarity", "semantic_score",
        "tone_match_score", "engagement_score", "ml_potential_score",
        "credibility_multiplier", "community_id"
    ]].head(10)
)
"""
    ))

    cells.append(md(
        """
### Interpretation for Step 8.2
Use this table for managerial explanation: each recommendation includes a transparent score breakdown.
"""
    ))

    cells.append(code(
        """
# Step 8.3: Score breakdown visualization for top channels
if not top10_df.empty:
    fig = score_breakdown_figure(top10_df.head(10))
    display(fig)
    plt.close(fig)
"""
    ))

    cells.append(code(
        """
# Step 8.3b: Final score distribution over all scored channels
plt.figure(figsize=(8.5, 4.5))
sns.histplot(scored_df["final_score"], bins=30, color="#0E9F6E")
plt.title("Distribution of Final Recommendation Score")
plt.xlabel("Final Score")
plt.ylabel("Number of Channels")
plt.tight_layout()
plt.show()
plt.close()
"""
    ))

    cells.append(code(
        """
# Step 8.4: Network view of shortlisted ecosystem
if graph and not scored_df.empty:
    fig = network_figure(graph, scored_df, top_nodes=120, min_edge_weight=2)
    display(fig)
    plt.close(fig)
"""
    ))

    cells.append(code(
        """
# Step 8.4b: Community mix in Top-10 shortlist
if not top10_df.empty:
    comm_mix = (
        top10_df.groupby("community_id", as_index=False)
        .agg(channels=("_channel_id", "nunique"))
        .sort_values("channels", ascending=False)
    )
    display(comm_mix)
    plt.figure(figsize=(7.5, 4))
    sns.barplot(data=comm_mix, x="community_id", y="channels", color="#4C9BE8")
    plt.title("Top-10 Community Mix")
    plt.xlabel("Community ID")
    plt.ylabel("Channels in Top-10")
    plt.tight_layout()
    plt.show()
    plt.close()
"""
    ))

    cells.append(code(
        """
# Step 8.5: Concise decision summary for the #1 recommendation
if not top10_df.empty:
    top1 = top10_df.iloc[0]
    print("Top recommended channel:", top1["channel_title"])
    print(f"Final score: {top1['final_score']:.4f}")
    print(
        "Component summary -> "
        f"SNA={top1['sna_score']:.3f}, TFIDF={top1['tfidf_similarity']:.3f}, "
        f"Semantic={top1['semantic_score']:.3f}, Tone={top1['tone_match_score']:.3f}, "
        f"Engagement={top1['engagement_score']:.3f}, ML={top1['ml_potential_score']:.3f}"
    )
"""
    ))

    cells.append(md(
        """
### Interpretation for Steps 8.3-8.5
The visual and text summaries are useful for presentation slides and executive communication.
"""
    ))

    # ROI
    cells.append(md(
        """
## 9) ROI Simulation and Scenario Planning

### Why this analysis
Recommendations should be translated into expected business outcomes.

### How it was done
1. Baseline ROI simulation from budget and funnel assumptions.
2. Scenario analysis (conservative/base/upside).

### How to read outputs
ROAS estimates are assumption-based and should be treated as planning ranges.
"""
    ))

    cells.append(code(
        """
# Step 9.1: Baseline ROI simulation
roi = simulate_roi(
    budget_usd=brief.budget_usd,
    cpm=18.0,
    ctr=0.018,
    cvr=0.03,
    aov=38.0,
)

roi_df = pd.DataFrame([roi.to_dict()]).T
roi_df.columns = ["value"]
display(roi_df)
"""
    ))

    cells.append(code(
        """
# Step 9.2: ROI funnel visualization
fig = roi_funnel_figure(roi.to_dict())
display(fig)
plt.close(fig)
"""
    ))

    cells.append(code(
        """
# Step 9.3: Scenario comparison
scenario_df = pd.DataFrame(
    [
        simulate_roi(brief.budget_usd, cpm=18.0, ctr=0.015, cvr=0.025, aov=38.0).to_dict() | {"scenario": "Conservative"},
        simulate_roi(brief.budget_usd, cpm=18.0, ctr=0.018, cvr=0.030, aov=38.0).to_dict() | {"scenario": "Base"},
        simulate_roi(brief.budget_usd, cpm=18.0, ctr=0.022, cvr=0.035, aov=38.0).to_dict() | {"scenario": "Upside"},
    ]
)[["scenario", "impressions", "clicks", "conversions", "revenue", "roas"]]

display(scenario_df)
"""
    ))

    cells.append(code(
        """
# Step 9.4: Scenario ROAS comparison chart
plt.figure(figsize=(7.5, 4))
sns.barplot(
    data=scenario_df,
    x="scenario",
    y="roas",
    hue="scenario",
    dodge=False,
    palette=["#9CA3AF", "#3B82F6", "#10B981"],
    legend=False,
)
plt.title("ROAS by Scenario")
plt.xlabel("Scenario")
plt.ylabel("ROAS")
plt.tight_layout()
plt.show()
plt.close()
"""
    ))

    cells.append(md(
        """
### Interpretation for Section 9
Scenario ranges help decision-makers understand upside/downside risk before budget allocation.
"""
    ))

    # End-to-end
    cells.append(md(
        """
## 10) End-to-End Pipeline Run and Export Validation

### Why this analysis
After validating individual blocks, we run the full orchestrated pipeline to check reproducibility.

### How it was done
Run `run_pipeline` with ML and benchmark enabled, then verify generated export artifacts.

### How to read outputs
If artifact files are generated and readable, the system is production-demo ready.
"""
    ))

    cells.append(code(
        """
# Step 10.1: Full pipeline execution
result = run_pipeline(
    brand_params=brand_params,
    run_ml=True,
    run_benchmark=True,
)

print("Run timestamp:", result["timestamp_utc"])
print("Best ML model:", result.get("ml_best_model"))
print("Benchmark summary:")
print(json.dumps(result.get("benchmark_summary", {}), indent=2))

print("\\nArtifact paths:")
for k, v in result.get("artifact_paths", {}).items():
    print(f"- {k}: {v}")
"""
    ))

    cells.append(code(
        """
# Step 10.2: Load exported recommendation files
top_path = result["artifact_paths"]["topn_csv"]
scored_path = result["artifact_paths"]["scored_csv"]
memo_path = result["artifact_paths"]["memo_md"]

top_export = pd.read_csv(top_path)
scored_export = pd.read_csv(scored_path)

print("Exported top shape:", top_export.shape)
print("Exported scored shape:", scored_export.shape)
display(top_export.head(10))
"""
    ))

    cells.append(code(
        """
# Step 10.3: Executive memo preview
with open(memo_path, "r", encoding="utf-8") as f:
    memo_preview = f.read()[:1500]
print(memo_preview)
"""
    ))

    cells.append(md(
        """
### Final Interpretation
This notebook demonstrates the full chain from data preparation to explainable recommendations and business-facing ROI planning.
It is suitable for both technical grading and presentation support.
"""
    ))

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.10",
            },
            "colab": {
                "name": OUT_NB.name,
                "provenance": [],
                "include_colab_link": True,
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return nb


def write_py_mirror(nb: dict) -> None:
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""',
        "AI-MCN Course Project Submission (Standalone Colab-style script)",
        "Generated from the submission notebook.",
        '"""',
        "",
    ]

    for cell in nb["cells"]:
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        src = src.rstrip("\n")

        if cell.get("cell_type") == "markdown":
            lines.append("# %% [markdown]")
            for line in src.splitlines():
                lines.append("# " + line)
            lines.append("")
        else:
            lines.append("# %%")
            lines.append(src)
            lines.append("")

    OUT_PY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    nb = build_notebook()
    OUT_NB.write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
    write_py_mirror(nb)
    print(OUT_NB)
    print(OUT_PY)


if __name__ == "__main__":
    main()
