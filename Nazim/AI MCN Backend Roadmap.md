# AI-MCN: Backend Execution Roadmap

---

## Phase 1: Data Acquisition & Master Processing

### Step 1 & 2: Distributed YouTube Scraping

- **Input:** Raw industry keywords (e.g., "K-beauty", "Indie Games", "Fitness").
- **Task:** Implement `data_collection.py` using the `google-api-python-client`.
- **Logic:**
  - Fetch metadata for 100+ channels per keyword: `channel_id`, `title`, `description`, `subscriber_count`, `view_count`, and `tags`.
  - Additionally collect: `avg_likes`, `avg_comments`, `upload_frequency`, `category`, past video `titles` and `descriptions` (for Feature 4 style extraction).
  - Store each entry as a JSON object in a master list.
  - Convert the list into a `pandas` DataFrame and cache as `channels_raw.csv` to avoid re-hitting API quota.

### Step 3: Master Dataset Aggregation

- **Input:** Four separate DataFrames/CSVs (one from each team member).
- **Task:** Execute a merge script in `utils.py`.
- **Logic:**
  - Use `pd.concat` to unify all member datasets.
  - **Deduplication:** Use `drop_duplicates(subset=['channel_id'])` to ensure a clean master list.
  - **SQL Guardrail:** Apply `ON CONFLICT (message_id) DO NOTHING` logic if writing to a database to prevent primary key errors.
  - Export unified dataset as `channels_master.csv` — this is the single source of truth for all downstream steps.

---

## Phase 2: Brand Context, Scoring Engine & Subagent Orchestration

> **Multi-Agent Architecture Overview**
>
> Phase 2 deploys a coordinated subagent system managed by `orchestrator.py`. Subagents are
> focused Claude API calls with narrow system prompts and typed outputs — they are not general
> assistants. Each runs exactly where an LLM adds unique value (semantic understanding, structured
> extraction, qualitative judgment) that pure Python cannot provide. Every step that is pure
> math or pure data manipulation (SNA graph construction, TF-IDF vectorization, engagement
> normalization) deliberately stays as Python — calling an LLM for arithmetic is wasteful and
> slower. The orchestrator manages async dispatch, response parsing, cache fallback, and error
> handling so that `app.py` makes a single function call and receives a fully assembled result dict.
>
> ```
> orchestrator.py — full pipeline control flow
> │
> ├── [sequential]  BrandIntelligenceAgent    →  enriched brand_params     (Step 4B)
> ├── [sequential]  SNA + TF-IDF + Engagement →  master_df scored          (Steps 5A–5D)
> ├── [parallel ×20] ChannelEnrichmentAgent   →  semantic_scores appended  (Step 5F)
> ├── [sequential]  Composite scoring + Top 5  →  top5_df                  (Step 5D)
> ├── [parallel ×5]  ContentStrategyAgent     →  strategy_texts dict       (Step 6B)
> └── [sequential]  ExecutiveSynthesisAgent   →  brand_memo.md             (Step 7I)
> ```

---

### Step 4: Brand Context Capture (Streamlit Frontend → Backend)

- **Interface:** Streamlit (`app.py`) renders a structured brand intake form.
- **Input fields collected via `st.text_input` / `st.text_area` / `st.selectbox`:**
  - **Brand Name** — `st.text_input("Brand Name")`
  - **Product Category** — `st.selectbox(...)` (e.g. Skincare, Tech, Fitness, Gaming)
  - **Target Audience** — `st.text_area(...)` (demographics, psychographics, use-case description)
  - **Budget Range** — `st.slider(...)` for rough range; `st.number_input(...)` for exact ROI simulation
  - **Brand Story / Product Description** — `st.text_area(...)` — the primary NLP input
  - **Preferred Content Style** — `st.multiselect(...)` (e.g. Tutorial, Review, Lifestyle, Short-form)

- **Task:** Parse all inputs and format them into a structured **Brand Brief** string used downstream.
- **Logic:**
  1. Concatenate all text fields into a single clean `brand_brief` string:
     ```python
     brand_brief = f"""
     Brand: {brand_name}
     Category: {category}
     Target Audience: {target_audience}
     Product Description: {product_description}
     Preferred Style: {', '.join(content_style)}
     """
     ```
  2. Pass `brand_brief` as a **Markdown-formatted string** to the Claude/OpenAI API (Step 6) for structured parsing and content strategy generation. The LLM receives it as structured context — not raw freeform text.
  3. Store all input fields in a `brand_params` dict for reuse across Steps 5 and 6:
     ```python
     brand_params = {
         "name": brand_name,
         "category": category,
         "audience": target_audience,
         "budget": budget,
         "description": product_description,
         "style_prefs": content_style,
         "brief_md": brand_brief,
     }
     ```
  4. Display a **Brand Brief Preview** card in the Streamlit sidebar using `st.markdown(brand_brief)` so the user can confirm inputs before running the pipeline.

---

#### Step 4B — 🤖 Subagent: Brand Intelligence Agent

> **Skill file:** `subagents/SKILL_BrandIntelligenceAgent.md`

> **Why a subagent here:** The raw `brand_brief` string concatenation above is structurally
> correct but semantically shallow. A brand manager writing "we make clean skincare for busy
> moms who don't have time to read ingredient labels" contains implicit signals — trust-based
> tone, anti-complexity positioning, primary caregiver audience — that TF-IDF's bag-of-words
> model cannot extract. The Brand Intelligence Agent reads the freeform brand story and returns
> a structured enrichment dict that sharpens every downstream scoring signal.

