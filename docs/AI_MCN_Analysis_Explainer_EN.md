# AI-MCN Analysis Explainer (English)

This document explains, in plain language, exactly how your Streamlit prototype works from input to output.
It is based on the current code in `app.py` and `src/`.

## 1) One-line summary

Your campaign input does **not** trigger live web research.  
It is used as a scoring/query brief that filters and re-ranks channels already present in your CSV data.

## 2) End-to-end flow (input -> output)

```text
Campaign Input Form
  -> Build BrandBrief + runtime config
  -> Load data CSVs (full if present, demo if not)
  -> Clean/filter videos + aggregate channels
  -> Build channel graph from shared tags
  -> Compute SNA scores + communities
  -> (Optional) ML benchmark + channel ML potential score
  -> TF-IDF text relevance scoring
  -> Semantic/tone enrichment on top candidates
  -> Final score + reliability penalty + diversity guardrail
  -> Top-N recommendations + benchmark + ROI + strategy + memo
  -> Render tabs (Overview, Top Matches, Network Studio, etc.)
```

## 3) Which data is used (full vs demo)

The app/pipeline auto-selects files in this order:

- Videos: `data/videos_text_ready_combined.csv` -> fallback `data/videos_text_ready_demo.csv`
- Comments: `data/comments_raw_combined.csv` -> fallback `data/comments_raw_demo.csv`
- Master channel stats: `data/master_prd_slim_combined.csv` -> fallback `data/master_prd_slim_demo.csv`

So on your local machine, if `*_combined.csv` exists, full data is used.

## 4) Campaign Input: where each field goes

| Input field | Used where | Practical effect |
|---|---|---|
| Brand Name, Product Name, Category, Audience, Goal, USP, Market | `BrandBrief` for text/semantic query | Changes what “fit” means in text/semantic scoring and generated strategy/memo text |
| Budget | ROI tab + benchmark budget alignment | Changes simulated ROI numbers (impressions/clicks/conversions/ROAS) |
| Must-Have Keywords | Data prep + text scoring + semantic scoring + keyword matrix | Adds include filter terms, boosts channels that contain terms |
| Excluded Keywords | Data prep + text scoring + semantic scoring | Removes noisy videos in preprocessing and penalizes channels with excluded terms |
| Top-N Default | Ranking config | Sets default recommendation size and semantic pre-candidate size |
| Min Shared Tags per Edge | Network graph builder | Higher value = stricter edges, sparser graph |
| Max Tag Coverage Ratio | Network graph builder | Drops over-common tags to avoid “everyone connected to everyone” |
| Min Community Size | Community post-processing | Small communities are reassigned to `-1` (micro/other) |
| Enable ML Benchmark Block | Pipeline | Turns ML training block on/off |
| ML model selection | ML Studio rerun / pipeline | Chooses model families for 5-fold CV |
| Run CeraVe Benchmark | Pipeline | Runs second pass with fixed CeraVe brief and compares top-score averages |

## 5) Detailed pipeline logic

## 5.1 Data preparation (`src/data_prep.py`)

Video-level steps:

1. Deduplicate by `_video_id`
2. Parse numeric metrics (`viewCount`, `likeCount`, `commentCount`)
3. Build `full_text = title + description + tags`
4. Include filter: beauty keywords + your must keywords
5. Exclude filter: noise keywords + your excluded keywords
6. Basic metric guardrails (`views > 0`, likes/comments non-negative)
7. Build engagement target for ML:
   - `engagement_rate = (likes + comments + 1) / (views + 100)`
   - `engagement_target = log1p(engagement_rate)`
8. Build helper features for ML:
   - recency, title length, description length, hashtag count, tag count, log views/likes/comments

Comment-level steps:

- Deduplicate by `_comment_id`, parse like count/date/text length.

Channel-level aggregation:

- `n_videos`, `median_views`, `median_likes`, `median_comments`, `mean_engagement`, latest publish date
- representative video id
- aggregated tag list
- `channel_text` (used by TF-IDF/semantic)
- comment stats (count, mean likes, median length)

## 5.2 Network graph (`src/network_scoring.py`)

Nodes:

- one node per `_channel_id`

Edges:

