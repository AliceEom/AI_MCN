---
name: SKILL_ChannelEnrichmentAgent
description: >
  Scores a single YouTube channel against a brand brief using semantic reasoning.
  Use this subagent at Step 5F of the AI-MCN orchestrator, dispatched as 20 parallel
  async tasks via asyncio.gather against the Top 20 TF-IDF/SNA candidates before the
  final Top 5 is locked. Each instance receives one channel profile and the full
  brand_params dict (including brand_enrichment from Step 4B). Returns semantic
  alignment score, tone match score, audience fit score, a list of red flags, and
  a one-sentence alignment rationale. Never call this agent on the full dataset —
  only on the pre-filtered Top 20 candidates from Step 5D. Results are merged back
  into master_df as semantic_score and tone_match_score columns and incorporated
  into the final 5-signal confidence score composite. Always run this agent after
  the Brand Intelligence Agent (Step 4B) so brand_enrichment tone/trust/avoid
  signals are available to inject into the prompt.
---

# Channel Enrichment Agent

## Role in Pipeline

```
Step 5D — initial Top 20 ranked by 3-signal composite (SNA + TF-IDF + Engagement)
Step 5F — [THIS AGENT × 20, parallel] semantic scores appended to each candidate
Step 5D — final confidence_score_final recomputed with 5 signals; Top 5 selected
Step 7D — red_flags and alignment_rationale rendered in dashboard score breakdown
Step 7H — red_flags surfaced as st.warning() banners in competitive panel
```

**Execution:** Async parallel · 20 calls · `llama-3.1-8b-instant` (Groq) · max_tokens=300 · semaphore(5) — free-tier TPM guard

**Why parallel, not sequential:** 20 sequential calls at ~5s each = 100s of blocking
wait. `asyncio.gather` collapses this to ~5–8s (the latency of a single call). Each
instance is fully stateless — no shared memory, no coordination needed.

**Why this agent, not TF-IDF alone:** TF-IDF is lexical. "Minimal Beauty" scores near
zero against "clean skincare" — no shared vocabulary. This agent understands they are
semantically equivalent. It also catches negative signals TF-IDF misses entirely:
a highly-tagged beauty channel that primarily posts controversy content would score high
on keywords but low on `tone_match` and generate a `red_flag` — preventing a bad
recommendation.

---

## Input Contract

**Per-call inputs (one channel, one brand):**

```python
row = {
    "channel_id":          str,        # YouTube channel ID
    "title":               str,        # channel display name
    "description":         str,        # channel description (truncated to 800 chars)
    "tags":                list[str],  # top 15 tags
    "past_video_titles":   list[str],  # last 5 video titles
    "community_id":        int,        # SNA community cluster label
}

brand_params = {
    "brief_md":    str,        # full Markdown brand brief
    "enrichment": {
        "brand_tone":     list[str],  # from Brand Intelligence Agent
        "trust_signals":  list[str],  # from Brand Intelligence Agent
        "avoid_signals":  list[str],  # from Brand Intelligence Agent
    }
}
```

**Batch input (called from orchestrator):**

```python
candidates_df: pd.DataFrame   # Top 20 rows from master_df
brand_params:  dict           # full brand_params including enrichment
```

---

## Output Contract

**Per-channel output:**

```python
{
    "semantic_alignment_score": float,      # 0.0–1.0 overall brand-channel fit
    "tone_match":               float,      # 0.0–1.0 voice/style alignment
    "audience_fit":             float,      # 0.0–1.0 audience demographic overlap
    "red_flags":                list[str],  # misalignment concerns, or []
    "alignment_rationale":      str,        # one sentence explaining the score
}
```

**Batch output (from `run_channel_enrichment_agents`):**

```python
semantic_results: dict[str, dict]   # {channel_id: per-channel output dict}
```

---

## System Prompt

```
You are a brand-influencer alignment analyst. You receive a brand brief and a
YouTube channel profile. Score how well this channel aligns with the brand on a
scale from 0.0 to 1.0. Return ONLY a JSON object — no prose.
```

---

## User Prompt Template

```
Brand brief:
{brief}

Brand tone descriptors: {tone}
Brand trust signals: {trust_signals}
Content to avoid: {avoid_signals}

Channel profile:
- Name: {title}
- Description: {description}
- Top tags: {tags}
- Past video titles: {video_titles}
- Community cluster: {community_id}

Return JSON:
{
  "semantic_alignment_score": <float 0.0-1.0>,
  "tone_match": <float 0.0-1.0>,
  "audience_fit": <float 0.0-1.0>,
  "red_flags": ["list of any misalignment concerns, or empty list"],
  "alignment_rationale": "one sentence explaining the score"
}
```

