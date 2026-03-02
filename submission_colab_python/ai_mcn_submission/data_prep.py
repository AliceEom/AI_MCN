from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .utils import join_non_empty, normalize_text, parse_tags, safe_log1p


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