- channels are connected when they share enough tags
- edge weight = number of shared tags
- keep edge only when `weight >= min_shared_tags`
- drop tags that appear in too many channels using:
  - hard cap: `max_channels_per_tag` (default 150)
  - ratio cap: `max_tag_channel_ratio * n_nodes`
  - effective cap = min(hard cap, ratio cap)

## 5.3 Network scores

For each channel:

- `degree_centrality`
- `betweenness_centrality` (proxy)
- `eigenvector_centrality` (implemented as normalized node strength proxy)
- combined:
  - `sna_score_raw = 0.33*degree + 0.34*betweenness_proxy + 0.33*eigenvector_proxy`
  - `sna_score = min-max scale(sna_score_raw)`

Communities:

- label-propagation style assignment
- communities smaller than `min_community_size` become `community_id = -1`

## 5.4 ML benchmark block (`src/ml_modeling.py`)

Only runs if enabled.

Target:

- video-level `engagement_target = log1p(engagement_rate)`

Features:

- numeric only (8 features): `log_views, log_likes, log_comments, days_since_publish, title_len, desc_len, hashtag_count, tag_count`
- standardized via `StandardScaler`

Validation:

- `GroupKFold(n_splits=5)` grouped by channel id (prevents leakage across videos from same channel)

Model candidates:

- LinearRegression, LASSO, Ridge, CART, RandomForest, LightGBM (if installed)

Outputs:

- CV metrics (`RMSE`, `MAE`, `R2`)
- best model by lowest CV RMSE
- per-channel `ml_pred_engagement` (median prediction across that channel’s videos)
- `ml_potential_score = min-max scale(ml_pred_engagement)`
- SHAP summary/dependence (tree model + SHAP installed)

Important gate:

- ML is only included in final ranking when best model beats BaselineMedian by at least 2% RMSE gain.

## 5.5 Text relevance scoring (`src/text_scoring.py`)

TF-IDF setup:

- Corpus: each channel’s `channel_text`
- Query: full brand brief text + must keywords
- Similarity: cosine similarity(channel_text, query)

Keyword adjustment:

- `keyword_boost = 0.08*(must-hit count) - 0.12*(excluded-hit count)`
- `tfidf_similarity = min-max scale(raw_similarity + keyword_boost)`

## 5.6 Semantic/tone enrichment (`src/semantic_enrichment.py`)

Runs on top pre-candidates only (default top 30 or `3 * top_n`, whichever is larger).

For each pre-candidate:

- semantic base from TF-IDF similarity to brief
- adjustment:
  - `+0.04 * must_hit`
  - `-0.08 * exclude_hit`
- clamp to `[0, 1]` -> `semantic_score`

Tone matching:

- if goal includes conversion: looks for terms like `review, demo, before after, results, routine`
- otherwise: `story, favorites, tips, routine, guide`
- score = hit ratio over tone terms

Red flags generated when:

- excluded terms detected
- semantic score < 0.20
- `n_videos < 5`

## 5.7 Final ranking and reliability controls (`src/ranking.py`)

Step A: base signals

- `engagement_score = min-max scale(mean_engagement)`

Evidence/reliability:

- `scale_score = min-max scale(log1p(median_views))`
- `activity_score = min-max scale(log1p(n_videos))`
- `interaction_score = min-max scale(log1p(median_likes + median_comments))`
- `evidence_score = 0.55*scale + 0.30*activity + 0.15*interaction`

Reliability multiplier:

- `credibility_multiplier = clip(0.35 + 0.65*evidence_score, 0.20, 1.00)`
- extra severe penalty for very weak channels:
  - if `median_views < 100` and `median_likes <= 1` and `median_comments <= 1`
  - multiply multiplier by `0.30`
- final clip: `[0.08, 1.00]`

Eligibility guard:

- channel is “eligible” if any of:
  - `evidence_score >= 0.20`
  - `median_views >= 500`
  - `n_videos >= 12`

Weighted final score:

- If ML is active:
  - `0.30*SNA + 0.20*TFIDF + 0.15*Semantic + 0.10*Tone + 0.15*Engagement + 0.10*ML`
