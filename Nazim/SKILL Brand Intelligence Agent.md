---
name: SKILL_BrandIntelligenceAgent
description: >
  Extracts structured brand intelligence from a freeform brand brief. Use this
  subagent whenever a raw brand_params dict has been assembled from Streamlit form
  inputs and needs to be enriched before the scoring pipeline runs. Triggers at
  Step 4B of the AI-MCN orchestrator, called once per pipeline invocation,
  sequentially. Returns a typed brand_enrichment dict containing audience personas,
  tone descriptors, trust/avoid signals, competitive positioning, and 10 niche
  YouTube keywords — all derived from implicit signals in the brand story that
  TF-IDF cannot extract. Always use this agent before running Steps 5A–5F; its
  niche_keywords output directly augments the TF-IDF corpus and its tone/trust
  signals feed every Channel Enrichment Agent prompt.
---

# Brand Intelligence Agent

## Role in Pipeline

```
Step 4  — brand_params assembled from Streamlit form
Step 4B — [THIS AGENT] brand_enrichment returned and merged into brand_params
Step 5B — TF-IDF corpus augmented with brand_enrichment['niche_keywords']
Step 5F — Channel Enrichment Agents receive brand_enrichment['brand_tone'],
           ['trust_signals'], ['avoid_signals'] in their prompts
Step 6B — Content Strategy Agents receive enriched brand_params
```

**Execution:** Sequential · 1 call · `llama-3.3-70b-versatile` (Groq) · max_tokens=600

**Why this agent, not pure Python:** A brand manager writing
*"we make clean skincare for busy moms who don't have time to read ingredient labels"*
contains implicit signals — anti-complexity positioning, primary caregiver audience,
trust-based tone — that string concatenation and bag-of-words models cannot surface.
This agent extracts those signals into typed fields that every downstream step can act on.

---

## Input Contract

```python
brand_params = {
    "name":        str,   # brand name
    "category":    str,   # e.g. "Beauty & Skincare"
    "audience":    str,   # free-text audience description
    "budget":      float, # campaign budget in USD
    "description": str,   # product/brand story (primary NLP input)
    "style_prefs": list,  # e.g. ["Tutorial", "Review"]
    "brief_md":    str,   # assembled Markdown brand brief (Step 4 output)
}
```

The agent reads **only** `brand_params["brief_md"]`.

---

## Output Contract

```python
brand_enrichment = {
    "primary_audience_persona":   str,        # one sentence — the core buyer
    "secondary_audience_persona": str | None, # secondary segment, or null
    "brand_tone":                 list[str],  # e.g. ["authentic", "educational", "minimal"]
    "content_affinity":           list[str],  # e.g. ["Tutorial", "Review", "GRWM"]
    "competitive_position":       str,        # differentiator sentence
    "trust_signals":              list[str],  # keywords that signal credibility for this brand
    "avoid_signals":              list[str],  # content styles/topics to avoid
    "niche_keywords":             list[str],  # exactly 10 YouTube search terms
}
```

All fields are required. Use `null` / empty list when a field cannot be inferred —
**never hallucinate specifics** not present in the brief.

---

## System Prompt

```
You are a brand strategy analyst. Your job is to read a brand brief and extract
structured intelligence from it. You must return ONLY valid JSON — no prose, no
markdown fences. If a field cannot be inferred, use null.
```

---

## User Prompt Template

```
Analyse this brand brief and return a JSON object with exactly these keys:

{
  "primary_audience_persona": "string — one concise sentence describing the core buyer",
  "secondary_audience_persona": "string or null",
  "brand_tone": ["list", "of", "tone", "descriptors"],
  "content_affinity": ["list", "of", "content", "formats", "that", "fit", "this", "brand"],
  "competitive_position": "string — what differentiates this brand",
  "trust_signals": ["list", "of", "keywords", "that", "signal", "credibility"],
  "avoid_signals": ["list", "of", "content", "styles", "or", "topics", "to", "avoid"],
  "niche_keywords": ["exactly", "10", "specific", "YouTube", "search", "terms"]
}

Brand brief:
{brief}
```

**Fill `{brief}` with `brand_params["brief_md"]` verbatim.**

---

## Implementation