- **File:** `orchestrator.py` → `run_brand_intelligence_agent(brand_params)`
- **Trigger:** Called once, sequentially, immediately after `brand_params` is assembled.
- **Input:** `brand_params['brief_md']` (the Markdown brand brief)
- **Output:** `brand_enrichment` dict — merged back into `brand_params` before Step 5

```python
# orchestrator.py

from groq import Groq
import json, re

BRAND_INTELLIGENCE_SYSTEM = """
You are a brand strategy analyst. Your job is to read a brand brief and extract
structured intelligence from it. You must return ONLY valid JSON — no prose, no
markdown fences. If a field cannot be inferred, use null.
"""

BRAND_INTELLIGENCE_PROMPT = """
Analyse this brand brief and return a JSON object with exactly these keys:

{
  "primary_audience_persona": "string — one concise sentence describing the core buyer",
  "secondary_audience_persona": "string or null",
  "brand_tone": ["list", "of", "tone", "descriptors"],
  "content_affinity": ["list", "of", "content", "formats", "that", "fit", "this", "brand"],
  "competitive_position": "string — what differentiates this brand (e.g. 'clean ingredients, premium price point')",
  "trust_signals": ["list", "of", "keywords", "that", "signal", "credibility", "for", "this", "brand"],
  "avoid_signals": ["list", "of", "content", "styles", "or", "topics", "this", "brand", "should", "avoid"],
  "niche_keywords": ["list", "of", "10", "specific", "YouTube", "search", "terms", "relevant", "to", "this", "brand"]
}

Brand brief:
{brief}
"""

def run_brand_intelligence_agent(brand_params: dict) -> dict:
    cache_path = f"cache/brand_intel_{hash(brand_params['brief_md'])}.json"

    try:
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return json.load(f)

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
        # Strip any accidental markdown fences before parsing
        raw  = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)

        os.makedirs("cache", exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)
        return data

    except Exception as e:
        print(f"[BrandIntelligenceAgent] Failed: {e} — using empty enrichment")
        return {
            "primary_audience_persona": brand_params.get("audience", ""),
            "brand_tone": brand_params.get("style_prefs", []),
            "niche_keywords": [],
            "trust_signals": [],
            "avoid_signals": [],
            "content_affinity": [],
            "competitive_position": "",
            "secondary_audience_persona": None,
        }
```

- **Integration:** The returned `brand_enrichment` dict is merged into `brand_params`:
  ```python
  brand_enrichment = run_brand_intelligence_agent(brand_params)
  brand_params["enrichment"] = brand_enrichment
  # brand_params["enrichment"]["niche_keywords"] is used to
  # augment the TF-IDF corpus in Step 5B and the LLM prompts in Steps 5F and 6B.
  ```

---

### Step 5: Hybrid AI Matching Engine

- **Input:** Master Influencer DataFrame (`channels_master.csv` loaded into memory as `master_df`) + `brand_params` dict from Step 4.
- **Task:** Execute `matching_roi.py` to query `master_df` and assign a composite **Confidence Score** to every influencer, then return the Top 5.
- **Logic:**

#### 5A — SNA Graph Construction (NetworkX)

  Build the influencer network graph before scoring:
  ```python
  import networkx as nx

  G = nx.Graph()
  # Add nodes — one per channel
  for _, row in master_df.iterrows():
      G.add_node(row['channel_id'], **row.to_dict())

  # Add edges — channels sharing 2+ tags are connected
  # Edge weight = number of shared tags (stronger overlap = stronger edge)
  for i, ch1 in master_df.iterrows():
      for j, ch2 in master_df.iterrows():
          if i >= j:
              continue
          shared = set(ch1['tags']).intersection(set(ch2['tags']))
          if len(shared) >= 2:
              G.add_edge(ch1['channel_id'], ch2['channel_id'], weight=len(shared))
  ```

  Compute centrality metrics and write back to `master_df`:
  ```python
  master_df['degree_centrality']       = master_df['channel_id'].map(nx.degree_centrality(G))
  master_df['betweenness_centrality']  = master_df['channel_id'].map(nx.betweenness_centrality(G, weight='weight'))
  master_df['eigenvector_centrality']  = master_df['channel_id'].map(nx.eigenvector_centrality(G, weight='weight', max_iter=1000))

  # Composite SNA score: weighted average of all three centrality metrics
  master_df['sna_score'] = (
      0.33 * master_df['degree_centrality'] +
      0.34 * master_df['betweenness_centrality'] +
      0.33 * master_df['eigenvector_centrality']
  )
  ```

  Run community detection to label audience clusters (used for bias mitigation and Top 5 diversity):
  ```python
  from networkx.algorithms.community import greedy_modularity_communities
  communities = greedy_modularity_communities(G)
  community_map = {node: i for i, comm in enumerate(communities) for node in comm}
  master_df['community_id'] = master_df['channel_id'].map(community_map)
  ```

  Save the enriched DataFrame as `channels_scored.csv` for downstream use and caching.