- If ML inactive:
  - `0.34*SNA + 0.24*TFIDF + 0.18*Semantic + 0.10*Tone + 0.14*Engagement + 0.00*ML`

Then:

- `final_score_base = weighted_sum`
- `final_score = final_score_base * credibility_multiplier`

Diversity guardrail:

- after sorting, selection tries to meet minimum community diversity (default 3 communities) for top-N

## 5.8 Channel details and media enrichment

From `src/channel_details.py`:

- channel profile text (longest description sample)
- top keyword summary from tags
- recent video titles (default 3)
- best video title + views + url
- recent comments (default 3)
- top liked comment
- estimated subscribers/video count (from master CSV when available)

From `src/channel_media.py`:

- channel thumbnail (YouTube API if `YOUTUBE_API_KEY` exists)
- fallback to representative video thumbnail
- channel and representative video URLs

## 5.9 Benchmark block

If enabled, pipeline also runs ranking with a fixed CeraVe brief.
Dashboard compares:

- anchor brand Top-N mean score vs CeraVe Top-N mean score
- score gap = anchor minus benchmark

## 5.10 ROI, Content Strategy, Executive Memo

ROI (`src/roi_simulation.py`):

- `impressions = (budget / cpm) * 1000`
- `clicks = impressions * ctr`
- `conversions = clicks * cvr`
- `revenue = conversions * aov`
- `roas = revenue / budget`
- range shown as `0.7x` to `1.3x` around base ROAS

Content strategy (`src/content_generation.py`):

- if `OPENAI_API_KEY` exists, generate per-channel strategy with OpenAI
- else use deterministic fallback templates
- app also auto-creates 3 thumbnail hook ideas per channel

Executive memo:

- markdown memo generated from top channels + ROI + risk flags + next steps

## 6) What each dashboard tab does

## Overview

- campaign snapshot
- top-level metrics
- reliability banner (avg evidence score)
- optional benchmark panel

## Top Matches

- filter by min match score and min evidence
- choose ranking strategy preset
- choose display Top-N
- optional diversity preview/guardrail
- card-level explanation of each channel with detailed signals

Ranking strategy presets in this tab:

- Model Default: uses pipeline `final_score`
- Network-first / Keyword-first / Performance-first:
  - recomputes display score using preset weights
  - still multiplied by reliability multiplier

## Network Studio

- interactive network graph (zoom/pan/hover)
- community distribution
- graph metadata
- bias report:
  - overlap between degree-only ranking and final hybrid ranking

## Text Intelligence

- scatter map: TF-IDF vs Semantic (color = evidence)
- top frequent terms from top channels
- keyword coverage matrix and chart
- TF-IDF/semantic leaderboard

## ML Studio

- CV benchmark chart/table
- rerun with selected model set
- predicted vs actual scatter
- SHAP summary/dependence if available

## ROI Lab

- interactive scenario sliders (budget, CPM, CTR, CVR, AOV)
- funnel and budget sensitivity curves

## Content Strategy

- per-channel strategy cards
- tabbed structure from generated markdown sections
- creative hook cards

## Executive Memo

- structured memo sections
- download markdown/txt

## Glossary

- client-facing definitions of core terms

## 6.1 Top Matches: exact recommendation flow in the UI

When you open **Top Matches**, the app does this in order:

1. Start from `result["scored_df"]` (already scored by pipeline).
2. Build `display_score`:
   - `Model Default` -> `display_score = final_score`
   - other presets -> recompute weighted score from component signals, then multiply by `credibility_multiplier`
3. Apply user filters:
   - keep rows where `display_score >= Min Match Score`
   - keep rows where `evidence_score >= Min Evidence`
4. Sort by `display_score` descending.
5. If diversity preview is enabled and applied:
   - temporarily set `final_score = display_score`
   - run diversity selector (`select_top_with_diversity`)
6. Trim to `Display Top-N`.
7. Render cards + charts + detailed table.

Important:

- `display_score` is what the Top Matches tab ranks by.
- `final_score` is the pipeline-native score.
- These can differ when you pick Network-first / Keyword-first / Performance-first.

## 6.2 Ranking strategies in Top Matches (actual weights)

If strategy is not `Model Default`, the app uses these weights:

