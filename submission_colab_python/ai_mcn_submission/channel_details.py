from __future__ import annotations

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