#### 5B — Text Similarity Scoring (TF-IDF)

  Compute content alignment between brand description and each influencer's channel text.
  Augment the brand document with `niche_keywords` extracted by the Brand Intelligence Agent
  in Step 4B — this sharpens cosine similarity for terms TF-IDF's vocabulary would otherwise
  underweight:
  ```python
  from sklearn.feature_extraction.text import TfidfVectorizer
  from sklearn.metrics.pairwise import cosine_similarity

  # Augment brand brief with niche_keywords from Brand Intelligence Agent (Step 4B)
  niche_boost = ' '.join(brand_params['enrichment'].get('niche_keywords', []))
  augmented_brief = brand_params['brief_md'] + ' ' + niche_boost

  # Combine each influencer's tags + video titles into a single text blob
  master_df['channel_text'] = master_df['tags'].apply(lambda t: ' '.join(t)) + ' ' + master_df['title']

  # Vectorize augmented brand brief + all channel texts together
  corpus = [augmented_brief] + master_df['channel_text'].tolist()
  vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
  tfidf_matrix = vectorizer.fit_transform(corpus)

  # Cosine similarity: brand brief (row 0) vs. each channel
  similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
  master_df['text_similarity'] = similarities
  ```

  Optional upgrade (if time permits): replace TF-IDF with `sentence-transformers` BERT embeddings for semantic matching that catches synonyms and paraphrases TF-IDF misses.

#### 5C — Engagement Quality Ratio

  Normalize engagement rate relative to subscriber count to surface high-quality mid-tier creators and penalize inflated follower counts:
  ```python
  master_df['engagement_ratio'] = (
      (master_df['avg_likes'] + master_df['avg_comments']) / master_df['subscriber_count']
  ).clip(upper=0.20)  # cap outliers at 20%

  # Min-max normalize to [0, 1] for scoring
  master_df['engagement_score'] = (
      (master_df['engagement_ratio'] - master_df['engagement_ratio'].min()) /
      (master_df['engagement_ratio'].max() - master_df['engagement_ratio'].min())
  )
  ```

#### 5D — Composite Confidence Score & Top 5 Selection

  Apply the weighted formula and select the Top 5, ensuring community diversity:
  ```python
  master_df['confidence_score'] = (
      0.40 * master_df['sna_score'] +
      0.30 * master_df['text_similarity'] +
      0.30 * master_df['engagement_score']
  )

  # Sort by score descending; enforce one influencer per community cluster
  # to prevent recommending 5 influencers from the same audience bubble
  top5_df = (
      master_df
      .sort_values('confidence_score', ascending=False)
      .drop_duplicates(subset=['community_id'], keep='first')
      .head(5)
      .reset_index(drop=True)
  )
  ```

  Each row in `top5_df` carries the full score breakdown: `sna_score`, `text_similarity`, `engagement_score`, `confidence_score`, plus all original channel metadata. This is the primary output passed to Steps 6 and 7.

#### 5E — Competitive Differentiation Logic

  This step is what separates AI-MCN from existing platforms (Modash, GRIN, VidIQ). Compute a **Popularity Bias Report** to show stakeholders why the recommendations are different:
  ```python
  # Degree-only ranking (what existing tools do — sorted by follower count proxy)
  degree_top5 = master_df.nlargest(5, 'degree_centrality')[['title', 'subscriber_count', 'degree_centrality']]

  # Betweenness-based ranking (AI-MCN: finds information brokers, not just popular accounts)
  betweenness_top5 = master_df.nlargest(5, 'betweenness_centrality')[['title', 'subscriber_count', 'betweenness_centrality']]

  # Overlap analysis: how many channels appear in BOTH lists?
  overlap = set(degree_top5['title']).intersection(set(betweenness_top5['title']))
  bias_report = {
      "degree_top5": degree_top5,
      "betweenness_top5": betweenness_top5,
      "overlap_count": len(overlap),
      "unique_to_betweenness": len(betweenness_top5) - len(overlap),
      "narrative": (
          f"Traditional tools would recommend {len(overlap)}/5 of the same influencers AI-MCN does. "
          f"AI-MCN surfaces {len(overlap)} overlapping picks but uniquely identifies "
          f"{5 - len(overlap)} bridge-node creators that follower-count tools miss entirely."
      )
  }
  ```

  The `bias_report` dict is passed to Step 7 for visualization and serves as a key slide in the presentation.

---

#### Step 5F — 🤖 Subagent: Channel Enrichment Agents (Parallel ×20)

> **Skill file:** `subagents/SKILL_ChannelEnrichmentAgent.md`

> **Why subagents here:** TF-IDF cosine similarity is a lexical signal — it matches exact or
> near-exact word overlap. It scores a channel called "Minimal Beauty" as a weak match for a
> "clean skincare" brand brief because "minimal" and "clean" share no vocabulary. A language
> model understands they are semantically aligned. The Channel Enrichment Agents bridge this
> gap by reading each candidate channel's description and top video titles and returning a
> qualitative alignment score and tone match — signals that pure text statistics cannot produce.
>
> Scope: runs on the **Top 20** candidates from Step 5D (pre-diversity filter), not the full
> dataset. This bounds cost to ~20 API calls per pipeline run while focusing enrichment where
> it matters most. Results are written to a new `semantic_score` column and factored into
> the final composite before the Top 5 is locked.

- **File:** `orchestrator.py` → `run_channel_enrichment_agents(candidates_df, brand_params)`
- **Trigger:** Called after Step 5D produces the initial ranked list; before Top 5 is finalized.
- **Concurrency:** `asyncio.gather` — all 20 calls fire simultaneously.
- **Input:** Top 20 rows from `master_df` + `brand_params` (including `brand_enrichment` from Step 4B)
- **Output:** `semantic_scores` dict — `{channel_id: float}` — merged into `master_df` as `semantic_score`