| Strategy | SNA | TF-IDF | Semantic | Tone | Engagement | ML |
|---|---:|---:|---:|---:|---:|---:|
| Network-first | 0.46 | 0.16 | 0.14 | 0.08 | 0.14 | 0.02 |
| Keyword-first | 0.20 | 0.42 | 0.18 | 0.08 | 0.10 | 0.02 |
| Performance-first | 0.20 | 0.12 | 0.16 | 0.08 | 0.38 | 0.06 |

Then:

- If ML is disabled in this run, ML weight is set to 0 and all weights are renormalized.
- Final tab ranking score is:
  - `display_score = weighted_sum * credibility_multiplier`

## 6.3 Match labels and reliability labels (card badges)

Fit label by score (`display_score`):

- `>= 0.65`: Very Strong Match
- `>= 0.45`: Strong Match
- `>= 0.30`: Moderate Match
- `< 0.30`: Exploratory

Evidence label by `evidence_score`:

- `>= 0.60`: High Evidence
- `>= 0.35`: Medium Evidence
- `< 0.35`: Low Evidence

These are UI interpretation buckets; they are not additional model training classes.

## 6.4 How “Why this creator” sentence is generated

The plain-language sentence checks thresholds:

- TF-IDF >= 0.55 -> “channel language closely matches your brand keywords”
- SNA >= 0.55 -> “creator sits near the center of the relevant creator network”
- Engagement >= 0.45 -> “audience interaction quality is healthy”
- Semantic >= 0.45 -> “brand tone and content style are aligned”

If none of these pass, it shows a cautionary exploratory message.

## 6.5 Top Matches card: field-by-field meaning

Score and controls:

- `Final Match Score`: score used for ranking in current tab (`display_score`)
- `Signal Breakdown`: component signals used in weighted sum
- `Score Controls`: 
  - `Base` = `final_score_base` before reliability penalty
  - `Reliability x...` = `credibility_multiplier`
  - `Community` = cluster id used for diversity

Observed evidence fields:

- `Videos Used`: unique videos per channel in filtered dataset (`n_videos`)
- `Median Views/Likes`: robust central tendency, less noisy than mean
- `Comments Collected`: sampled/available comments tied to channel

Freshness fields:

- `Latest publish` and `Days since latest` = recency signals for activity context

Content context fields:

- `Channel Snapshot`: extracted profile-like description text
- `Channel Keywords`: top tags/keywords summary
- `Best Video in Dataset`: highest-view video from available dataset slice
- `Recent Video Titles`, `Recent Audience Comments`, `Top Liked Audience Comment`: qualitative context for reviewers

Risk/context fields:

- `Model Rationale`: semantic/tone rationale string from enrichment module
- `red_flags`: warnings such as excluded keyword hits, low semantic relevance, low activity

## 6.6 Graph interpretation guide (all major charts)

### A) Top Influencer Score Breakdown (Top Matches)

- X-axis: channel title
- Y-axis: component score (0-1)
- Color: signal type (SNA/TF-IDF/Semantic/Tone/Engagement/ML)
- Use case: quickly see why two channels with similar final score differ in composition.

Interpretation tip:

- High SNA + low TF-IDF means structurally influential but weaker campaign-language fit.
- High TF-IDF + low evidence can indicate keyword fit with weaker observed performance base.

### B) Influencer Network Graph (Network Studio)

Node meaning:

- One node = one channel
- Node color = `community_id`
- Node size = `8 + 28 * max(final_score, 0)` in plotting logic

Edge meaning:

- One edge = channels sharing tags
- Edge inclusion depends on `Min Edge Strength` slider (minimum shared-tag count)

Selection logic:

- Graph tries to show top-scoring nodes first.
- If too sparse, it falls back to a broader edge subset so the graph remains visible.

How to read:

- Big node near dense cluster center: strong candidate with many topical ties.
- Isolated node: niche creator or sparse tag overlap.

### C) Community Distribution Bar (Network Studio)

- X-axis: community id
- Y-axis: number of channels in each community
- If `Include micro/isolated` is off, micro clusters (`-1`) are excluded.

Use case:

- Detect concentration risk (one community dominating shortlist).

### D) Text Match Map (Text Intelligence)

