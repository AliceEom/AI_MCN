from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"

VIDEOS_FULL = DATA / "videos_text_ready_combined.csv"
COMMENTS_FULL = DATA / "comments_raw_combined.csv"
MASTER_FULL = DATA / "master_prd_slim_combined.csv"

VIDEOS_DEMO = DATA / "videos_text_ready_demo.csv"
COMMENTS_DEMO = DATA / "comments_raw_demo.csv"
MASTER_DEMO = DATA / "master_prd_slim_demo.csv"


def build_demo(
    max_channels: int = 260,
    max_videos_per_channel: int = 25,
    max_comments: int = 12000,
    random_state: int = 42,
) -> None:
    if not VIDEOS_FULL.exists() or not COMMENTS_FULL.exists():
        raise FileNotFoundError("Full videos/comments files are required to build demo snapshots.")

    videos = pd.read_csv(VIDEOS_FULL, low_memory=False)
    for c in ["statistics__viewCount", "statistics__likeCount", "statistics__commentCount"]:
        videos[c] = pd.to_numeric(videos[c], errors="coerce").fillna(0)

    videos["publish_dt"] = pd.to_datetime(videos.get("snippet__publishedAt"), errors="coerce", utc=True)

    by_channel = (
        videos.groupby("_channel_id", dropna=False)
        .agg(
            n_videos=("_video_id", "nunique"),
            median_views=("statistics__viewCount", "median"),
            median_likes=("statistics__likeCount", "median"),
        )
        .reset_index()
        .sort_values(["n_videos", "median_views", "median_likes"], ascending=False)
    )

    selected_channels = by_channel.head(max_channels)["_channel_id"].astype(str).tolist()

    v = videos[videos["_channel_id"].astype(str).isin(selected_channels)].copy()
    v = v.sort_values("publish_dt", ascending=False)
    v = v.groupby("_channel_id", dropna=False).head(max_videos_per_channel).copy()
    if len(v) > 12000:
        v = v.sample(n=12000, random_state=random_state)

    v = v.drop(columns=["publish_dt"], errors="ignore")
    v.to_csv(VIDEOS_DEMO, index=False)

    comments = pd.read_csv(COMMENTS_FULL, low_memory=False)
    if "_channel_id" in comments.columns:
        c = comments[comments["_channel_id"].astype(str).isin(selected_channels)].copy()
    else:
        c = comments.copy()

    if len(c) > max_comments:
        c = c.sample(n=max_comments, random_state=random_state)
    c.to_csv(COMMENTS_DEMO, index=False)

    if MASTER_FULL.exists():
        m = pd.read_csv(MASTER_FULL, nrows=4000, low_memory=False)
        m.to_csv(MASTER_DEMO, index=False)

    print(f"Wrote: {VIDEOS_DEMO} ({VIDEOS_DEMO.stat().st_size / (1024*1024):.2f} MB)")
    print(f"Wrote: {COMMENTS_DEMO} ({COMMENTS_DEMO.stat().st_size / (1024*1024):.2f} MB)")
    if MASTER_DEMO.exists():
        print(f"Wrote: {MASTER_DEMO} ({MASTER_DEMO.stat().st_size / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    build_demo()