```python
# orchestrator.py

import asyncio
from groq import AsyncGroq

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
  "semantic_alignment_score": <float 0.0–1.0>,
  "tone_match": <float 0.0–1.0>,
  "audience_fit": <float 0.0–1.0>,
  "red_flags": ["list of any misalignment concerns, or empty list"],
  "alignment_rationale": "one sentence explaining the score"
}}
"""

async def _enrich_single_channel(
    client: AsyncGroq,
    row: dict,
    brand_params: dict,
) -> tuple[str, dict]:
    enrichment = brand_params.get("enrichment", {})
    prompt = CHANNEL_ENRICHMENT_PROMPT.format(
        brief        = brand_params["brief_md"],
        tone         = ", ".join(enrichment.get("brand_tone", [])),
        trust_signals= ", ".join(enrichment.get("trust_signals", [])),
        avoid_signals= ", ".join(enrichment.get("avoid_signals", [])),
        title        = row["title"],
        description  = str(row.get("description", ""))[:800],  # truncate long descriptions
        tags         = ", ".join(row.get("tags", [])[:15]),
        video_titles = "; ".join(row.get("past_video_titles", [])[:5]),
        community_id = row.get("community_id", "unknown"),
    )

    cache_key  = f"cache/enrich_{row['channel_id']}_{hash(brand_params['brief_md'])}.json"
    if os.path.exists(cache_key):
        with open(cache_key) as f:
            return row["channel_id"], json.load(f)

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
        os.makedirs("cache", exist_ok=True)
        with open(cache_key, "w") as f:
            json.dump(data, f)
        return row["channel_id"], data

    except Exception as e:
        print(f"[ChannelEnrichmentAgent] {row['channel_id']} failed: {e}")
        return row["channel_id"], {"semantic_alignment_score": 0.0, "tone_match": 0.0,
                                    "audience_fit": 0.0, "red_flags": [], "alignment_rationale": ""}


async def run_channel_enrichment_agents(
    candidates_df: pd.DataFrame,
    brand_params:  dict,
) -> dict:
    """Dispatch one enrichment subagent per candidate channel, all in parallel."""
# Semaphore: caps concurrent Groq free-tier calls at 5 to avoid
# bursting the 6,000 TPM limit for llama-3.1-8b-instant.
_ENRICHMENT_SEM = asyncio.Semaphore(5)

async def _enrich_guarded(client, row, brand_params):
    async with _ENRICHMENT_SEM:
        return await _enrich_single_channel(client, row, brand_params)

    client  = AsyncGroq()
    tasks   = [
        _enrich_guarded(client, row.to_dict(), brand_params)
        for _, row in candidates_df.iterrows()
    ]
    results = await asyncio.gather(*tasks)
    return {channel_id: data for channel_id, data in results}
```

- **Integration:** Merge semantic scores back into `master_df` and recompute the final
  composite with a 5-point semantic adjustment before selecting the Top 5:
  ```python
  # In matching_roi.py — called from orchestrator.py after Step 5D

  # Get Top 20 candidates (before diversity filter)
  top20 = master_df.nlargest(20, 'confidence_score')

  # Run enrichment subagents in parallel
  semantic_results = asyncio.run(
      run_channel_enrichment_agents(top20, brand_params)
  )

  # Map semantic scores back to master_df
  master_df['semantic_score'] = master_df['channel_id'].map(
      lambda cid: semantic_results.get(cid, {}).get('semantic_alignment_score', 0.0)
  ).fillna(0.0)

  master_df['tone_match_score'] = master_df['channel_id'].map(
      lambda cid: semantic_results.get(cid, {}).get('tone_match', 0.0)
  ).fillna(0.0)

  # Recompute final confidence score including semantic signal
  # Semantic replaces a slice of text_similarity weight for Top 20 candidates
  master_df['confidence_score_final'] = master_df.apply(
      lambda r: (
          0.35 * r['sna_score'] +
          0.20 * r['text_similarity'] +
          0.20 * r.get('semantic_score', 0.0) +
          0.10 * r.get('tone_match_score', 0.0) +
          0.15 * r['engagement_score']
      ) if r['channel_id'] in semantic_results
      else r['confidence_score'],   # keep original score for unenriched channels
      axis=1,
  )

  # Final Top 5 with diversity guardrail
  top5_df = (
      master_df
      .sort_values('confidence_score_final', ascending=False)
      .drop_duplicates(subset=['community_id'], keep='first')
      .head(5)
      .reset_index(drop=True)
  )

  # Attach red_flags to top5_df for display in the competitive differentiation panel
  top5_df['red_flags'] = top5_df['channel_id'].map(
      lambda cid: semantic_results.get(cid, {}).get('red_flags', [])
  )
  top5_df['alignment_rationale'] = top5_df['channel_id'].map(
      lambda cid: semantic_results.get(cid, {}).get('alignment_rationale', '')
  )
  ```

  **Revised weight table after subagent integration:**

  | Signal                          | Weight | Source                          |
  |---------------------------------|--------|---------------------------------|
  | SNA composite score             | 35%    | NetworkX (Steps 5A)             |
  | TF-IDF text similarity          | 20%    | sklearn (Step 5B)               |
  | Semantic alignment score        | 20%    | ChannelEnrichmentAgent (Step 5F)|
  | Tone match score                | 10%    | ChannelEnrichmentAgent (Step 5F)|
  | Engagement quality ratio        | 15%    | pandas (Step 5C)                |