**Field mappings:**

| Template variable | Source |
|-------------------|--------|
| `{brief}` | `brand_params["brief_md"]` |
| `{tone}` | `", ".join(brand_params["enrichment"]["brand_tone"])` |
| `{trust_signals}` | `", ".join(brand_params["enrichment"]["trust_signals"])` |
| `{avoid_signals}` | `", ".join(brand_params["enrichment"]["avoid_signals"])` |
| `{title}` | `row["title"]` |
| `{description}` | `str(row["description"])[:800]` — always truncate |
| `{tags}` | `", ".join(row["tags"][:15])` |
| `{video_titles}` | `"; ".join(row["past_video_titles"][:5])` |
| `{community_id}` | `row["community_id"]` |

---

## Implementation

```python
# orchestrator.py
import asyncio, json, os, re
from groq import AsyncGroq
import asyncio

CHANNEL_ENRICHMENT_SYSTEM = """
You are a brand-influencer alignment analyst. You receive a brand brief and a
YouTube channel profile. Score how well this channel aligns with the brand on a
scale from 0.0 to 1.0. Return ONLY a JSON object — no prose.
"""

CHANNEL_ENRICHMENT_PROMPT = """
Brand brief:
{brief}

Brand tone descriptors: {tone}
Brand trust signals: {trust_signals}
Content to avoid: {avoid_signals}

Channel profile:
- Name: {title}
- Description: {description}
- Top tags: {tags}
- Past video titles: {video_titles}
- Community cluster: {community_id}

Return JSON:
{{
  "semantic_alignment_score": <float 0.0-1.0>,
  "tone_match": <float 0.0-1.0>,
  "audience_fit": <float 0.0-1.0>,
  "red_flags": ["list of any misalignment concerns, or empty list"],
  "alignment_rationale": "one sentence explaining the score"
}}
"""

_EMPTY_RESULT = {
    "semantic_alignment_score": 0.0,
    "tone_match":               0.0,
    "audience_fit":             0.0,
    "red_flags":                [],
    "alignment_rationale":      "",
}

async def _enrich_single_channel(
    client:       AsyncGroq,
    row:          dict,
    brand_params: dict,
) -> tuple[str, dict]:
    # Cache key is scoped to both channel AND brand brief hash
    # so cache is invalidated when the brand changes
    cache_key = (
        f"cache/enrich_{row['channel_id']}"
        f"_{hash(brand_params['brief_md'])}.json"
    )
    os.makedirs("cache", exist_ok=True)

    if os.path.exists(cache_key):
        with open(cache_key) as f:
            return row["channel_id"], json.load(f)

    enrichment = brand_params.get("enrichment", {})
    prompt = CHANNEL_ENRICHMENT_PROMPT.format(
        brief         = brand_params["brief_md"],
        tone          = ", ".join(enrichment.get("brand_tone", [])),
        trust_signals = ", ".join(enrichment.get("trust_signals", [])),
        avoid_signals = ", ".join(enrichment.get("avoid_signals", [])),
        title         = row["title"],
        description   = str(row.get("description", ""))[:800],
        tags          = ", ".join(row.get("tags", [])[:15]),
        video_titles  = "; ".join(row.get("past_video_titles", [])[:5]),
        community_id  = row.get("community_id", "unknown"),
    )

    try:
        response = await client.chat.completions.create(
            model      = "llama-3.1-8b-instant",
            max_tokens = 300,
            messages   = [
                {"role": "system", "content": CHANNEL_ENRICHMENT_SYSTEM},
                {"role": "user",   "content": prompt},
            ],
        )
        raw  = response.choices[0].message.content.strip()
        raw  = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)

        with open(cache_key, "w") as f:
            json.dump(data, f)
        return row["channel_id"], data

    except Exception as e:
        print(f"[ChannelEnrichmentAgent] {row['channel_id']} failed: {e}")
        return row["channel_id"], _EMPTY_RESULT


# Semaphore caps concurrent calls at 5 — protects against Groq free-tier
# TPM limit of 6,000/min for llama-3.1-8b-instant.
# 20 calls × ~930 tokens = 18,600 token burst without this guard.
_ENRICHMENT_SEMAPHORE = asyncio.Semaphore(5)

async def _enrich_with_semaphore(client, row, brand_params):
    async with _ENRICHMENT_SEMAPHORE:
        return await _enrich_single_channel(client, row, brand_params)

async def run_channel_enrichment_agents(
    candidates_df: pd.DataFrame,
    brand_params:  dict,
) -> dict[str, dict]:
    """
    Dispatch one enrichment subagent per candidate channel.
    Semaphore(5) prevents bursting the Groq free-tier TPM limit.

    Args:
        candidates_df: Top 20 rows from master_df (pre-filtered by Step 5D)
        brand_params:  Full brand_params dict including ['enrichment'] from Step 4B

    Returns:
        Dict mapping channel_id → enrichment result dict
    """
    client  = AsyncGroq()
    tasks   = [
        _enrich_with_semaphore(client, row.to_dict(), brand_params)
        for _, row in candidates_df.iterrows()
    ]
    results = await asyncio.gather(*tasks)
    return {channel_id: data for channel_id, data in results}
```

