---
name: SKILL_ContentStrategyAgent
description: >
  Generates 3 tailored YouTube sponsorship content concepts for a single
  influencer-brand pairing. Use this subagent at Step 6B of the AI-MCN
  orchestrator, dispatched as 5 parallel async tasks via asyncio.gather — one
  per Top 5 influencer — after top5_df is finalized and ROI simulation completes.
  Each instance receives one influencer row (including semantic scores and
  alignment_rationale from the Channel Enrichment Agent) plus the full brand_params
  dict. Returns a Markdown-formatted string with exactly 3 numbered sponsorship
  concepts, each containing a title, format, messaging angle, tone, two sample
  ad copy lines, and a posting window recommendation. Output is cached per channel
  and rendered directly in the Streamlit dashboard via st.markdown(). Always run
  this agent after both the Brand Intelligence Agent (Step 4B) and Channel
  Enrichment Agents (Step 5F) so that alignment_rationale and tone_match_score
  are available to inject into the prompt — without them the output is generic.
---

# Content Strategy Agent

## Role in Pipeline

```
Step 5F — Channel Enrichment Agents produce alignment_rationale + tone_match_score
Step 6A — ROI simulation completes (sequential)
Step 6B — [THIS AGENT × 5, parallel] content strategies generated for Top 5
Step 7G — strategy_texts dict rendered in Streamlit: st.markdown(strategy_text)
           st.download_button() exports per-influencer strategy brief
Step 7I — Executive Synthesis Agent receives one-sentence summaries from these outputs
```

**Execution:** Async parallel · 5 concurrent calls · `llama-3.3-70b-versatile` (Groq) · max_tokens=1500

**Why parallel:** Sequential at ~7s per call = 35s of UI blocking. `asyncio.gather`
across all 5 collapses this to ~7–10s total. Each call is fully stateless — one
influencer, one brand brief, zero shared state.

**Why the two-stage dependency matters:** Content Strategy Agents receive
`alignment_rationale` and `tone_match_score` from the Channel Enrichment Agents.
Without those fields, the model has only raw metadata (subscriber count, tags) and
produces generic sponsorship templates. With them, it generates concepts anchored to
how the enrichment analysis described this channel's specific brand voice fit.

---

## Input Contract

**Per-call inputs (one influencer, one brand):**

```python
row = {
    "channel_id":           str,
    "title":                str,
    "subscriber_count":     int,
    "avg_views":            float,
    "tags":                 list[str],    # top 10 used
    "community_id":         int,
    "confidence_score_final": float,      # 5-signal composite from Step 5F
    "engagement_ratio":     float,
    "upload_frequency":     str | float,  # e.g. "3 videos/week" or numeric
    "alignment_rationale":  str,          # from Channel Enrichment Agent
    "tone_match_score":     float,        # from Channel Enrichment Agent
}

brand_params = {
    "brief_md": str,   # full Markdown brand brief
    # enrichment subdict used for context but not injected directly
}
```

**Batch input (called from orchestrator):**

```python
top5_df:      pd.DataFrame   # 5-row DataFrame from Step 5D/5F
brand_params: dict           # full brand_params including enrichment
```

---

## Output Contract

**Per-call output:** A Markdown string containing exactly 3 numbered sponsorship
content concepts. Each concept must include all 6 required fields. The model returns
clean Markdown — no JSON, no fences.

**Expected structure:**

```markdown
## Concept 1: [Title]

**Format:** [Dedicated video | Mid-roll | Short-form series | Review | Tutorial | Live]
**Messaging Angle:** [core narrative hook]
**Tone:** [Educational | Humorous | Aspirational | Authentic/raw | etc.]

**Ad Copy:**
1. [sample line 1 in influencer's voice]
2. [sample line 2 in influencer's voice]

**Posting Window:** [specific timing recommendation]

---

## Concept 2: [Title]
...

## Concept 3: [Title]
...
```

**Batch output (from `run_content_strategy_agents`):**

```python
strategy_texts: dict[str, str]   # {channel_id: markdown_string}
```

---

## System Prompt

```
You are a senior influencer marketing strategist at a top-tier MCN agency.
You specialize in YouTube sponsorship campaigns for consumer brands.
Your output must be data-driven, specific to the influencer's actual content style,
and tailored to the brand's audience and product.
Never produce generic advice. Every recommendation must reference specific data
provided in the user prompt.
```

---

## User Prompt Template