---

## Phase 3: Performance Metrics, Content Generation & Synthesis

### Step 6: ROI Simulation & LLM Content Strategy

#### 6A — ROI Simulator

- **Input:** `brand_params['budget']` (exact value from `st.number_input`) + selected influencer's avg view count from `top5_df`.
- **Task:** Apply the performance marketing funnel from the course Blendo assignment, adapted for influencer marketing.
- **Formula:**
  ```python
  def simulate_roi(budget, avg_views, ctr=0.012, cvr=0.035, aov=65.0):
      """
      Default benchmarks (document in a comment and cite source):
        CTR 1.2%  — industry avg for YouTube sponsored content (Influencer Marketing Hub, 2024)
        CVR 3.5%  — mid-funnel conversion rate for beauty/lifestyle (Nielsen, 2023)
        AOV $65   — average order value, overridden by brand input
      All three are exposed as Streamlit sliders for sensitivity analysis.
      """
      sponsorship_rate_per_view = 0.018   # $0.018 CPV average
      impressions   = budget / sponsorship_rate_per_view
      clicks        = impressions * ctr
      conversions   = clicks * cvr
      revenue       = conversions * aov
      roa           = revenue / budget

      # ±30% confidence range — honest uncertainty quantification
      return {
          "impressions":        round(impressions),
          "clicks":             round(clicks),
          "conversions":        round(conversions),
          "est_revenue":        round(revenue, 2),
          "roa_expected":       round(roa, 2),
          "roa_low":            round(roa * 0.70, 2),
          "roa_high":           round(roa * 1.30, 2),
          "confidence_note":    "±30% range based on industry benchmarks. Not a guarantee.",
      }
  ```

- **Streamlit UI for ROI:**
  - `st.number_input("Budget ($)")` — exact amount
  - `st.slider("CTR benchmark", 0.005, 0.030, 0.012)` — let user adjust sensitivity
  - `st.slider("CVR benchmark", 0.010, 0.080, 0.035)`
  - `st.slider("Average Order Value ($)", 10, 500, 65)`
  - Render output as a **funnel chart** (Plotly) and a **confidence band chart** showing low/expected/high ROA.

---

#### Step 6B — 🤖 Subagents: Content Strategy Agents (Parallel ×5)

> **Skill file:** `subagents/SKILL_ContentStrategyAgent.md`

> **Why subagents here, and why parallel:** Content strategy generation requires generating 3
> tailored sponsorship concepts for each of the 5 recommended influencers. Running these
> sequentially at ~5–10 seconds per LLM call means 25–50 seconds of blocking wait time in the
> UI — unacceptable for a live demo. Running all 5 as parallel async subagents collapses this
> to the latency of a single call (~5–10 seconds total). Each subagent operates with an
> identical system prompt but a unique user message scoped to one influencer. They share no
> state with each other — true parallel independence.

- **File:** `orchestrator.py` → `run_content_strategy_agents(top5_df, brand_params)`
- **Trigger:** Called after `top5_df` is finalized and after ROI simulation completes.
- **Concurrency:** `asyncio.gather` — all 5 calls fire simultaneously.
- **Input:** `top5_df` (5 rows) + `brand_params` dict
- **Output:** `strategy_texts` dict — `{channel_id: markdown_string}` — rendered in Step 7G

```python
# orchestrator.py

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
Generate exactly 3 sponsorship content concepts for this influencer × brand pairing.
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
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return row["channel_id"], f.read()

    try:
        prompt   = CONTENT_STRATEGY_PROMPT.format(
            brief             = brand_params["brief_md"],
            title             = row["title"],
            subscriber_count  = int(row.get("subscriber_count", 0)),
            avg_views         = int(row.get("avg_views", 0)),
            tags              = ", ".join(row.get("tags", [])[:10]),
            community_id      = row.get("community_id", "N/A"),
            confidence_score  = float(row.get("confidence_score_final", row.get("confidence_score", 0))),
            engagement_ratio  = float(row.get("engagement_ratio", 0)),
            upload_frequency  = row.get("upload_frequency", "N/A"),
            alignment_rationale = row.get("alignment_rationale", "N/A"),
            tone_match_score  = float(row.get("tone_match_score", 0)),
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
        os.makedirs("cache", exist_ok=True)
        with open(cache_path, "w") as f:
            f.write(text)
        return row["channel_id"], text

    except Exception as e:
        print(f"[ContentStrategyAgent] {row['channel_id']} failed: {e}")
        fallback = f"# Content Strategy Unavailable\n\nAPI error for {row['title']}: {e}"
        return row["channel_id"], fallback


async def run_content_strategy_agents(
    top5_df:      pd.DataFrame,
    brand_params: dict,
) -> dict:
    """Dispatch one content strategy subagent per Top 5 influencer, all in parallel."""
    client  = AsyncGroq()
    tasks   = [
        _generate_single_strategy(client, row.to_dict(), brand_params)
        for _, row in top5_df.iterrows()
    ]
    results = await asyncio.gather(*tasks)
    return {channel_id: text for channel_id, text in results}
```