---

## Orchestrator Integration

```python
# orchestrator.py → run_full_pipeline() → run_scoring_pipeline()

# After Step 5D: get Top 20 candidates (no diversity filter yet)
top20 = master_df.nlargest(20, 'confidence_score')

# Step 5F: run all 20 enrichment agents in parallel
semantic_results = asyncio.run(
    run_channel_enrichment_agents(top20, brand_params)
)

# Map scores back to master_df (unenriched rows keep original confidence_score)
master_df['semantic_score']    = master_df['channel_id'].map(
    lambda cid: semantic_results.get(cid, {}).get('semantic_alignment_score', 0.0)
).fillna(0.0)
master_df['tone_match_score']  = master_df['channel_id'].map(
    lambda cid: semantic_results.get(cid, {}).get('tone_match', 0.0)
).fillna(0.0)

# Recompute final confidence score for enriched candidates
master_df['confidence_score_final'] = master_df.apply(
    lambda r: (
        0.35 * r['sna_score']          +
        0.20 * r['text_similarity']     +
        0.20 * r.get('semantic_score', 0.0)    +
        0.10 * r.get('tone_match_score', 0.0)  +
        0.15 * r['engagement_score']
    ) if r['channel_id'] in semantic_results
    else r['confidence_score'],     # keep 3-signal score for unenriched channels
    axis=1,
)

# Attach red_flags and rationale for dashboard rendering
top5_df['red_flags'] = top5_df['channel_id'].map(
    lambda cid: semantic_results.get(cid, {}).get('red_flags', [])
)
top5_df['alignment_rationale'] = top5_df['channel_id'].map(
    lambda cid: semantic_results.get(cid, {}).get('alignment_rationale', '')
)
```

**Revised 5-signal weight table:**

| Signal | Weight | Source |
|--------|--------|--------|
| SNA composite score | 35% | NetworkX Step 5A |
| TF-IDF text similarity | 20% | sklearn Step 5B |
| Semantic alignment score | 20% | **This agent** |
| Tone match score | 10% | **This agent** |
| Engagement quality ratio | 15% | pandas Step 5C |

---

## Scoring Guidance for the LLM

Include this context in the prompt for calibration consistency across 20 parallel calls:

| Score range | Interpretation |
|-------------|----------------|
| 0.85 – 1.00 | Near-perfect alignment — brand and channel are clearly in the same space |
| 0.65 – 0.84 | Strong fit — meaningful overlap with minor gaps |
| 0.45 – 0.64 | Partial fit — some alignment but notable differences in tone or audience |
| 0.25 – 0.44 | Weak fit — surface-level overlap only |
| 0.00 – 0.24 | Poor fit — misaligned category, tone, or audience |

---

## Common Failure Modes

| Failure | Symptom | Resolution |
|---------|---------|------------|
| One of 20 tasks raises an exception | `asyncio.gather` still completes the other 19 | Per-task try/except returns `_EMPTY_RESULT`; channel keeps 3-signal score |
| LLM returns invalid JSON | `json.JSONDecodeError` | Strip markdown fences with `re.sub`; if still fails → `_EMPTY_RESULT` |
| `description` field is very long | Slow tokenization, potential truncation | Always slice `[:800]` before inserting into prompt |
| All 20 return score ~0.5 uniformly | Prompt calibration failure | Check that `brand_tone`/`trust_signals` from Step 4B are non-empty |
| Cache miss on every call during demo | Slow demo startup | Pre-generate cache on Friday night (see below) |

---

## Demo Pre-generation

```python
# Run once Friday night — writes cache/enrich_{channel_id}_{hash}.json × 20
import asyncio
from orchestrator import run_channel_enrichment_agents
import pandas as pd, json

top20  = pd.read_csv("channels_scored.csv").nlargest(20, 'confidence_score')
brand  = json.load(open("demo_brand_params.json"))
result = asyncio.run(run_channel_enrichment_agents(top20, brand))
print(f"Cached {len(result)} channel enrichments")
```

Saturday demo reads all 20 from cache — `asyncio.gather` returns in milliseconds.