```
## Brand Brief
{brief}

## Selected Influencer Profile
- Channel: {title}
- Subscribers: {subscriber_count:,}
- Avg Views: {avg_views:,}
- Top Tags: {tags}
- Community Cluster: {community_id}
- AI-MCN Confidence Score: {confidence_score:.3f}
- Engagement Rate: {engagement_ratio:.2%}
- Upload Frequency: {upload_frequency}
- Alignment Rationale (AI-assessed): {alignment_rationale}
- Tone Match Score: {tone_match_score:.2f}

## Task
Generate exactly 3 sponsorship content concepts for this influencer × brand pairing.
For each concept provide:
1. **Concept Title** — short, punchy name
2. **Format** — (e.g. Dedicated video, Mid-roll integration, Short-form series, Review, Tutorial)
3. **Messaging Angle** — the core narrative hook
4. **Tone** — (e.g. Educational, Humorous, Aspirational, Authentic/raw)
5. **Two sample ad copy lines** — written in the influencer's voice
6. **Suggested posting window** — based on the influencer's upload cadence and audience peak times

Format your response as clean Markdown with clear headers for each concept.
```

**Field mappings:**

| Template variable | Source |
|-------------------|--------|
| `{brief}` | `brand_params["brief_md"]` |
| `{title}` | `row["title"]` |
| `{subscriber_count}` | `int(row["subscriber_count"])` |
| `{avg_views}` | `int(row["avg_views"])` |
| `{tags}` | `", ".join(row["tags"][:10])` |
| `{community_id}` | `row["community_id"]` |
| `{confidence_score}` | `float(row.get("confidence_score_final", row["confidence_score"]))` |
| `{engagement_ratio}` | `float(row["engagement_ratio"])` |
| `{upload_frequency}` | `row.get("upload_frequency", "N/A")` |
| `{alignment_rationale}` | `row.get("alignment_rationale", "N/A")` — from Channel Enrichment Agent |
| `{tone_match_score}` | `float(row.get("tone_match_score", 0))` — from Channel Enrichment Agent |

---

## Implementation

```python
# orchestrator.py
import asyncio, os
from groq import AsyncGroq

CONTENT_STRATEGY_SYSTEM = """
You are a senior influencer marketing strategist at a top-tier MCN agency.
You specialize in YouTube sponsorship campaigns for consumer brands.
Your output must be data-driven, specific to the influencer's actual content style,
and tailored to the brand's audience and product.
Never produce generic advice. Every recommendation must reference specific data
provided in the user prompt.
"""

CONTENT_STRATEGY_PROMPT = """
## Brand Brief
{brief}

## Selected Influencer Profile
- Channel: {title}
- Subscribers: {subscriber_count:,}
- Avg Views: {avg_views:,}
- Top Tags: {tags}
- Community Cluster: {community_id}
- AI-MCN Confidence Score: {confidence_score:.3f}
- Engagement Rate: {engagement_ratio:.2%}
- Upload Frequency: {upload_frequency}
- Alignment Rationale (AI-assessed): {alignment_rationale}
- Tone Match Score: {tone_match_score:.2f}

## Task
Generate exactly 3 sponsorship content concepts for this influencer x brand pairing.
For each concept provide:
1. **Concept Title** — short, punchy name
2. **Format** — (e.g. Dedicated video, Mid-roll integration, Short-form series, Review, Tutorial)
3. **Messaging Angle** — the core narrative hook
4. **Tone** — (e.g. Educational, Humorous, Aspirational, Authentic/raw)
5. **Two sample ad copy lines** — written in the influencer's voice
6. **Suggested posting window** — based on the influencer's upload cadence and audience peak times

Format your response as clean Markdown with clear headers for each concept.
"""

async def _generate_single_strategy(
    client:       AsyncGroq,
    row:          dict,
    brand_params: dict,
) -> tuple[str, str]:
    cache_path = f"cache/{row['channel_id']}_strategy.md"
    os.makedirs("cache", exist_ok=True)

    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return row["channel_id"], f.read()

    try:
        prompt = CONTENT_STRATEGY_PROMPT.format(
            brief               = brand_params["brief_md"],
            title               = row["title"],
            subscriber_count    = int(row.get("subscriber_count", 0)),
            avg_views           = int(row.get("avg_views", 0)),
            tags                = ", ".join(row.get("tags", [])[:10]),
            community_id        = row.get("community_id", "N/A"),
            confidence_score    = float(row.get("confidence_score_final",
                                               row.get("confidence_score", 0))),
            engagement_ratio    = float(row.get("engagement_ratio", 0)),
            upload_frequency    = row.get("upload_frequency", "N/A"),
            alignment_rationale = row.get("alignment_rationale", "N/A"),
            tone_match_score    = float(row.get("tone_match_score", 0)),
        )
        response = await client.chat.completions.create(
            model      = "llama-3.3-70b-versatile",
            max_tokens = 1500,
            messages   = [
                {"role": "system", "content": CONTENT_STRATEGY_SYSTEM},
                {"role": "user",   "content": prompt},
            ],
        )
        text = response.choices[0].message.content
        with open(cache_path, "w") as f:
            f.write(text)
        return row["channel_id"], text

    except Exception as e:
        print(f"[ContentStrategyAgent] {row['channel_id']} failed: {e}")
        fallback = (
            f"# Content Strategy Temporarily Unavailable\n\n"
            f"Could not generate strategy for **{row.get('title', row['channel_id'])}**.\n\n"
            f"Error: `{e}`\n\n"
            f"Re-run this cell or load from cache once the API recovers."
        )
        return row["channel_id"], fallback


async def run_content_strategy_agents(
    top5_df:      pd.DataFrame,
    brand_params: dict,
) -> dict[str, str]:
    """
    Dispatch one content strategy subagent per Top 5 influencer — all in parallel.

    Args:
        top5_df:      5-row DataFrame. Must include alignment_rationale and
                      tone_match_score columns (populated by Channel Enrichment Agents).
        brand_params: Full brand_params dict including brief_md.

    Returns:
        Dict mapping channel_id → Markdown strategy string.
    """
    client  = AsyncGroq()
    tasks   = [
        _generate_single_strategy(client, row.to_dict(), brand_params)
        for _, row in top5_df.iterrows()
    ]
    results = await asyncio.gather(*tasks)
    return {channel_id: text for channel_id, text in results}
```