```python
# orchestrator.py
from groq import Groq
import json, os, re

BRAND_INTELLIGENCE_SYSTEM = """
You are a brand strategy analyst. Your job is to read a brand brief and extract
structured intelligence from it. You must return ONLY valid JSON — no prose, no
markdown fences. If a field cannot be inferred, use null.
"""

BRAND_INTELLIGENCE_PROMPT = """
Analyse this brand brief and return a JSON object with exactly these keys:

{{
  "primary_audience_persona": "string — one concise sentence describing the core buyer",
  "secondary_audience_persona": "string or null",
  "brand_tone": ["list", "of", "tone", "descriptors"],
  "content_affinity": ["list", "of", "content", "formats", "that", "fit", "this", "brand"],
  "competitive_position": "string — what differentiates this brand",
  "trust_signals": ["list", "of", "keywords", "that", "signal", "credibility"],
  "avoid_signals": ["list", "of", "content", "styles", "or", "topics", "to", "avoid"],
  "niche_keywords": ["exactly", "10", "specific", "YouTube", "search", "terms"]
}}

Brand brief:
{brief}
"""

def run_brand_intelligence_agent(brand_params: dict) -> dict:
    cache_path = f"cache/brand_intel_{hash(brand_params['brief_md'])}.json"
    os.makedirs("cache", exist_ok=True)

    # Cache hit — return immediately
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return json.load(f)

    try:
        client   = Groq()
        response = client.chat.completions.create(
            model      = "llama-3.3-70b-versatile",
            max_tokens = 600,
            messages   = [
                {"role": "system", "content": BRAND_INTELLIGENCE_SYSTEM},
                {"role": "user",   "content": BRAND_INTELLIGENCE_PROMPT.format(brief=brand_params["brief_md"])},
            ],
        )
        raw  = response.choices[0].message.content.strip()
        raw  = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)

        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)
        return data

    except Exception as e:
        print(f"[BrandIntelligenceAgent] Failed: {e} — returning minimal fallback")
        return _fallback_enrichment(brand_params)


def _fallback_enrichment(brand_params: dict) -> dict:
    """
    Graceful degradation: derive minimal enrichment from raw brand_params fields.
    Pipeline continues; downstream agents receive partial but valid data.
    """
    return {
        "primary_audience_persona":   brand_params.get("audience", ""),
        "secondary_audience_persona": None,
        "brand_tone":                 brand_params.get("style_prefs", []),
        "content_affinity":           brand_params.get("style_prefs", []),
        "competitive_position":       "",
        "trust_signals":              [],
        "avoid_signals":              [],
        "niche_keywords":             [],
    }
```

---

## Orchestrator Integration

```python
# orchestrator.py → run_full_pipeline()

# Step 4B — called immediately after brand_params is assembled
brand_enrichment = run_brand_intelligence_agent(brand_params)
brand_params["enrichment"] = brand_enrichment   # merge in-place

# Downstream consumers:
# Step 5B:  brand_params["enrichment"]["niche_keywords"]  → augments TF-IDF corpus
# Step 5F:  brand_params["enrichment"]["brand_tone"]      → Channel Enrichment Agent prompts
#           brand_params["enrichment"]["trust_signals"]
#           brand_params["enrichment"]["avoid_signals"]
# Step 6B:  brand_params["enrichment"] passed through to content strategy prompts
# Step 7A:  brand_enrichment fields rendered as st.info() callouts in dashboard
```

---

## Validation

After receiving the response, validate before caching:

```python
REQUIRED_KEYS = {
    "primary_audience_persona", "secondary_audience_persona",
    "brand_tone", "content_affinity", "competitive_position",
    "trust_signals", "avoid_signals", "niche_keywords",
}

def _validate(data: dict) -> bool:
    if not REQUIRED_KEYS.issubset(data.keys()):
        return False
    if not isinstance(data.get("niche_keywords"), list):
        return False
    if len(data.get("niche_keywords", [])) < 5:
        return False   # fewer than 5 keywords is suspicious — fall back
    return True
```

If validation fails, log a warning and return `_fallback_enrichment()` — **do not
raise an exception** that would halt the pipeline.

---

## Common Failure Modes

| Failure | Symptom | Resolution |
|---------|---------|------------|
| LLM returns prose instead of JSON | `json.JSONDecodeError` | `re.sub` strips fences; if still fails → fallback |
| `niche_keywords` has fewer than 10 items | Validation warning | Accept partial list; downstream TF-IDF boost is weaker but functional |
| Brand story is very short (<20 words) | Sparse output, nulls everywhere | Acceptable; advise user to provide richer brand story |
| Cache file is corrupt / zero bytes | `json.JSONDecodeError` on load | Delete cache file, re-run agent |

---

## Demo Pre-generation

**Requires:** `GROQ_API_KEY` in `.env` — free at [console.groq.com](https://console.groq.com). No credit card needed.


Run once on Friday night against your real brand input:
```bash
python -c "
from orchestrator import run_brand_intelligence_agent
brand_params = { 'brief_md': open('demo_brand_brief.md').read(), ... }
result = run_brand_intelligence_agent(brand_params)
print(result)
"
```
Cache is written to `cache/brand_intel_{hash}.json`. Saturday demo loads from cache —
no API call required.