- X-axis: TF-IDF similarity (keyword/lexical fit)
- Y-axis: Semantic score (meaning-level fit)
- Color: evidence score
- Bubble size: transformed median views

Quadrant guide:

- Upper-right: strongest language + meaning alignment
- Upper-left: semantic alignment but weaker direct keyword overlap
- Lower-right: keyword overlap without deeper semantic fit
- Lower-left: weak fit candidates

### E) Top Terms and Keyword Coverage (Text Intelligence)

Top Terms chart:

- Shows frequently occurring terms in top candidate text corpus.
- Helps verify if shortlist language reflects campaign context.

Keyword Coverage chart:

- Coverage rate = share of top channels containing a keyword.
- Low coverage on a “must” keyword means you may need to adjust query terms or data scope.

### F) ML Studio charts

CV RMSE bar:

- Lower RMSE is better.
- Compare each model to `BaselineMedian` reference row.

Predicted vs Actual:

- 45-degree dashed line = perfect prediction.
- Wide scatter away from diagonal means weaker predictive precision.

SHAP summary:

- Mean absolute SHAP value = average feature impact magnitude.
- Higher means more influence on model predictions.

SHAP dependence:

- X = feature value, Y = SHAP contribution.
- Shows directionality: whether higher feature values push prediction up or down.

### G) ROI Lab charts

ROI Funnel:

- Sequential projection from impressions -> clicks -> conversions -> revenue.
- Not causal attribution; assumption-driven scenario output.

Budget sensitivity:

- X = budget, left Y = ROAS, right Y = conversions.
- Useful for planning tradeoffs (efficiency vs scale).

## 6.7 Why chart reading and score reading can disagree

Sometimes users see a strong bar/cluster but lower final rank. Typical reasons:

1. Reliability penalty reduced final score (`credibility_multiplier`).
2. Diversity guardrail replaced a same-community candidate.
3. Current tab strategy uses `display_score` (not pipeline default `final_score`).
4. Min Evidence filter removed otherwise high-fit channels.

When debugging a recommendation, always inspect in this order:

1. `display_score` and strategy preset
2. `evidence_score` and `credibility_multiplier`
3. community id and diversity settings
4. red flags and semantic rationale

## 7) Why a low-view channel can still appear

It can happen when text/network fit is high but evidence is weak.  
The system already penalizes weak evidence via `credibility_multiplier` and `eligible_recommendation`.

If you still want stricter results in demos:

1. Increase `Min Evidence` slider in Top Matches
2. Increase `Min Match Score`
3. Use `Performance-first` strategy
4. Keep diversity guardrail on, but review if it forces low-evidence picks in sparse communities

## 8) Common misconceptions

- "Does it research my brand from the live internet?"  
  - No. Campaign input is a query/constraint against your existing CSV dataset.

- "Does Brand Name alone change scores a lot?"  
  - Mostly through text in the brief. The strongest direct levers are must/exclude keywords + goal + audience wording.

- "Are ROI numbers causal predictions?"  
  - No. They are scenario simulations from your funnel assumptions.

- "Is ML always used in final ranking?"  
  - No. Only when CV gain over baseline is >= 2%.

## 9) Quick field glossary (important scores)

| Field | Meaning |
|---|---|
| `sna_score` | network influence structure score |
| `tfidf_similarity` | lexical match to campaign brief |
| `semantic_score` | meaning-level fit after enrichment |
| `tone_match_score` | style/goal tone compatibility |
| `engagement_score` | normalized observed engagement quality |
| `ml_potential_score` | model-predicted engagement upside |
| `evidence_score` | reliability based on scale/activity/interaction |
| `credibility_multiplier` | down-weight factor for weak evidence |
| `final_score_base` | weighted sum before reliability penalty |
| `final_score` | final ranking score after reliability multiplier |

## 10) Where outputs are saved

- Top-N CSV: `artifacts/reports/top{N}_{brand}.csv`
- All scored channels CSV: `artifacts/reports/scored_channels_{brand}.csv`
- Memo: `artifacts/reports/memo_{brand}.md`
- ML results: `artifacts/reports/ml_cv_results.csv`
- Cached strategy/media: `artifacts/cache/`