- **Calling from `app.py`:**
  ```python
  with st.spinner("Generating content strategies for all 5 influencers in parallel…"):
      strategy_texts = asyncio.run(
          run_content_strategy_agents(top5_df, brand_params)
      )
  ```

- **Pre-generation for demo safety:** On Friday night, run `asyncio.run(run_content_strategy_agents(...))` once against your real data. The cache files will be written to `cache/`. All subsequent runs — including the live demo — will load from cache and return in milliseconds.

- **Bias Mitigation:** After generating strategies, check that the 5 recommendations span at least 3 distinct `community_id` clusters. If not, swap the lowest-scoring same-cluster influencer for the highest-scoring influencer from an underrepresented cluster and flag the substitution in the UI.

---

### Step 7: Dashboards & Distribution

- **Input:** `top5_df`, `bias_report`, `roi_result`, `strategy_texts` dict (from Step 6B), NetworkX graph object `G`.
- **Task:** Render the complete interactive dashboard in `app.py`.
- **Visualization Suite:**

#### 7A — Brand Context Display Panel
  Show the parsed Brand Brief as a formatted card before results load:
  - `st.markdown(brand_params['brief_md'])` rendered in a styled `st.container()` with a border
  - Key brand parameters displayed as `st.metric()` tiles: Category, Budget, Audience segment
  - A **TF-IDF keyword cloud** (Matplotlib `WordCloud`) built from `brand_params['description']` — shows which terms drive matching
  - Brand Intelligence enrichment summary: `primary_audience_persona`, `brand_tone`, `competitive_position` rendered as `st.info()` callouts — sourced from the Step 4B subagent output

#### 7B — Interactive SNA Network Graph
  ```python
  from pyvis.network import Network
  import streamlit.components.v1 as components

  net = Network(height="600px", width="100%", bgcolor="#0f1117", font_color="white")
  net.from_nx(G)

  # Visual encoding: node size = sna_score, node color = community_id
  for node in net.nodes:
      channel = master_df[master_df['channel_id'] == node['id']].iloc[0]
      node['size']  = 10 + channel['sna_score'] * 60
      node['color'] = COMMUNITY_COLOR_MAP[channel['community_id']]
      node['title'] = (
          f"{channel['title']}<br>"
          f"Subscribers: {channel['subscriber_count']:,}<br>"
          f"SNA Score: {channel['sna_score']:.3f}<br>"
          f"Community: {channel['community_id']}"
      )

  # Highlight Top 5 with a gold border
  top5_ids = set(top5_df['channel_id'])
  for node in net.nodes:
      if node['id'] in top5_ids:
          node['borderWidth'] = 4
          node['color'] = {'border': '#FFD700', 'background': node['color']}

  net.save_graph("sna_graph.html")
  components.html(open("sna_graph.html").read(), height=620, scrolling=False)
  ```

#### 7C — Centrality Distribution Charts (Plotly)
  Three side-by-side `plotly.express.histogram` charts:
  - Degree Centrality distribution — with a vertical line marking each Top 5 influencer
  - Betweenness Centrality distribution
  - Eigenvector Centrality distribution
  - All rendered with `st.plotly_chart(fig, use_container_width=True)`

#### 7D — Match Scorecard (Top 5 Comparison)
  Horizontal grouped bar chart (Plotly) comparing all score components per influencer.
  Now includes the two semantic signals from the Channel Enrichment Agents (Step 5F):
  ```python
  import plotly.graph_objects as go

  fig = go.Figure()
  score_signals = [
      ('sna_score',          '#4C9BE8', 'SNA Score'),
      ('text_similarity',    '#E87C4C', 'Text Similarity'),
      ('semantic_score',     '#A78BFA', 'Semantic Alignment'),
      ('tone_match_score',   '#F472B6', 'Tone Match'),
      ('engagement_score',   '#4CE87C', 'Engagement Score'),
  ]
  for col, color, label in score_signals:
      if col in top5_df.columns:
          fig.add_trace(go.Bar(
              name=label, y=top5_df['title'], x=top5_df[col],
              orientation='h', marker_color=color,
          ))
  fig.update_layout(barmode='group', title='Top 5 Influencer Score Breakdown (All Signals)')
  st.plotly_chart(fig, use_container_width=True)
  ```

  Below the chart, render `st.dataframe(top5_df[display_cols])` with columns: Channel, Subscribers, SNA Score, Text Match, Semantic Alignment, Engagement Rate, Confidence Score, Alignment Rationale.

#### 7E — Niche / Community Distribution (Plotly)
  - **Pie chart:** proportion of channels per `community_id` cluster in the full `master_df`
  - **Scatter plot:** `subscriber_count` (x-axis) vs. `engagement_ratio` (y-axis), colored by `community_id`, sized by `sna_score` — reveals mid-tier high-engagement creators vs. mega-influencers with low engagement
  - **Bar chart:** Top 10 most frequent tags across the full dataset — shows what topics dominate the niche

#### 7F — ROI Funnel Visualization (Plotly)
  ```python
  import plotly.express as px

  funnel_data = {
      "Stage": ["Budget", "Impressions", "Clicks", "Conversions", "Revenue"],
      "Value": [roi['budget'], roi['impressions'], roi['clicks'], roi['conversions'], roi['est_revenue']],
  }
  fig = px.funnel(funnel_data, x='Value', y='Stage', title='ROI Performance Funnel')
  st.plotly_chart(fig, use_container_width=True)
  ```

  Below the funnel, show a **confidence band** indicator:
  ```python
  st.metric("Expected ROA", f"{roi['roa_expected']}×", delta=f"Range: {roi['roa_low']}× – {roi['roa_high']}×")
  st.caption(roi['confidence_note'])
  ```

