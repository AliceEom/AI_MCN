from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

from .text_scoring import BrandBrief
from .utils import build_hash_key, ensure_dir

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