---

## Orchestrator Integration

```python
# orchestrator.py → run_full_pipeline()

# Step 6B — after top5_df is finalized and ROI simulation completes
strategy_texts = asyncio.run(
    run_content_strategy_agents(top5_df, brand_params)
)

# app.py — Section 7G rendering
selected_channel_id = top5_df[top5_df['title'] == selected_title].iloc[0]['channel_id']
st.markdown(strategy_texts[selected_channel_id])
st.download_button(
    label     = "Download Strategy Brief",
    data      = strategy_texts[selected_channel_id],
    file_name = f"{selected_title.replace(' ', '_')}_strategy.md",
    mime      = "text/markdown",
)

# Step 7I — Executive Synthesis Agent receives one-line summaries
strategy_summaries = "\n".join(
    f"- **{top5_df.loc[i, 'title']}:** "
    f"{strategy_texts.get(row['channel_id'], '')[:200].strip().split(chr(10))[0]}"
    for i, row in top5_df.iterrows()
)
```

---

## Quality Guardrails

After receiving each strategy, verify before caching:

```python
def _validate_strategy(text: str) -> bool:
    """Ensure the response contains exactly 3 concepts with all 6 required fields."""
    required_fields = [
        "Format", "Messaging Angle", "Tone", "Ad Copy", "Posting Window"
    ]
    concept_count = text.count("## Concept")
    if concept_count != 3:
        return False
    for field in required_fields:
        if field not in text:
            return False
    return True
```

If validation fails, log a warning but still cache and return the text — a partial
strategy is better than an error block in the UI.

---

## Bias Mitigation Check

After all 5 strategies are generated, verify community diversity:

```python
# In matching_roi.py — called after run_content_strategy_agents completes
community_counts = top5_df['community_id'].value_counts()
if community_counts.max() > 2:
    # Flag: more than 2 influencers from the same audience cluster
    st.warning(
        "⚠️ Top 5 contains 3+ influencers from the same audience cluster. "
        "Consider adjusting your brand keywords for more diverse reach."
    )
```

---

## Common Failure Modes

| Failure | Symptom | Resolution |
|---------|---------|------------|
| Missing `alignment_rationale` | Generic concepts, no data grounding | Ensure Channel Enrichment Agents ran first (Step 5F) |
| LLM returns fewer than 3 concepts | Validation fails | Log warning, use partial output; do not re-call during demo |
| `max_tokens=1500` hit before Concept 3 | Output truncated mid-sentence | Increase to 2000 if budget allows; or split into 2 calls |
| API rate limit hit on 5th parallel call | One task returns fallback string | Cache the 4 successes; retry the failure separately |
| Cache files from a previous brand brief | Wrong strategies served | Cache key is `{channel_id}_strategy.md` — clear cache when brand changes |

> **Important:** Cache keys for this agent do NOT include the brand brief hash. If the
> brand brief changes between runs, manually delete `cache/*_strategy.md` or the agent
> will serve stale strategies for the new brand.

---

## Demo Pre-generation

**Requires:** `GROQ_API_KEY` in `.env` — free at [console.groq.com](https://console.groq.com). No credit card needed.


```python
# Run once on Friday night against your real data
import asyncio, json, pandas as pd
from orchestrator import run_content_strategy_agents

top5_df    = pd.read_csv("top5_matches.csv")
brand_params = json.load(open("demo_brand_params.json"))

strategies = asyncio.run(run_content_strategy_agents(top5_df, brand_params))
for cid, text in strategies.items():
    print(f"Cached: {cid} ({len(text)} chars)")
```

Saturday demo loads all 5 from `cache/{channel_id}_strategy.md` — no API call,
no latency, no risk.