#### 7G — LLM Content Strategy Display
  When a user selects an influencer from a `st.selectbox` populated from `top5_df`:
  1. Load pre-generated strategy from `strategy_texts[channel_id]` (already in memory from Step 6B)
  2. Render strategy with `st.markdown(strategy_text)` — the LLM returns clean Markdown with headers, which Streamlit renders natively
  3. Add a `st.download_button("Download Strategy Brief", strategy_text, file_name=f"{channel_title}_strategy.md")` for export

#### 7H — Competitive Differentiation Panel
  Render the `bias_report` as a side-by-side comparison table:
  - Left column: "What traditional tools recommend" (Degree-only top 5 by follower count)
  - Right column: "What AI-MCN recommends" (Betweenness-weighted top 5)
  - Highlight channels that appear only in the AI-MCN column as "Hidden Gems"
  - Display `bias_report['narrative']` as a callout block (`st.info(...)`) — this is a key business value statement for brand stakeholders
  - If `red_flags` were populated by the Channel Enrichment Agents (Step 5F) for any Top 5 pick, display them as `st.warning()` banners inline with that influencer's card

---

#### Step 7I — 🤖 Subagent: Executive Synthesis Agent

> **Skill file:** `subagents/SKILL_ExecutiveSynthesisAgent.md`

> **Why a subagent here:** By Step 7H, the dashboard contains rich but fragmented outputs —
> five content strategies, an ROI simulation, a bias audit, SNA centrality scores, and a
> competitive differentiation table. A brand manager should not need to synthesize these
> mentally. The Executive Synthesis Agent reads the entire pipeline output and produces a
> single, coherent, one-page **Brand Partnership Recommendation Memo** in Markdown — the
> document a real CMO would hand to their team to action. This is the final intelligence
> layer of the system and the strongest demonstration of LLM value in the project.

- **File:** `orchestrator.py` → `run_executive_synthesis_agent(top5_df, strategy_texts, roi_result, bias_report, brand_params)`
- **Trigger:** Called once after all Content Strategy Agents complete. Sequential — it needs all prior outputs.
- **Input:** All pipeline outputs aggregated into one structured prompt
- **Output:** `brand_memo.md` — downloadable from the dashboard via `st.download_button`

```python
# orchestrator.py

SYNTHESIS_SYSTEM = """
You are a Chief Marketing Officer writing a concise, executive-grade influencer
partnership recommendation memo. You receive structured data outputs from an AI
matching system and translate them into a clear, actionable business document.
Write in confident, direct prose. Use Markdown headers and tables where appropriate.
Never pad with generic marketing language. Every sentence must reference specific data.
"""

SYNTHESIS_PROMPT = """
You have completed an AI-powered influencer matching analysis for the following brand.
Synthesise all outputs into a one-page Brand Partnership Recommendation Memo.

## Brand
{brief}

## Top 5 Recommended Influencers
{top5_table}

## ROI Simulation (at ${budget:,} budget)
- Estimated Impressions: {impressions:,}
- Estimated Clicks: {clicks:,}
- Estimated Conversions: {conversions:,}
- Expected ROA: {roa_expected}× (range: {roa_low}× – {roa_high}×)

## AI Competitive Differentiation
{bias_narrative}

## Content Strategy Summaries (one sentence each)
{strategy_summaries}

## Memo Requirements
1. **Executive Summary** (3 sentences max) — why these 5 influencers, what ROA to expect
2. **Priority Recommendation** — single top pick with one-paragraph justification citing SNA score, semantic alignment, and tone match
3. **Campaign Structure** — how to deploy all 5 across a 4-week campaign timeline
4. **Risk Flags** — any red flags surfaced by the AI analysis that the brand team should address
5. **Next Steps** — 3 concrete action items for the brand team

Format as clean Markdown. Keep the entire memo under 600 words.
"""

def run_executive_synthesis_agent(
    top5_df:       pd.DataFrame,
    strategy_texts: dict,
    roi_result:    dict,
    bias_report:   dict,
    brand_params:  dict,
) -> str:
    cache_path = f"cache/brand_memo_{hash(brand_params['brief_md'])}.md"
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return f.read()

    # Build top5 table string
    top5_table = top5_df[['title', 'subscriber_count', 'confidence_score_final',
                            'semantic_score', 'engagement_ratio', 'alignment_rationale']].to_markdown(index=False)

    # Build one-sentence strategy summaries
    strategy_summaries = "\n".join(
        f"- **{top5_df.loc[i, 'title']}:** {strategy_texts.get(row['channel_id'], '')[:200].strip().split(chr(10))[0]}"
        for i, row in top5_df.iterrows()
    )

    prompt = SYNTHESIS_PROMPT.format(
        brief              = brand_params["brief_md"],
        top5_table         = top5_table,
        budget             = int(brand_params.get("budget", 0)),
        impressions        = roi_result.get("impressions", 0),
        clicks             = roi_result.get("clicks", 0),
        conversions        = roi_result.get("conversions", 0),
        roa_expected       = roi_result.get("roa_expected", "N/A"),
        roa_low            = roi_result.get("roa_low", "N/A"),
        roa_high           = roi_result.get("roa_high", "N/A"),
        bias_narrative     = bias_report.get("narrative", ""),
        strategy_summaries = strategy_summaries,
    )

    try:
        client   = Groq()
        response = client.chat.completions.create(
            model      = "llama-3.3-70b-versatile",
            max_tokens = 900,
            messages   = [
                {"role": "system", "content": SYNTHESIS_SYSTEM},
                {"role": "user",   "content": prompt},
            ],
        )
        memo = response.choices[0].message.content
        os.makedirs("cache", exist_ok=True)
        with open(cache_path, "w") as f:
            f.write(memo)
        return memo

    except Exception as e:
        print(f"[ExecutiveSynthesisAgent] Failed: {e}")
        return f"# Memo Unavailable\n\nAPI error during synthesis: {e}"
```

