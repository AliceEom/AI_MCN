# -*- coding: utf-8 -*-
"""
AI-MCN Submission (All-in-One Python File)
=========================================

Purpose
-------
This file combines all core project code into a single Python script for course submission.
It includes:
- data preparation and cleaning
- text analysis (including TF-IDF)
- social network analysis (degree, betweenness proxy, eigenvector proxy, communities)
- ML benchmarking (LinearRegression, LASSO, Ridge, CART, RandomForest, LightGBM)
- SHAP explainability
- hybrid ranking and reliability controls
- ROI calculator and simulation
- benchmark, strategy, memo, and export-ready outputs

Main workflow
-------------
1) Load data (combined first, demo fallback; optional Google Drive bootstrap)
2) Clean and aggregate video/comment data into channel-level features
3) Build network graph and compute SNA signals
4) Compute text relevance and semantic/tone enrichment
5) Optionally run ML benchmark and generate ML potential score
6) Produce final recommendation score with reliability and diversity controls
7) Build benchmark/ROI/strategy/memo outputs

Quick run examples
------------------
Fast run:
    python AI_MCN_Submission_AllInOne.py --no-benchmark

Full run with ML:
    python AI_MCN_Submission_AllInOne.py --ml

"""

from __future__ import annotations

# ===== Begin utils.py =====
import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def min_max_scale(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").fillna(0.0)
    vmin = float(s.min())
    vmax = float(s.max())
    if math.isclose(vmin, vmax):
        return pd.Series(np.zeros(len(s), dtype=float), index=s.index)
    return (s - vmin) / (vmax - vmin)


def parse_tags(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    text = str(value).strip()
    if not text:
        return []

    if text.startswith("[") and text.endswith("]"):
        try:
            data = json.loads(text.replace("'", '"'))
            if isinstance(data, list):
                return [str(x).strip().lower() for x in data if str(x).strip()]
        except Exception:
            pass

    # Fallback split for malformed list strings.
    text = re.sub(r"^[\[\(]|[\]\)]$", "", text)
    parts = re.split(r",|\|", text)
    return [p.strip().strip("'\"").lower() for p in parts if p.strip()]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def join_non_empty(parts: Iterable[Any], sep: str = " ") -> str:
    cleaned = [normalize_text(p) for p in parts if p is not None and str(p).strip()]
    return sep.join(cleaned).strip()


def safe_log1p(series: pd.Series) -> pd.Series:
    return np.log1p(pd.to_numeric(series, errors="coerce").clip(lower=0).fillna(0.0))


def build_hash_key(*parts: Any) -> str:
    joined = "||".join([str(p) for p in parts])
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
# ===== End utils.py =====

# ===== Begin config.py =====
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
# Local fallback for development where data files are under project-root /data.
FALLBACK_DATA_DIR = BASE_DIR.parent / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
CACHE_DIR = ARTIFACTS_DIR / "cache"
PLOTS_DIR = ARTIFACTS_DIR / "plots"
MODELS_DIR = ARTIFACTS_DIR / "models"
REPORTS_DIR = ARTIFACTS_DIR / "reports"


def _prefer_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


def resolve_data_paths() -> tuple[Path, Path, Path]:
    videos_csv = _prefer_existing(
        DATA_DIR / "videos_text_ready_combined.csv",
        DATA_DIR / "videos_text_ready_demo.csv",
        FALLBACK_DATA_DIR / "videos_text_ready_combined.csv",
        FALLBACK_DATA_DIR / "videos_text_ready_demo.csv",
    )
    comments_csv = _prefer_existing(
        DATA_DIR / "comments_raw_combined.csv",
        DATA_DIR / "comments_raw_demo.csv",
        FALLBACK_DATA_DIR / "comments_raw_combined.csv",
        FALLBACK_DATA_DIR / "comments_raw_demo.csv",
    )
    master_csv = _prefer_existing(
        DATA_DIR / "master_prd_slim_combined.csv",
        DATA_DIR / "master_prd_slim_demo.csv",
        FALLBACK_DATA_DIR / "master_prd_slim_combined.csv",
        FALLBACK_DATA_DIR / "master_prd_slim_demo.csv",
    )
    return videos_csv, comments_csv, master_csv


VIDEOS_CSV, COMMENTS_CSV, MASTER_CSV = resolve_data_paths()


@dataclass(frozen=True)
class PipelineConfig:
    random_state: int = 42
    tfidf_max_features: int = 1200
    svd_components: int = 50
    ml_max_rows: int = 3000
    top_candidates_for_semantic: int = 30
    top_recommendations: int = 10
    min_shared_tags_edge: int = 2
    max_tag_channel_ratio: float = 0.20
    min_community_size: int = 3


DEFAULT_CONFIG = PipelineConfig()
# ===== End config.py =====

# ===== Begin analysis_categories.py =====
"""
Canonical analysis/modeling taxonomy used in the submission package.

This module groups all implemented methods into large categories so
reviewers can understand the project structure at a glance.
"""

from typing import Any

import pandas as pd


ANALYSIS_CATEGORIES: list[dict[str, Any]] = [
    {
        "category": "Analysis: Class Concepts",
        "method": "Text analysis",
        "implemented": True,
        "class_concept": True,
        "description": "Campaign-language relevance and semantic interpretation from creator text.",
        "primary_files": ["text_scoring.py", "semantic_enrichment.py", "app.py"],
    },
    {
        "category": "Analysis: Class Concepts",
        "method": "TF-IDF",
        "implemented": True,
        "class_concept": True,
        "description": "TF-IDF vectorization + cosine similarity between campaign brief and channel text.",
        "primary_files": ["text_scoring.py"],
    },
    {
        "category": "Analysis: Class Concepts",
        "method": "Sentiment Analysis & Tone enrichment",
        "implemented": True,
        "class_concept": True,
        "description": "Tone enrichment is implemented directly. Explicit standalone sentiment classifier is not used; comment and tone signals provide sentiment-like context.",
        "primary_files": ["semantic_enrichment.py", "channel_details.py", "app.py"],
    },
    {
        "category": "Analysis: Class Concepts",
        "method": "SNA - Social Network Analysis (degree, betweenness proxy, eigenvector proxy)",
        "implemented": True,
        "class_concept": True,
        "description": "Tag-based creator graph, centrality signals, and community detection for influence structure.",
        "primary_files": ["network_scoring.py", "app.py"],
    },
    {
        "category": "Analysis: Class Concepts",
        "method": "ROI Calculator & Simulation",
        "implemented": True,
        "class_concept": False,
        "description": "Scenario-based ROI calculations from budget, CPM, CTR, CVR, and AOV assumptions.",
        "primary_files": ["roi_simulation.py", "app.py"],
    },
    {
        "category": "Additional Category: Data Engineering",
        "method": "Data preparation and cleaning",
        "implemented": True,
        "class_concept": False,
        "description": "Deduplication, type normalization, include/exclude filtering, feature preparation.",
        "primary_files": ["data_prep.py"],
    },
    {
        "category": "Additional Category: Predictive Modeling",
        "method": "Regression benchmark suite",
        "implemented": True,
        "class_concept": False,
        "description": "LinearRegression, LASSO, Ridge, CART, RandomForest, LightGBM with 5-fold GroupKFold CV.",
        "primary_files": ["ml_modeling.py"],
    },
    {
        "category": "Additional Category: Explainability",
        "method": "SHAP model interpretation",
        "implemented": True,
        "class_concept": False,
        "description": "SHAP summary and dependence outputs for tree-based best model.",
        "primary_files": ["ml_modeling.py", "app.py"],
    },
    {
        "category": "Additional Category: Decision Optimization",
        "method": "Hybrid ranking + reliability controls + diversity guardrail",
        "implemented": True,
        "class_concept": False,
        "description": "Weighted final score, credibility multiplier, eligibility constraints, and community-aware Top-N.",
        "primary_files": ["ranking.py", "orchestrator.py", "app.py"],
    },
    {
        "category": "Additional Category: Reporting and Decision Support",
        "method": "Benchmarking, memo generation, strategy generation, export workflow",
        "implemented": True,
        "class_concept": False,
        "description": "Anchor vs benchmark comparison, executive memo, strategy text, and downloadable artifacts.",
        "primary_files": ["orchestrator.py", "content_generation.py", "app.py"],
    },
]


def get_analysis_category_table() -> pd.DataFrame:
    """Return a clean DataFrame for reporting or notebook display."""
    df = pd.DataFrame(ANALYSIS_CATEGORIES).copy()
    df["class_concept"] = df["class_concept"].map(lambda x: "Yes" if bool(x) else "No")
    return df
# ===== End analysis_categories.py =====

# ===== Begin data_bootstrap.py =====
import os
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse


DATA_FILES = {
    "videos": "videos_text_ready_combined.csv",
    "comments": "comments_raw_combined.csv",
    "master": "master_prd_slim_combined.csv",
}

ENV_KEYS = {
    "videos": ("GDRIVE_VIDEOS_FILE_ID", "GDRIVE_VIDEOS_URL"),
    "comments": ("GDRIVE_COMMENTS_FILE_ID", "GDRIVE_COMMENTS_URL"),
    "master": ("GDRIVE_MASTER_FILE_ID", "GDRIVE_MASTER_URL"),
}

FOLDER_ENV_KEYS = ("GDRIVE_FOLDER_ID", "GDRIVE_FOLDER_URL")
DEFAULT_GDRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1fB_c_o3ma2eA2ypHP25eFvQvx5P95FX_?usp=drive_link"


def _extract_file_id(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    # Plain file id
    if re.fullmatch(r"[-\w]{20,}", text):
        return text

    # URL patterns:
    # - https://drive.google.com/file/d/<id>/view
    # - https://drive.google.com/open?id=<id>
    # - https://drive.google.com/uc?id=<id>
    m = re.search(r"/d/([-\w]{20,})", text)
    if m:
        return m.group(1)

    try:
        parsed = urlparse(text)
        qs = parse_qs(parsed.query)
        if "id" in qs and qs["id"]:
            return str(qs["id"][0]).strip()
    except Exception:
        pass

    return ""


def _extract_folder_id(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    if re.fullmatch(r"[-\w]{20,}", text):
        return text

    # URL pattern: https://drive.google.com/drive/folders/<id>
    m = re.search(r"/folders/([-\w]{20,})", text)
    if m:
        return m.group(1)

    try:
        parsed = urlparse(text)
        qs = parse_qs(parsed.query)
        if "id" in qs and qs["id"]:
            return str(qs["id"][0]).strip()
    except Exception:
        pass

    return ""


def _download_gdrive_file(file_id: str, target_path: Path) -> tuple[bool, str]:
    try:
        import gdown  # type: ignore
    except Exception:
        return False, "gdown is not installed"

    url = f"https://drive.google.com/uc?id={file_id}"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        out = gdown.download(url=url, output=str(target_path), quiet=True, fuzzy=True)
    except Exception as e:
        return False, str(e)

    if not out or not target_path.exists() or target_path.stat().st_size <= 0:
        return False, "download produced no file"
    return True, ""


def _download_gdrive_folder(folder_ref: str, output_dir: Path) -> tuple[list[Path], str]:
    try:
        import gdown  # type: ignore
    except Exception:
        return [], "gdown is not installed"

    folder_ref = str(folder_ref or "").strip()
    if not folder_ref:
        return [], "missing folder id/url"
    if folder_ref.startswith("http"):
        folder_url = folder_ref
    else:
        folder_url = f"https://drive.google.com/drive/folders/{folder_ref}"

    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        try:
            out = gdown.download_folder(
                url=folder_url,
                output=str(output_dir),
                quiet=True,
                remaining_ok=True,
            )
        except TypeError:
            out = gdown.download_folder(
                url=folder_url,
                output=str(output_dir),
                quiet=True,
            )
    except Exception as e:
        return [], str(e)

    paths = [Path(p) for p in (out or []) if p]
    if not paths:
        paths = [p for p in output_dir.rglob("*") if p.is_file()]
    if not paths:
        return [], "folder download produced no files"
    return paths, ""


def ensure_full_data_from_gdrive(data_dir: Path, force: bool = False) -> dict[str, object]:
    data_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {
        "complete": True,
        "downloaded": [],
        "skipped_existing": [],
        "missing_env": [],
        "errors": [],
        "folder_used": False,
        "default_folder_used": False,
    }

    pending_folder: list[tuple[str, str, Path]] = []
    for key, filename in DATA_FILES.items():
        target = data_dir / filename
        if target.exists() and target.stat().st_size > 0 and not force:
            report["skipped_existing"].append(filename)
            continue

        env_id_key, env_url_key = ENV_KEYS[key]
        raw = os.getenv(env_id_key, "").strip() or os.getenv(env_url_key, "").strip()
        if not raw:
            pending_folder.append((key, filename, target))
            continue

        file_id = _extract_file_id(raw)
        if not file_id:
            report["errors"].append(f"{filename}: invalid Google Drive id/url")
            continue

        ok, err = _download_gdrive_file(file_id=file_id, target_path=target)
        if ok:
            report["downloaded"].append(filename)
        else:
            report["errors"].append(f"{filename}: {err}")

    if pending_folder:
        folder_raw = os.getenv(FOLDER_ENV_KEYS[0], "").strip() or os.getenv(FOLDER_ENV_KEYS[1], "").strip()
        if not folder_raw:
            folder_raw = DEFAULT_GDRIVE_FOLDER_URL
            report["default_folder_used"] = True
        folder_id = _extract_folder_id(folder_raw)
        if not folder_raw or not folder_id:
            for key, filename, _ in pending_folder:
                env_id_key, env_url_key = ENV_KEYS[key]
                report["missing_env"].append(
                    f"{filename}: set file-specific env ({env_id_key}/{env_url_key}) "
                    f"or folder env ({FOLDER_ENV_KEYS[0]}/{FOLDER_ENV_KEYS[1]})"
                )
        else:
            tmp_dir = None
            try:
                tmp_dir = Path(tempfile.mkdtemp(prefix="gdrive_full_", dir=str(data_dir)))
                files, err = _download_gdrive_folder(folder_raw, tmp_dir)
                if err:
                    report["errors"].append(f"folder download failed: {err}")
                else:
                    report["folder_used"] = True
                    by_name: dict[str, Path] = {}
                    for p in files:
                        name = p.name
                        # Prefer larger file when duplicate names exist.
                        if name not in by_name or p.stat().st_size > by_name[name].stat().st_size:
                            by_name[name] = p
                    for _, filename, target in pending_folder:
                        src = by_name.get(filename)
                        if not src:
                            report["errors"].append(f"{filename}: not found in folder download")
                            continue
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, target)
                        if target.exists() and target.stat().st_size > 0:
                            report["downloaded"].append(filename)
                        else:
                            report["errors"].append(f"{filename}: copy from folder failed")
            except Exception as e:
                report["errors"].append(f"folder download failed: {e}")
            finally:
                if tmp_dir is not None:
                    shutil.rmtree(tmp_dir, ignore_errors=True)

    required = [data_dir / name for name in DATA_FILES.values()]
    report["complete"] = all(p.exists() and p.stat().st_size > 0 for p in required)
    return report
# ===== End data_bootstrap.py =====

# ===== Begin data_prep.py =====
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd



INCLUDE_BEAUTY_KEYWORDS = [
    "beauty",
    "skincare",
    "skin care",
    "makeup",
    "cosmetic",
    "retinol",
    "sunscreen",
    "spf",
    "acne",
    "moistur",
    "cleanser",
    "serum",
    "haircare",
    "fragrance",
    "nail",
    "k-beauty",
]

EXCLUDE_NOISE_KEYWORDS = [
    "official music video",
    "lyrics",
    "trailer",
    "football",
    "cricket",
    "movie",
    "song",
    "dance challenge",
    "reaction",
    "gaming live",
]


@dataclass
class PreparedData:
    videos: pd.DataFrame
    channels: pd.DataFrame
    comments: pd.DataFrame


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    text = normalize_text(text)
    return any(k in text for k in keywords)


def load_data(videos_path: Path, comments_path: Path, master_path: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None]:
    if not videos_path.exists():
        raise FileNotFoundError(f"Videos CSV not found: {videos_path}")
    if not comments_path.exists():
        raise FileNotFoundError(f"Comments CSV not found: {comments_path}")

    videos = pd.read_csv(videos_path, low_memory=False)
    comments = pd.read_csv(comments_path, low_memory=False)
    master = pd.read_csv(master_path, low_memory=False) if master_path and master_path.exists() else None
    return videos, comments, master


def prepare_videos(videos_raw: pd.DataFrame, must_keywords: list[str] | None = None, exclude_keywords: list[str] | None = None) -> pd.DataFrame:
    df = videos_raw.copy()
    df = df.drop_duplicates(subset=["_video_id"], keep="first")

    numeric_cols = [
        "statistics__viewCount",
        "statistics__likeCount",
        "statistics__commentCount",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["publish_dt"] = pd.to_datetime(df["snippet__publishedAt"], errors="coerce", utc=True)
    df["channel_title"] = df["snippet__channelTitle"].fillna("Unknown Channel")
    df["video_title"] = df["snippet__title"].fillna("")
    df["video_description"] = df["snippet__description"].fillna("")

    df["tags_list"] = df["snippet__tags"].apply(parse_tags)
    df["tags_text"] = df["tags_list"].apply(lambda x: " ".join(x))

    df["full_text"] = (
        df["video_title"].astype(str)
        + " "
        + df["video_description"].astype(str)
        + " "
        + df["tags_text"].astype(str)
    ).str.lower()

    include_terms = INCLUDE_BEAUTY_KEYWORDS + (must_keywords or [])
    exclude_terms = EXCLUDE_NOISE_KEYWORDS + (exclude_keywords or [])

    df["beauty_hit"] = df["full_text"].apply(lambda t: _contains_any(t, include_terms))
    df["noise_hit"] = df["full_text"].apply(lambda t: _contains_any(t, exclude_terms))

    # Keep beauty records and remove obvious non-beauty noise.
    df = df[df["beauty_hit"]]
    df = df[~df["noise_hit"]]

    # Conservative guardrails for impossible metric values.
    df = df[df["statistics__viewCount"].fillna(0) > 0]
    df = df[df["statistics__likeCount"].fillna(0) >= 0]
    df = df[df["statistics__commentCount"].fillna(0) >= 0]

    # Engagement target for modeling.
    views = df["statistics__viewCount"].fillna(0)
    likes = df["statistics__likeCount"].fillna(0)
    comments = df["statistics__commentCount"].fillna(0)
    df["engagement_rate"] = (likes + comments + 1.0) / (views + 100.0)
    df["engagement_target"] = np.log1p(df["engagement_rate"])

    # Helper features for ML.
    now_utc = pd.Timestamp.now(tz="UTC")
    df["days_since_publish"] = (now_utc - df["publish_dt"]).dt.days.clip(lower=0).fillna(df["publish_dt"].notna().mean() * 365)
    df["title_len"] = df["video_title"].str.len().fillna(0)
    df["desc_len"] = df["video_description"].str.len().fillna(0)
    df["hashtag_count"] = df["video_title"].str.count("#").fillna(0) + df["video_description"].str.count("#").fillna(0)
    df["tag_count"] = df["tags_list"].apply(len)
    df["log_views"] = safe_log1p(df["statistics__viewCount"])
    df["log_likes"] = safe_log1p(df["statistics__likeCount"])
    df["log_comments"] = safe_log1p(df["statistics__commentCount"])

    return df.reset_index(drop=True)


def prepare_comments(comments_raw: pd.DataFrame) -> pd.DataFrame:
    c = comments_raw.copy()
    c = c.drop_duplicates(subset=["_comment_id"], keep="first")
    c["comment_like_count"] = pd.to_numeric(c["comment_like_count"], errors="coerce").fillna(0)
    c["comment_text"] = c["comment_text"].fillna("")
    c["comment_len"] = c["comment_text"].str.len()
    c["comment_published_at"] = pd.to_datetime(c["comment_published_at"], errors="coerce", utc=True)
    return c


def build_channel_table(videos_df: pd.DataFrame, comments_df: pd.DataFrame | None = None) -> pd.DataFrame:
    grouped = videos_df.groupby(["_channel_id", "channel_title"], dropna=False)

    channel = grouped.agg(
        n_videos=("_video_id", "nunique"),
        median_views=("statistics__viewCount", "median"),
        median_likes=("statistics__likeCount", "median"),
        median_comments=("statistics__commentCount", "median"),
        mean_engagement=("engagement_rate", "mean"),
        latest_publish=("publish_dt", "max"),
    ).reset_index()

    # Representative video for image fallback.
    rep_idx = grouped["statistics__viewCount"].idxmax()
    rep = videos_df.loc[rep_idx, ["_channel_id", "_video_id", "video_title", "tags_text", "video_description"]].copy()
    rep = rep.rename(columns={"_video_id": "representative_video_id"})
    channel = channel.merge(rep, on="_channel_id", how="left")

    tags = grouped["tags_list"].apply(
        lambda x: [t for arr in x for t in arr][:80]
    ).reset_index(name="all_tags")
    channel = channel.merge(tags, on="_channel_id", how="left")

    channel["channel_text"] = channel.apply(
        lambda r: join_non_empty([r.get("video_title", ""), r.get("video_description", ""), " ".join(r.get("all_tags", []))]),
        axis=1,
    )

    now_utc = pd.Timestamp.now(tz="UTC")
    channel["days_since_latest"] = (now_utc - channel["latest_publish"]).dt.days.clip(lower=0).fillna(365)

    if comments_df is not None and not comments_df.empty:
        comm_group = comments_df.groupby("_channel_id", dropna=False).agg(
            comments_n=("_comment_id", "nunique"),
            comments_like_mean=("comment_like_count", "mean"),
            comment_len_median=("comment_len", "median"),
        ).reset_index()
        channel = channel.merge(comm_group, on="_channel_id", how="left")
    else:
        channel["comments_n"] = 0
        channel["comments_like_mean"] = 0.0
        channel["comment_len_median"] = 0.0

    fill_cols = ["comments_n", "comments_like_mean", "comment_len_median"]
    for c in fill_cols:
        channel[c] = channel[c].fillna(0)

    # Resolve merge suffixes for channel title.
    if "channel_title" not in channel.columns:
        if "channel_title_x" in channel.columns:
            channel["channel_title"] = channel["channel_title_x"]
        elif "channel_title_y" in channel.columns:
            channel["channel_title"] = channel["channel_title_y"]
        else:
            channel["channel_title"] = channel["_channel_id"].astype(str)

    drop_cols = [c for c in ["channel_title_x", "channel_title_y"] if c in channel.columns]
    if drop_cols:
        channel = channel.drop(columns=drop_cols)

    return channel


def prepare_all(videos_raw: pd.DataFrame, comments_raw: pd.DataFrame, must_keywords: list[str] | None = None, exclude_keywords: list[str] | None = None) -> PreparedData:
    videos = prepare_videos(videos_raw, must_keywords=must_keywords, exclude_keywords=exclude_keywords)
    comments = prepare_comments(comments_raw)
    channels = build_channel_table(videos, comments)
    return PreparedData(videos=videos, channels=channels, comments=comments)
# ===== End data_prep.py =====

# ===== Begin network_scoring.py =====
from collections import Counter, defaultdict
from itertools import combinations
import math

import numpy as np
import pandas as pd



def _top_tags(tags: list[str], k: int = 40) -> list[str]:
    if not tags:
        return []
    counts = Counter(tags)
    return [t for t, _ in counts.most_common(k)]


def build_channel_graph(
    channel_df: pd.DataFrame,
    min_shared_tags: int = 2,
    max_channels_per_tag: int = 150,
    max_tag_channel_ratio: float = 0.20,
) -> dict:
    tag_map: dict[str, list[str]] = defaultdict(list)

    for _, row in channel_df.iterrows():
        cid = str(row["_channel_id"])
        for tag in _top_tags(row.get("all_tags", []) or []):
            tag = str(tag).strip().lower()
            if tag:
                tag_map[tag].append(cid)

    n_nodes = int(channel_df["_channel_id"].astype(str).nunique())
    max_by_ratio = max(3, int(math.ceil(max(0.01, max_tag_channel_ratio) * max(n_nodes, 1))))
    max_allowed_per_tag = min(max_channels_per_tag, max_by_ratio)

    edge_counts: Counter[tuple[str, str]] = Counter()
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

    edges = [
        (a, b, w)
        for (a, b), w in edge_counts.items()
        if w >= min_shared_tags
    ]

    edge_df = pd.DataFrame(edges, columns=["source", "target", "weight"])

    nodes = channel_df["_channel_id"].astype(str).unique().tolist()

    return {
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


def _build_adjacency(nodes: list[str], edge_df: pd.DataFrame) -> tuple[dict[str, int], np.ndarray]:
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    a = np.zeros((n, n), dtype=float)

    if not edge_df.empty:
        for _, r in edge_df.iterrows():
            i = idx.get(str(r["source"]))
            j = idx.get(str(r["target"]))
            if i is None or j is None:
                continue
            w = float(r["weight"])
            if not np.isfinite(w):
                w = 0.0
            a[i, j] = w
            a[j, i] = w

    a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
    return idx, a


def _connected_components(nodes: list[str], edge_df: pd.DataFrame) -> dict[str, int]:
    parent = {n: n for n in nodes}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    if not edge_df.empty:
        for _, r in edge_df.iterrows():
            s = str(r["source"])
            t = str(r["target"])
            if s in parent and t in parent:
                union(s, t)

    roots = sorted({find(n) for n in nodes})
    root_to_id = {r: i for i, r in enumerate(roots)}
    return {n: root_to_id[find(n)] for n in nodes}


def _label_propagation_communities(
    nodes: list[str],
    adj: np.ndarray,
    random_state: int = 42,
    max_iter: int = 70,
) -> dict[str, int]:
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

            scores: dict[int, float] = {}
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


def _eigenvector_centrality(adj: np.ndarray, max_iter: int = 200, tol: float = 1e-6) -> np.ndarray:
    n = adj.shape[0]
    if n == 0:
        return np.array([])
    strength = np.clip(adj, 0.0, None).sum(axis=1).astype(float)
    max_strength = float(np.max(strength))
    if max_strength <= 0:
        return np.zeros(n)
    return strength / max_strength


def compute_network_scores(channel_df: pd.DataFrame, graph: dict, min_community_size: int = 3, random_state: int = 42) -> pd.DataFrame:
    out = channel_df.copy()
    nodes = graph.get("nodes", [])
    edge_df = graph.get("edges", pd.DataFrame(columns=["source", "target", "weight"]))

    idx, adj = _build_adjacency(nodes, edge_df)
    n = len(nodes)

    # Degree centrality
    degree_raw = adj.astype(bool).sum(axis=1).astype(float)
    degree = degree_raw / max(n - 1, 1)

    # Betweenness approximation using bridge tendency proxy.
    # proxy = degree * inverse neighbor degree
    inv_neighbor = np.zeros(n)
    for i in range(n):
        neigh = np.where(adj[i] > 0)[0]
        if len(neigh) == 0:
            inv_neighbor[i] = 0.0
        else:
            inv_neighbor[i] = np.mean(1.0 / (degree_raw[neigh] + 1.0))
    between_proxy = degree * inv_neighbor

    eigen = _eigenvector_centrality(adj)

    out["degree_centrality"] = out["_channel_id"].astype(str).map(lambda x: degree[idx[x]] if x in idx else 0.0)
    out["betweenness_centrality"] = out["_channel_id"].astype(str).map(lambda x: between_proxy[idx[x]] if x in idx else 0.0)
    out["eigenvector_centrality"] = out["_channel_id"].astype(str).map(lambda x: eigen[idx[x]] if x in idx else 0.0)

    out["sna_score_raw"] = (
        0.33 * out["degree_centrality"]
        + 0.34 * out["betweenness_centrality"]
        + 0.33 * out["eigenvector_centrality"]
    )
    out["sna_score"] = min_max_scale(out["sna_score_raw"])

    comp_map = _label_propagation_communities(nodes, adj, random_state=random_state)
    out["community_id_raw"] = out["_channel_id"].astype(str).map(lambda x: comp_map.get(x, -1)).astype(int)
    size_map = out["community_id_raw"].value_counts().to_dict()
    out["community_size"] = out["community_id_raw"].map(lambda cid: int(size_map.get(int(cid), 1))).astype(int)

    out["community_id"] = out["community_id_raw"]
    out.loc[out["community_size"] < max(1, int(min_community_size)), "community_id"] = -1

    valid_ids = sorted([int(x) for x in out["community_id"].unique() if int(x) >= 0])
    reindex = {cid: new_id for new_id, cid in enumerate(valid_ids)}
    out["community_id"] = out["community_id"].map(lambda x: reindex.get(int(x), -1)).astype(int)

    out["graph_degree"] = out["_channel_id"].astype(str).map(lambda x: int(degree_raw[idx[x]]) if x in idx else 0).astype(int)
    out["is_isolated"] = out["graph_degree"] == 0

    return out
# ===== End network_scoring.py =====

# ===== Begin text_scoring.py =====
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



@dataclass
class BrandBrief:
    brand_name: str
    product_name: str
    category: str
    target_audience: str
    campaign_goal: str
    budget_usd: float
    usp: str
    must_keywords: list[str]
    exclude_keywords: list[str]
    market: str

    @property
    def brief_md(self) -> str:
        return (
            f"Brand: {self.brand_name}\n"
            f"Product: {self.product_name}\n"
            f"Category: {self.category}\n"
            f"Target audience: {self.target_audience}\n"
            f"Campaign goal: {self.campaign_goal}\n"
            f"Market: {self.market}\n"
            f"Core message: {self.usp}\n"
            f"Must keywords: {', '.join(self.must_keywords)}\n"
            f"Excluded keywords: {', '.join(self.exclude_keywords)}"
        )


DEFAULT_BRAND = BrandBrief(
    brand_name="Beauty of Joseon",
    product_name="Relief Sun SPF + Glow Serum",
    category="Skincare",
    target_audience="US Gen Z and Millennial skincare users with sensitivity and acne concerns",
    campaign_goal="Awareness + trial conversion",
    budget_usd=50000,
    usp="Gentle, effective Korean skincare with lightweight textures and strong UV care.",
    must_keywords=["sunscreen", "spf", "sensitive skin", "k-beauty"],
    exclude_keywords=["music", "gaming", "movie"],
    market="United States",
)


def build_brand_brief(params: dict | None = None) -> BrandBrief:
    p = params or {}
    return BrandBrief(
        brand_name=str(p.get("brand_name", DEFAULT_BRAND.brand_name)),
        product_name=str(p.get("product_name", DEFAULT_BRAND.product_name)),
        category=str(p.get("category", DEFAULT_BRAND.category)),
        target_audience=str(p.get("target_audience", DEFAULT_BRAND.target_audience)),
        campaign_goal=str(p.get("campaign_goal", DEFAULT_BRAND.campaign_goal)),
        budget_usd=float(p.get("budget_usd", DEFAULT_BRAND.budget_usd)),
        usp=str(p.get("usp", DEFAULT_BRAND.usp)),
        must_keywords=list(p.get("must_keywords", DEFAULT_BRAND.must_keywords)),
        exclude_keywords=list(p.get("exclude_keywords", DEFAULT_BRAND.exclude_keywords)),
        market=str(p.get("market", DEFAULT_BRAND.market)),
    )


def compute_text_scores(channel_df: pd.DataFrame, brief: BrandBrief) -> pd.DataFrame:
    out = channel_df.copy()

    corpus = out["channel_text"].fillna("").astype(str).tolist()
    query = normalize_text(brief.brief_md + " " + " ".join(brief.must_keywords))

    vectorizer = TfidfVectorizer(
        max_features=2500,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
    )
    x = vectorizer.fit_transform(corpus + [query])
    sim = cosine_similarity(x[:-1], x[-1])[:, 0]

    out["tfidf_similarity_raw"] = sim

    # Encourage explicit must-keyword overlap.
    must_terms = [normalize_text(k) for k in brief.must_keywords if str(k).strip()]
    ex_terms = [normalize_text(k) for k in brief.exclude_keywords if str(k).strip()]

    def keyword_boost(text: str) -> float:
        t = normalize_text(text)
        if not t:
            return 0.0
        hit = sum(1 for w in must_terms if w and w in t)
        miss = sum(1 for w in ex_terms if w and w in t)
        return (0.08 * hit) - (0.12 * miss)

    out["keyword_boost"] = out["channel_text"].fillna("").apply(keyword_boost)
    out["tfidf_similarity"] = min_max_scale(out["tfidf_similarity_raw"] + out["keyword_boost"])
    return out
# ===== End text_scoring.py =====

# ===== Begin semantic_enrichment.py =====
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



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
# ===== End semantic_enrichment.py =====

# ===== Begin ml_modeling.py =====
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

os.environ.setdefault(
    "MPLCONFIGDIR",
    str((Path(__file__).resolve().parents[1] / "artifacts" / "cache" / "mpl")),
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


try:
    from lightgbm import LGBMRegressor
    LIGHTGBM_AVAILABLE = True
except Exception:
    LIGHTGBM_AVAILABLE = False

try:
    import shap
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False


@dataclass
class MLArtifacts:
    cv_results: pd.DataFrame
    best_model_name: str
    channel_potential: pd.DataFrame
    pred_actual: pd.DataFrame
    shap_summary: pd.DataFrame
    shap_dependence: pd.DataFrame
    model_plot_path: str | None
    pred_plot_path: str | None
    shap_plot_paths: list[str]
    notes: list[str]


def _build_feature_matrix(train_df: pd.DataFrame, test_df: pd.DataFrame, max_features: int, svd_components: int) -> tuple[np.ndarray, np.ndarray, list[str]]:
    numeric_cols = [
        "log_views",
        "log_likes",
        "log_comments",
        "days_since_publish",
        "title_len",
        "desc_len",
        "hashtag_count",
        "tag_count",
    ]

    x_train_num = train_df[numeric_cols].fillna(0.0).to_numpy(dtype=float)
    x_test_num = test_df[numeric_cols].fillna(0.0).to_numpy(dtype=float)

    scaler = StandardScaler()
    x_train_num = scaler.fit_transform(x_train_num)
    x_test_num = scaler.transform(x_test_num)

    x_train = x_train_num
    x_test = x_test_num
    x_train = np.nan_to_num(x_train, nan=0.0, posinf=0.0, neginf=0.0)
    x_test = np.nan_to_num(x_test, nan=0.0, posinf=0.0, neginf=0.0)
    x_train = np.clip(x_train, -1e6, 1e6)
    x_test = np.clip(x_test, -1e6, 1e6)
    feature_names = numeric_cols
    return x_train, x_test, feature_names


def _model_factories(random_state: int) -> list[tuple[str, Callable[[], object], str]]:
    models: list[tuple[str, Callable[[], object], str]] = [
        ("LinearRegression", lambda: LinearRegression(), "linear"),
        ("LASSO", lambda: Lasso(alpha=0.0005, max_iter=2000), "linear"),
        ("Ridge", lambda: Ridge(alpha=1.0, random_state=random_state), "linear"),
        ("CART", lambda: DecisionTreeRegressor(max_depth=8, min_samples_leaf=10, random_state=random_state), "tree"),
        ("RandomForest", lambda: RandomForestRegressor(
            n_estimators=90,
            max_depth=10,
            min_samples_leaf=8,
            random_state=random_state,
            n_jobs=1,
        ), "tree"),
    ]
    if LIGHTGBM_AVAILABLE:
        models.append(("LightGBM", lambda: LGBMRegressor(
            n_estimators=350,
            learning_rate=0.05,
            max_depth=-1,
            num_leaves=31,
            random_state=random_state,
            objective="regression",
            n_jobs=1,
        ), "tree"))
    else:
        models.append(("LightGBM", lambda: None, "unavailable"))
    return models


def _score(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    mse = float(mean_squared_error(y_true, y_pred))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def _plot_cv_results(cv_df: pd.DataFrame, out_dir: Path) -> str | None:
    valid = cv_df[cv_df["status"] == "ok"].copy()
    if valid.empty:
        return None

    valid = valid.sort_values("rmse_mean", ascending=True)
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.bar(valid["model"], valid["rmse_mean"], color="#4C9BE8")
    ax.set_ylabel("CV RMSE")
    ax.set_title("Model Comparison (5-Fold Group CV)")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()

    out_path = out_dir / "model_cv_rmse.png"
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return str(out_path)


def _plot_pred_vs_actual(y_true: np.ndarray, y_pred: np.ndarray, model_name: str, out_dir: Path) -> str:
    fig, ax = plt.subplots(1, 1, figsize=(6.5, 6.0))
    ax.scatter(y_true, y_pred, alpha=0.25, s=12)
    minv = float(min(np.min(y_true), np.min(y_pred)))
    maxv = float(max(np.max(y_true), np.max(y_pred)))
    ax.plot([minv, maxv], [minv, maxv], color="red", linestyle="--", linewidth=1.2)
    ax.set_xlabel("Actual log1p(engagement_rate)")
    ax.set_ylabel("Predicted")
    ax.set_title(f"Predicted vs Actual ({model_name})")
    fig.tight_layout()

    out_path = out_dir / f"pred_vs_actual_{model_name}.png"
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return str(out_path)


def _try_shap(
    model: object,
    x_sample: np.ndarray,
    feature_names: list[str],
    out_dir: Path,
    model_name: str,
) -> tuple[list[str], pd.DataFrame, pd.DataFrame]:
    empty_summary = pd.DataFrame(columns=["feature", "mean_abs_shap"])
    empty_dep = pd.DataFrame(columns=["feature", "feature_value", "shap_value"])
    if not SHAP_AVAILABLE or x_sample.shape[0] == 0:
        return [], empty_summary, empty_dep

    paths: list[str] = []
    summary_df = empty_summary
    dep_df = empty_dep
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(x_sample)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        shap_values = np.asarray(shap_values)
        if shap_values.ndim == 1:
            shap_values = shap_values.reshape(-1, 1)

        n_features = min(shap_values.shape[1], len(feature_names))
        use_names = feature_names[:n_features]
        shap_values = shap_values[:, :n_features]

        abs_mean = np.abs(shap_values).mean(axis=0)
        summary_df = (
            pd.DataFrame({"feature": use_names, "mean_abs_shap": abs_mean})
            .sort_values("mean_abs_shap", ascending=False)
            .reset_index(drop=True)
        )

        plt.figure(figsize=(8.5, 5.2))
        shap.summary_plot(shap_values, x_sample[:, :n_features], feature_names=use_names, show=False)
        out1 = out_dir / f"shap_summary_{model_name}.png"
        plt.tight_layout()
        plt.savefig(out1, dpi=140, bbox_inches="tight")
        plt.close()
        paths.append(str(out1))

        # Dependence plots for top 3 absolute SHAP features.
        top_idx = np.argsort(abs_mean)[::-1][:3]
        dep_rows: list[dict[str, float | str]] = []
        for idx in top_idx:
            plt.figure(figsize=(7.0, 4.5))
            shap.dependence_plot(int(idx), shap_values, x_sample[:, :n_features], feature_names=use_names, show=False)
            out_dep = out_dir / f"shap_dependence_{model_name}_{use_names[int(idx)]}.png"
            plt.tight_layout()
            plt.savefig(out_dep, dpi=140, bbox_inches="tight")
            plt.close()
            paths.append(str(out_dep))
            dep_rows.extend(
                [
                    {
                        "feature": str(use_names[int(idx)]),
                        "feature_value": float(x_sample[i, int(idx)]),
                        "shap_value": float(shap_values[i, int(idx)]),
                    }
                    for i in range(shap_values.shape[0])
                ]
            )
        if dep_rows:
            dep_df = pd.DataFrame(dep_rows)
    except Exception:
        return [], empty_summary, empty_dep

    return paths, summary_df, dep_df


def run_ml_suite(
    videos_df: pd.DataFrame,
    out_dir: Path,
    random_state: int = 42,
    tfidf_max_features: int = 1200,
    svd_components: int = 50,
    max_rows: int = 5000,
    include_models: list[str] | None = None,
) -> MLArtifacts:
    out_dir.mkdir(parents=True, exist_ok=True)

    df = videos_df.copy()
    df["ml_text"] = (
        df["video_title"].fillna("").astype(str)
        + " "
        + df["tags_text"].fillna("").astype(str)
        + " "
        + df["video_description"].fillna("").astype(str)
    )

    target_col = "engagement_target"
    required_cols = [
        "_channel_id",
        target_col,
        "ml_text",
        "log_views",
        "log_likes",
        "log_comments",
        "days_since_publish",
        "title_len",
        "desc_len",
        "hashtag_count",
        "tag_count",
    ]
    df = df.dropna(subset=["_channel_id", target_col])
    df = df[required_cols + ["engagement_rate"]].copy()
    if len(df) > max_rows:
        df = df.sample(max_rows, random_state=random_state)

    y = df[target_col].to_numpy(dtype=float)
    groups = df["_channel_id"].astype(str).to_numpy()

    baseline_pred = np.full_like(y, fill_value=float(np.median(y)))
    baseline_score = _score(y, baseline_pred)

    gkf = GroupKFold(n_splits=5)
    records: list[dict] = []
    oof_store: dict[str, np.ndarray] = {}
    model_meta: dict[str, dict] = {}
    notes: list[str] = []

    model_defs = _model_factories(random_state)
    if include_models:
        requested = {str(m).strip() for m in include_models if str(m).strip()}
        model_defs = [m for m in model_defs if m[0] in requested]
        missing = sorted(requested - {m[0] for m in model_defs})
        if missing:
            notes.append(f"Requested models not recognized: {', '.join(missing)}")
    if not model_defs:
        raise RuntimeError("No ML models selected for training.")

    for model_name, factory, model_type in model_defs:
        if model_type == "unavailable":
            records.append({
                "model": model_name,
                "status": "unavailable",
                "mae_mean": np.nan,
                "mae_std": np.nan,
                "rmse_mean": np.nan,
                "rmse_std": np.nan,
                "r2_mean": np.nan,
                "r2_std": np.nan,
            })
            notes.append("LightGBM is unavailable in this runtime. Install lightgbm to enable it.")
            continue

        try:
            fold_scores = []
            oof_pred = np.zeros(len(df), dtype=float)
            fold_feature_names: list[str] | None = None

            for train_idx, test_idx in gkf.split(df, y, groups):
                train_df = df.iloc[train_idx]
                test_df = df.iloc[test_idx]

                x_train, x_test, feature_names = _build_feature_matrix(
                    train_df=train_df,
                    test_df=test_df,
                    max_features=tfidf_max_features,
                    svd_components=svd_components,
                )
                fold_feature_names = feature_names

                model = factory()
                model.fit(x_train, y[train_idx])
                pred = model.predict(x_test)
                pred = np.nan_to_num(pred, nan=0.0, posinf=0.0, neginf=0.0)
                if not np.isfinite(pred).all():
                    raise ValueError("Non-finite predictions encountered.")
                oof_pred[test_idx] = pred

                fold_scores.append(_score(y[test_idx], pred))

            fold_df = pd.DataFrame(fold_scores)
            records.append({
                "model": model_name,
                "status": "ok",
                "mae_mean": float(fold_df["mae"].mean()),
                "mae_std": float(fold_df["mae"].std()),
                "rmse_mean": float(fold_df["rmse"].mean()),
                "rmse_std": float(fold_df["rmse"].std()),
                "r2_mean": float(fold_df["r2"].mean()),
                "r2_std": float(fold_df["r2"].std()),
            })
            oof_store[model_name] = oof_pred
            model_meta[model_name] = {"type": model_type, "feature_names": fold_feature_names or []}
        except Exception as e:
            records.append({
                "model": model_name,
                "status": "failed",
                "mae_mean": np.nan,
                "mae_std": np.nan,
                "rmse_mean": np.nan,
                "rmse_std": np.nan,
                "r2_mean": np.nan,
                "r2_std": np.nan,
            })
            notes.append(f"{model_name} failed during CV: {e}")
            continue

    cv_df = pd.DataFrame(records)
    cv_df = cv_df.sort_values(["status", "rmse_mean"], ascending=[False, True], na_position="last").reset_index(drop=True)

    valid_df = cv_df[cv_df["status"] == "ok"].copy()
    if valid_df.empty:
        raise RuntimeError("No valid ML model finished training.")

    best_model_name = valid_df.sort_values("rmse_mean").iloc[0]["model"]

    model_plot_path = _plot_cv_results(cv_df, out_dir)
    pred_plot_path = _plot_pred_vs_actual(y, oof_store[best_model_name], best_model_name, out_dir)

    # Fit best model on full data for downstream channel potential score.
    x_full, _, feature_names_full = _build_feature_matrix(
        train_df=df,
        test_df=df,
        max_features=tfidf_max_features,
        svd_components=svd_components,
    )
    best_factory = [f for n, f, _ in _model_factories(random_state) if n == best_model_name][0]
    best_model = best_factory()
    best_model.fit(x_full, y)

    pred_full = best_model.predict(x_full)
    pred_engagement = np.expm1(pred_full)
    pred_engagement = np.clip(pred_engagement, 0, None)

    channel_potential = (
        pd.DataFrame({
            "_channel_id": df["_channel_id"].values,
            "ml_pred_engagement": pred_engagement,
        })
        .groupby("_channel_id", as_index=False)
        .agg(ml_pred_engagement=("ml_pred_engagement", "median"))
    )
    channel_potential["ml_potential_score"] = min_max_scale(channel_potential["ml_pred_engagement"])

    # SHAP only for tree models.
    shap_paths: list[str] = []
    shap_summary_df = pd.DataFrame(columns=["feature", "mean_abs_shap"])
    shap_dependence_df = pd.DataFrame(columns=["feature", "feature_value", "shap_value"])
    if model_meta.get(best_model_name, {}).get("type") == "tree":
        sample_n = min(600, x_full.shape[0])
        rng = np.random.default_rng(seed=random_state)
        idx = rng.choice(np.arange(x_full.shape[0]), size=sample_n, replace=False)
        x_sample = x_full[idx]
        shap_paths, shap_summary_df, shap_dependence_df = _try_shap(
            best_model,
            x_sample,
            feature_names_full,
            out_dir,
            best_model_name,
        )

    # Baseline comparison note.
    best_rmse = float(valid_df.sort_values("rmse_mean").iloc[0]["rmse_mean"])
    baseline_rmse = baseline_score["rmse"]
    gain = (baseline_rmse - best_rmse) / baseline_rmse if baseline_rmse > 0 else 0.0
    notes.append(f"Baseline RMSE={baseline_rmse:.6f}, Best({best_model_name}) RMSE={best_rmse:.6f}, Relative gain={gain:.2%}")

    baseline_row = {
        "model": "BaselineMedian",
        "status": "reference",
        "mae_mean": baseline_score["mae"],
        "mae_std": 0.0,
        "rmse_mean": baseline_score["rmse"],
        "rmse_std": 0.0,
        "r2_mean": baseline_score["r2"],
        "r2_std": 0.0,
    }
    cv_df = pd.concat([cv_df, pd.DataFrame([baseline_row])], ignore_index=True)
    pred_actual_df = pd.DataFrame(
        {
            "actual": y,
            "predicted": oof_store[best_model_name],
        }
    )

    return MLArtifacts(
        cv_results=cv_df,
        best_model_name=best_model_name,
        channel_potential=channel_potential,
        pred_actual=pred_actual_df,
        shap_summary=shap_summary_df,
        shap_dependence=shap_dependence_df,
        model_plot_path=model_plot_path,
        pred_plot_path=pred_plot_path,
        shap_plot_paths=shap_paths,
        notes=notes,
    )
# ===== End ml_modeling.py =====

# ===== Begin ranking.py =====
from dataclasses import dataclass

import numpy as np
import pandas as pd



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
# ===== End ranking.py =====

# ===== Begin roi_simulation.py =====
from dataclasses import dataclass, asdict


@dataclass
class ROISimulation:
    budget_usd: float
    cpm: float
    ctr: float
    cvr: float
    aov: float
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    roas: float
    roas_low: float
    roas_high: float

    def to_dict(self) -> dict:
        return asdict(self)


def simulate_roi(
    budget_usd: float,
    cpm: float = 18.0,
    ctr: float = 0.018,
    cvr: float = 0.03,
    aov: float = 38.0,
) -> ROISimulation:
    budget = max(float(budget_usd), 0.0)
    cpm = max(float(cpm), 0.01)
    ctr = max(float(ctr), 0.0)
    cvr = max(float(cvr), 0.0)
    aov = max(float(aov), 0.0)

    impressions = int((budget / cpm) * 1000)
    clicks = int(impressions * ctr)
    conversions = int(clicks * cvr)
    revenue = conversions * aov
    roas = revenue / budget if budget > 0 else 0.0

    return ROISimulation(
        budget_usd=budget,
        cpm=cpm,
        ctr=ctr,
        cvr=cvr,
        aov=aov,
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        revenue=revenue,
        roas=roas,
        roas_low=roas * 0.7,
        roas_high=roas * 1.3,
    )
# ===== End roi_simulation.py =====

# ===== Begin channel_details.py =====
from collections import Counter

import pandas as pd


def _series(df: pd.DataFrame, col: str, default: object = "") -> pd.Series:
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df), index=df.index)


def _clean_text(value: object, max_len: int = 180) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split()).strip()
    if not text or text.lower() == "nan":
        return ""
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text


def _fmt_date(value: object) -> str:
    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        return "N/A"
    return dt.strftime("%Y-%m-%d")


def _to_tags(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip().lower() for x in value if str(x).strip()]
    text = _clean_text(value, max_len=1200).strip("[]")
    if not text:
        return []
    parts = text.replace("|", ",").split(",")
    out = [p.strip().strip("'\"").lower() for p in parts]
    return [x for x in out if x]


def _pick_non_empty_longest(series: pd.Series) -> str:
    values = [_clean_text(v, max_len=400) for v in series.tolist()]
    values = [v for v in values if v]
    if not values:
        return ""
    return max(values, key=len)


def _build_video_details(videos_df: pd.DataFrame, recent_video_n: int) -> pd.DataFrame:
    if videos_df.empty:
        return pd.DataFrame(columns=["_channel_id"])

    v = videos_df.copy()
    v["_channel_id"] = v["_channel_id"].astype(str)
    if "video_title" in v.columns:
        v["video_title"] = _series(v, "video_title").fillna("")
    else:
        v["video_title"] = _series(v, "snippet__title").fillna("")

    if "video_description" in v.columns:
        v["video_description"] = _series(v, "video_description").fillna("")
    else:
        v["video_description"] = _series(v, "snippet__description").fillna("")

    if "publish_dt" in v.columns:
        v["publish_dt"] = pd.to_datetime(_series(v, "publish_dt"), errors="coerce", utc=True)
    else:
        v["publish_dt"] = pd.to_datetime(_series(v, "snippet__publishedAt"), errors="coerce", utc=True)

    v["statistics__viewCount"] = pd.to_numeric(_series(v, "statistics__viewCount", 0), errors="coerce").fillna(0)
    if "tags_list" not in v.columns:
        v["tags_list"] = _series(v, "snippet__tags").apply(_to_tags)
    else:
        v["tags_list"] = v["tags_list"].apply(_to_tags)

    records: list[dict[str, object]] = []
    for channel_id, group in v.groupby("_channel_id", dropna=False, sort=False):
        g = group.sort_values("publish_dt", ascending=False, na_position="last")
        recent = g.head(max(1, int(recent_video_n)))

        recent_titles: list[str] = []
        recent_urls: list[str] = []
        for _, row in recent.iterrows():
            title = _clean_text(row.get("video_title"), max_len=120) or "Untitled"
            dt = _fmt_date(row.get("publish_dt"))
            views = int(pd.to_numeric(row.get("statistics__viewCount"), errors="coerce") or 0)
            recent_titles.append(f"{dt} | {title} ({views:,} views)")
            vid = str(row.get("_video_id", "")).strip()
            if vid and vid.lower() != "nan":
                recent_urls.append(f"https://www.youtube.com/watch?v={vid}")

        best = g.sort_values("statistics__viewCount", ascending=False).head(1)
        best_title = ""
        best_views = 0
        best_url = ""
        if not best.empty:
            r0 = best.iloc[0]
            best_title = _clean_text(r0.get("video_title"), max_len=140)
            best_views = int(pd.to_numeric(r0.get("statistics__viewCount"), errors="coerce") or 0)
            best_vid = str(r0.get("_video_id", "")).strip()
            if best_vid and best_vid.lower() != "nan":
                best_url = f"https://www.youtube.com/watch?v={best_vid}"

        desc = _pick_non_empty_longest(g.head(8)["video_description"])
        tag_counter: Counter[str] = Counter()
        for tags in g["tags_list"].tolist():
            for tag in tags:
                if tag:
                    tag_counter[tag] += 1
        tag_summary = ", ".join([t for t, _ in tag_counter.most_common(10)])

        records.append(
            {
                "_channel_id": str(channel_id),
                "channel_profile_text": desc,
                "channel_keyword_summary": tag_summary,
                "recent_video_titles": recent_titles,
                "recent_video_urls": recent_urls,
                "best_video_title": best_title,
                "best_video_views": best_views,
                "best_video_url": best_url,
            }
        )

    return pd.DataFrame(records)


def _build_comment_details(comments_df: pd.DataFrame, recent_comment_n: int) -> pd.DataFrame:
    if comments_df.empty:
        return pd.DataFrame(columns=["_channel_id"])

    c = comments_df.copy()
    c["_channel_id"] = c["_channel_id"].astype(str)
    c["comment_text"] = _series(c, "comment_text").fillna("")
    c["comment_author"] = _series(c, "comment_author", "Viewer").fillna("Viewer")
    c["comment_like_count"] = pd.to_numeric(_series(c, "comment_like_count", 0), errors="coerce").fillna(0)
    c["comment_dt"] = pd.to_datetime(_series(c, "comment_published_at"), errors="coerce", utc=True)

    records: list[dict[str, object]] = []
    for channel_id, group in c.groupby("_channel_id", dropna=False, sort=False):
        g = group.sort_values("comment_dt", ascending=False, na_position="last")
        recent = g.head(max(1, int(recent_comment_n)))

        recent_comments: list[str] = []
        for _, row in recent.iterrows():
            dt = _fmt_date(row.get("comment_dt"))
            author = _clean_text(row.get("comment_author"), max_len=40) or "Viewer"
            text = _clean_text(row.get("comment_text"), max_len=160)
            if text:
                recent_comments.append(f"{dt} | {author}: {text}")

        top = g.sort_values(["comment_like_count", "comment_dt"], ascending=[False, False]).head(1)
        top_liked_comment = ""
        if not top.empty:
            r0 = top.iloc[0]
            top_likes = int(pd.to_numeric(r0.get("comment_like_count"), errors="coerce") or 0)
            top_author = _clean_text(r0.get("comment_author"), max_len=40) or "Viewer"
            top_text = _clean_text(r0.get("comment_text"), max_len=180)
            if top_text:
                top_liked_comment = f"{top_author}: {top_text} (likes {top_likes})"

        records.append(
            {
                "_channel_id": str(channel_id),
                "recent_comments": recent_comments,
                "top_liked_comment": top_liked_comment,
                "comment_samples_n": int(len(g)),
            }
        )

    return pd.DataFrame(records)


def _build_master_stats(master_df: pd.DataFrame | None) -> pd.DataFrame:
    if master_df is None or master_df.empty or "_channel_id" not in master_df.columns:
        return pd.DataFrame(columns=["_channel_id"])

    m = master_df.copy()
    m["_channel_id"] = m["_channel_id"].astype(str)

    m["statistics__subscriberCount"] = pd.to_numeric(_series(m, "statistics__subscriberCount"), errors="coerce")
    m["statistics__videoCount"] = pd.to_numeric(_series(m, "statistics__videoCount"), errors="coerce")
    m["brandingSettings__channel__keywords"] = _series(m, "brandingSettings__channel__keywords").fillna("")

    stats = (
        m.groupby("_channel_id", dropna=False)
        .agg(
            est_subscribers=("statistics__subscriberCount", "max"),
            est_video_count=("statistics__videoCount", "max"),
            channel_brand_keywords=("brandingSettings__channel__keywords", _pick_non_empty_longest),
        )
        .reset_index()
    )

    stats["est_subscribers"] = stats["est_subscribers"].fillna(0)
    stats["est_video_count"] = stats["est_video_count"].fillna(0)
    stats["channel_brand_keywords"] = stats["channel_brand_keywords"].fillna("")
    return stats


def build_channel_detail_table(
    videos_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    master_df: pd.DataFrame | None = None,
    recent_video_n: int = 3,
    recent_comment_n: int = 3,
) -> pd.DataFrame:
    base = _build_video_details(videos_df, recent_video_n=recent_video_n)
    if base.empty:
        return base

    comment = _build_comment_details(comments_df, recent_comment_n=recent_comment_n)
    master = _build_master_stats(master_df)

    out = base.merge(comment, on="_channel_id", how="left")
    out = out.merge(master, on="_channel_id", how="left")

    if "channel_brand_keywords" in out.columns:
        out["channel_keyword_summary"] = out.apply(
            lambda r: r["channel_keyword_summary"]
            if str(r.get("channel_keyword_summary", "")).strip()
            else str(r.get("channel_brand_keywords", "")).strip(),
            axis=1,
        )

    list_cols = ["recent_video_titles", "recent_video_urls", "recent_comments"]
    for col in list_cols:
        if col not in out.columns:
            out[col] = [[] for _ in range(len(out))]
        else:
            out[col] = out[col].apply(lambda x: x if isinstance(x, list) else [])

    for col in ["top_liked_comment", "channel_profile_text", "channel_keyword_summary", "best_video_title", "best_video_url"]:
        if col not in out.columns:
            out[col] = ""
        else:
            out[col] = out[col].fillna("")

    for col in ["best_video_views", "comment_samples_n", "est_subscribers", "est_video_count"]:
        if col not in out.columns:
            out[col] = 0
        else:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)

    drop_cols = [c for c in ["channel_brand_keywords"] if c in out.columns]
    if drop_cols:
        out = out.drop(columns=drop_cols)

    return out
# ===== End channel_details.py =====

# ===== Begin channel_media.py =====
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests



def _fetch_channel_thumbnails(channel_ids: list[str], api_key: str) -> dict[str, str]:
    result: dict[str, str] = {}
    if not channel_ids:
        return result

    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i : i + 50]
        params = {
            "part": "snippet",
            "id": ",".join(batch),
            "key": api_key,
            "maxResults": 50,
        }
        try:
            resp = requests.get("https://www.googleapis.com/youtube/v3/channels", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("items", []):
                cid = item.get("id")
                thumb = (
                    item.get("snippet", {})
                    .get("thumbnails", {})
                    .get("high", {})
                    .get("url")
                )
                if cid and thumb:
                    result[cid] = thumb
        except Exception:
            continue

    return result


def build_channel_media(top_df: pd.DataFrame, cache_dir: Path) -> dict[str, dict[str, str]]:
    ensure_dir(cache_dir)
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()

    channel_ids = top_df["_channel_id"].astype(str).tolist()
    cache_key = build_hash_key("channel_media", *channel_ids)
    cache_file = cache_dir / f"channel_media_{cache_key}.json"

    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    media: dict[str, dict[str, str]] = {}
    api_imgs: dict[str, str] = {}

    if api_key:
        api_imgs = _fetch_channel_thumbnails(channel_ids, api_key)

    for _, row in top_df.iterrows():
        cid = str(row["_channel_id"])
        video_id = str(row.get("representative_video_id", ""))
        img = api_imgs.get(cid)
        if not img and video_id and video_id != "nan":
            img = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

        media[cid] = {
            "image_url": img or "",
            "channel_url": f"https://www.youtube.com/channel/{cid}",
            "video_url": f"https://www.youtube.com/watch?v={video_id}" if video_id and video_id != "nan" else "",
        }

    cache_file.write_text(json.dumps(media, ensure_ascii=False, indent=2), encoding="utf-8")
    return media
# ===== End channel_media.py =====

# ===== Begin content_generation.py =====
import json
import os
from pathlib import Path

import pandas as pd


try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False


def _fallback_strategy(channel_row: pd.Series, brief: BrandBrief) -> str:
    channel_name = channel_row.get("channel_title", "Creator")
    product = brief.product_name
    audience = brief.target_audience

    return f"""
## Concept 1: Daily Routine Integration
**Format:** Tutorial integration
**Messaging Angle:** Show where {product} fits naturally in a daily routine for {audience}.
**Tone:** Educational + authentic
**Ad Copy:**
1. "I added this step because it is easy to use and lightweight on busy mornings."
2. "If your skin gets irritated easily, this is the texture and finish you should test first."
**Posting Window:** Weekday evening (7-9 PM local audience time)

---

## Concept 2: Results-Focused Comparison
**Format:** Before/after style review
**Messaging Angle:** Compare old routine versus routine with {product} and discuss practical outcomes.
**Tone:** Honest review
**Ad Copy:**
1. "I tested this for two weeks and here is exactly what changed for me."
2. "This is who I think should try it and who should probably skip it."
**Posting Window:** Sunday afternoon (1-4 PM)

---

## Concept 3: Audience Q&A Conversion Hook
**Format:** Community Q&A + short clips
**Messaging Angle:** Answer top follower questions and close with a limited-time CTA.
**Tone:** Conversational
**Ad Copy:**
1. "You asked whether this works for sensitive skin, so here is my real take."
2. "Use my link if you want to test the same combo I used in this routine."
**Posting Window:** Friday evening + next-day short-form recap

---

**Generated for:** {channel_name}
""".strip()


def _maybe_openai_strategy(channel_row: pd.Series, brief: BrandBrief) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or not OPENAI_AVAILABLE:
        return None

    try:
        client = OpenAI(api_key=api_key)
        prompt = f"""
Brand brief:
{brief.brief_md}

Channel profile:
- Channel: {channel_row.get('channel_title', 'Unknown')}
- Mean engagement: {channel_row.get('mean_engagement', 0):.4f}
- Community: {channel_row.get('community_id', -1)}
- Top tags: {', '.join((channel_row.get('all_tags', []) or [])[:12])}

Generate exactly 3 sponsorship concepts in Markdown.
For each concept include: title, format, messaging angle, tone, 2 ad copy lines, posting window.
Write concise, specific, and fully in English.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are an expert influencer marketing strategist."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def generate_channel_strategy(channel_row: pd.Series, brief: BrandBrief, cache_dir: Path) -> str:
    ensure_dir(cache_dir)
    channel_id = str(channel_row.get("_channel_id", "unknown"))
    key = build_hash_key(brief.brand_name, brief.product_name, channel_id)
    cache_path = cache_dir / f"strategy_{key}.md"

    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    text = _maybe_openai_strategy(channel_row, brief)
    if not text:
        text = _fallback_strategy(channel_row, brief)

    cache_path.write_text(text, encoding="utf-8")
    return text


def generate_strategies(top_df: pd.DataFrame, brief: BrandBrief, cache_dir: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for _, row in top_df.iterrows():
        cid = str(row["_channel_id"])
        result[cid] = generate_channel_strategy(row, brief, cache_dir)
    return result


def generate_executive_memo(top_df: pd.DataFrame, roi_result: dict, brief: BrandBrief, strategy_texts: dict[str, str]) -> str:
    lines = []
    lines.append("# Brand Partnership Recommendation Memo")
    lines.append(f"**Brand:** {brief.brand_name}")
    lines.append(f"**Product:** {brief.product_name}")
    lines.append(f"**Budget:** ${brief.budget_usd:,.0f}")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append(
        f"The model identified {len(top_df)} high-fit creators for {brief.brand_name}. "
        f"The expected ROAS under base assumptions is {roi_result.get('roas', 0):.2f}x "
        f"(range: {roi_result.get('roas_low', 0):.2f}x-{roi_result.get('roas_high', 0):.2f}x)."
    )
    lines.append("")
    lines.append("## Priority Recommendation")
    if not top_df.empty:
        r0 = top_df.iloc[0]
        lines.append(
            f"Prioritize **{r0.get('channel_title', 'Top Creator')}** first. "
            f"Final score={r0.get('final_score', 0):.3f}, SNA={r0.get('sna_score', 0):.3f}, "
            f"Text fit={r0.get('tfidf_similarity', 0):.3f}, Engagement={r0.get('engagement_score', 0):.3f}."
        )
    lines.append("")
    lines.append("## Campaign Structure (4 Weeks)")
    lines.append("1. Week 1: Awareness launch with creator #1 and #2.")
    lines.append("2. Week 2: Education-focused tutorials and Q&A clips.")
    lines.append("3. Week 3: Product proof and comparison content.")
    lines.append("4. Week 4: Conversion push with promo CTA and recap content.")
    lines.append("")
    lines.append("## Risk Flags")
    flags = []
    for _, row in top_df.iterrows():
        for f in row.get("red_flags", []) or []:
            flags.append(f"- {row.get('channel_title', 'Creator')}: {f}")
    if flags:
        lines.extend(flags)
    else:
        lines.append("- No material risk flags identified in the selected Top 5.")
    lines.append("")
    lines.append("## Next Steps")
    lines.append("1. Confirm creator availability and rate cards.")
    lines.append("2. Finalize creative brief and legal requirements.")
    lines.append("3. Launch a 2-week test and monitor CTR/CVR/ROAS.")
    return "\n".join(lines)
# ===== End content_generation.py =====

# ===== Begin orchestrator.py =====
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd



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

    # If Google Drive ids/urls are provided via env, bootstrap full data automatically.
    ensure_full_data_from_gdrive(DATA_DIR)
    videos_csv, comments_csv, master_csv = resolve_data_paths()
    videos_raw, comments_raw, master_raw = load_data(videos_csv, comments_csv, master_csv)

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

    detail_df = build_channel_detail_table(prepared.videos, prepared.comments, master_df=master_raw)
    if not detail_df.empty:
        scored_df = scored_df.merge(detail_df, on="_channel_id", how="left")
        top5 = top5.merge(detail_df, on="_channel_id", how="left")

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
        "data_sources": {
            "videos_csv": str(videos_csv),
            "comments_csv": str(comments_csv),
            "master_csv": str(master_csv),
        },
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
        "ml_pred_actual": ml_artifacts.pred_actual if ml_artifacts else pd.DataFrame(),
        "ml_shap_summary": ml_artifacts.shap_summary if ml_artifacts else pd.DataFrame(),
        "ml_shap_dependence": ml_artifacts.shap_dependence if ml_artifacts else pd.DataFrame(),
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
# ===== End orchestrator.py =====



# ---------------------------------------------------------------------------
# Submission CLI entry point
# ---------------------------------------------------------------------------
def _submission_parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Run AI-MCN all-in-one submission pipeline.")
    parser.add_argument("--ml", action="store_true", help="Enable ML benchmark block.")
    parser.add_argument(
        "--ml-models",
        type=str,
        default="",
        help="Comma-separated model names (used when --ml is enabled).",
    )
    parser.add_argument("--no-benchmark", action="store_true", help="Skip benchmark run.")
    return parser.parse_args()


def _submission_main() -> None:
    import json
    from pathlib import Path

    args = _submission_parse_args()
    ml_models = [x.strip() for x in args.ml_models.split(",") if x.strip()] if args.ml_models else None

    result = run_pipeline(
        run_ml=args.ml,
        run_benchmark=not args.no_benchmark,
        ml_models=ml_models,
    )

    topn = result.get("top5_df", None)
    top_channels = []
    if topn is not None and hasattr(topn, "columns") and "channel_title" in topn.columns:
        top_channels = topn["channel_title"].tolist()

    data_sources = result.get("data_sources", {})
    summary = {
        "timestamp_utc": result.get("timestamp_utc"),
        "data_sources": {
            "videos_csv": str(Path(str(data_sources.get("videos_csv", ""))).name),
            "comments_csv": str(Path(str(data_sources.get("comments_csv", ""))).name),
            "master_csv": str(Path(str(data_sources.get("master_csv", ""))).name),
        },
        "top_channels": top_channels,
        "best_model": result.get("ml_best_model", "N/A"),
        "benchmark": result.get("benchmark_summary", {}),
        "artifacts": result.get("artifact_paths", {}),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _submission_main()
