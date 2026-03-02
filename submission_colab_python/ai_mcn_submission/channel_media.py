from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .utils import build_hash_key, ensure_dir


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