- **Streamlit rendering in `app.py`:**
  ```python
  with st.expander("📄 Executive Brand Partnership Memo", expanded=True):
      st.markdown(brand_memo)
      st.download_button(
          label     = "Download Memo as Markdown",
          data      = brand_memo,
          file_name = f"{brand_params['name']}_partnership_memo.md",
          mime      = "text/markdown",
      )
  ```

---

### Orchestrator Entry Point (`orchestrator.py`)

The full pipeline is coordinated by a single public function that `app.py` calls after the
Streamlit form is submitted. This keeps `app.py` clean and makes the pipeline independently
testable:

```python
# orchestrator.py — public entry point

def run_full_pipeline(brand_params: dict, master_df: pd.DataFrame) -> dict:
    """
    Orchestrates the full Phase 2–3 subagent pipeline.
    Returns a single result dict containing all outputs needed by app.py.

    Execution order:
      1. BrandIntelligenceAgent       (sequential)
      2. SNA + TF-IDF + Engagement    (sequential, pure Python)
      3. ChannelEnrichmentAgents ×20  (parallel async)
      4. Final Top 5 selection        (sequential, pure Python)
      5. ROI simulation               (sequential, pure Python)
      6. ContentStrategyAgents ×5     (parallel async)
      7. ExecutiveSynthesisAgent      (sequential)
    """
    # Step 1 — Brand Intelligence
    brand_enrichment = run_brand_intelligence_agent(brand_params)
    brand_params["enrichment"] = brand_enrichment

    # Steps 2–4 — Scoring pipeline (in matching_roi.py)
    master_df, G, top5_df, bias_report = run_scoring_pipeline(master_df, brand_params)

    # Step 5 — ROI simulation (single influencer — default to rank-1)
    roi_result = simulate_roi(
        budget    = brand_params["budget"],
        avg_views = top5_df.iloc[0].get("avg_views", 0),
    )

    # Step 6 — Content strategies (parallel)
    strategy_texts = asyncio.run(
        run_content_strategy_agents(top5_df, brand_params)
    )

    # Step 7 — Executive memo (sequential, needs all prior outputs)
    brand_memo = run_executive_synthesis_agent(
        top5_df, strategy_texts, roi_result, bias_report, brand_params
    )

    return {
        "top5_df":        top5_df,
        "G":              G,
        "bias_report":    bias_report,
        "roi_result":     roi_result,
        "strategy_texts": strategy_texts,
        "brand_memo":     brand_memo,
        "brand_params":   brand_params,
    }
```

---

## File Ownership Summary

| File | Owner | Inputs | Outputs |
|------|-------|--------|---------|
| `data_collection.py` | Person A | Keywords | `channels_raw.csv` |
| `sna_analysis.py` | Person A | `channels_raw.csv` | `channels_scored.csv` + graph object `G` |
| `matching_roi.py` | Person B | `channels_scored.csv` + `brand_params` | `top5_df` + `roi_result` + `bias_report` |
| `llm_content.py` | Person C | `top5_df` + `brand_params` | LLM strategy strings + `cache/` |
| `orchestrator.py` | Person C | All module outputs | Full result dict for `app.py` |
| `app.py` | Person D | `orchestrator.run_full_pipeline()` result | Full Streamlit dashboard |
| `utils.py` | All | — | Shared helpers: `select_existing`, `normalize_score`, `build_community_color_map` |

## Critical Path

> **Before writing any code:** Read `AI-MCN_CostControl.md`. Get a free `GROQ_API_KEY` at
> [console.groq.com](https://console.groq.com) (no credit card). Add it to `.env` alongside
> `MOCK_MODE=true`. Every pipeline run during development costs $0. Flip `MOCK_MODE=false`
> only for the single cache-warming run on Friday night. Total project API spend: **$0.00**.

1. Person A must export `channels_scored.csv` by **Thursday EOD** — Person B is fully blocked until then.
2. Person B must finalize `top5_df` schema by **Friday morning** — Persons C and D depend on it.
3. Person C must finalize `orchestrator.py` and pre-cache all subagent outputs by **Friday night**:
   - `cache/brand_intel_*.json` — Brand Intelligence Agent outputs
   - `cache/enrich_*.json` — Channel Enrichment Agent outputs (×20)
   - `cache/{channel_id}_strategy.md` — Content Strategy Agent outputs (×5)
   - `cache/brand_memo_*.md` — Executive Synthesis Agent output
4. All LLM outputs must be pre-cached by **Friday night** — live API calls during the demo are a risk.
5. No new features after **Saturday morning** — integration and polish only.
