# AI-MCN Full Analysis Explainer (English)

This document is a full beginner-friendly walkthrough of how this project works.
It explains the entire flow from data loading and cleaning to scoring, modeling, recommendation, and dashboard interpretation.

Audience:
- Teammates who did not build the code
- Presentation prep and Q&A prep
- Anyone who wants to audit how recommendations are produced

Scope:
- This is based on the current implementation in `app.py` and `src/*`.
- It describes what the system actually does now (not future ideas).

---

## 0) Big picture in one minute

The system takes a campaign brief and ranks influencer channels from your existing dataset.

It does this by combining:
- Network influence structure
- Text relevance to campaign language
- Semantic/tone alignment
- Observed engagement behavior
- Optional ML predicted potential
- Reliability penalty and diversity controls

Output is not only a ranked list, but also:
- Why each channel was recommended
- Risk flags
- Benchmark comparison
- ROI scenario outputs
- Strategy/memo exports

Important:
- Campaign input does not run live internet brand research.
- Campaign input acts as query constraints and scoring context against your existing CSVs.

---

## 1) Repository map (where logic lives)

Core application:
- `app.py`: Streamlit UI, controls, tab rendering, interactive charts

Pipeline orchestrator:
- `src/orchestrator.py`: end-to-end execution order

Data prep:
- `src/data_prep.py`: cleaning, filtering, feature prep, channel aggregation

Network analysis:
- `src/network_scoring.py`: graph build, centrality, communities

Text analysis:
- `src/text_scoring.py`: TF-IDF similarity and keyword boost/penalty
- `src/semantic_enrichment.py`: semantic/tone enrichment on top candidates

ML modeling:
- `src/ml_modeling.py`: model suite, GroupKFold CV, baseline comparison, SHAP

Ranking and guardrails:
- `src/ranking.py`: final score formula, reliability multiplier, diversity selector

ROI simulation:
- `src/roi_simulation.py`

Content outputs:
- `src/content_generation.py`: strategy text and executive memo

Detail enrichment:
- `src/channel_details.py`: profile/recent video/comments details
- `src/channel_media.py`: channel image/channel URL/video URL

Data path and bootstrap:
- `src/config.py`: path resolution (combined first, demo fallback)
- `src/data_bootstrap.py`: Google Drive auto-download for full CSVs

---

## 2) Data loading logic (full vs demo vs Google Drive)

### 2.1 Priority order

At runtime, the system resolves each data file in this order:

1. `data/videos_text_ready_combined.csv` else `data/videos_text_ready_demo.csv`
2. `data/comments_raw_combined.csv` else `data/comments_raw_demo.csv`
3. `data/master_prd_slim_combined.csv` else `data/master_prd_slim_demo.csv`

So if combined files exist locally, full data is used.

### 2.2 Cloud-friendly full data bootstrap

Before loading CSVs, pipeline calls Google Drive bootstrap logic.

Supported secret/env patterns:
- Folder-level:
  - `GDRIVE_FOLDER_URL` or `GDRIVE_FOLDER_ID`
- File-level:
  - `GDRIVE_VIDEOS_FILE_ID` / `GDRIVE_VIDEOS_URL`
  - `GDRIVE_COMMENTS_FILE_ID` / `GDRIVE_COMMENTS_URL`
  - `GDRIVE_MASTER_FILE_ID` / `GDRIVE_MASTER_URL`

Current repo default:
- If no `GDRIVE_*` is set, code falls back to a built-in folder URL.

### 2.3 Expected files in Drive folder

These exact filenames must exist in the folder:
- `videos_text_ready_combined.csv`
- `comments_raw_combined.csv`
- `master_prd_slim_combined.csv`

---

## 3) Campaign input: what matters and how strongly

Input fields in landing form:
- Brand Name
- Product Name
- Product Category
- Target Audience
- Campaign Goal
- Core Message / USP
- Budget
- Market
- Must-have keywords
- Excluded keywords
- Top-N default
- Graph thresholds and community settings
- ML toggle and model choices
- Benchmark toggle

Practical impact level:

High impact:
- Must keywords
- Excluded keywords
- Campaign goal
- Graph controls (`min_shared_tags`, `max_tag_ratio`, `min_community_size`)

Medium impact:
- Target audience text
- USP text

Low impact (current implementation):
- Brand name only
- Product name only
- Market text only

Budget impact:
- Strongly affects ROI tab outputs
- Does not directly change core ranking score formula

---

## 4) End-to-end pipeline sequence (actual runtime order)

1. Build `BrandBrief` from input
2. Prepare data (videos/comments/channels)
3. Build channel graph from shared tags
4. Compute SNA scores and communities
5. Optional ML suite to produce `ml_potential_score`
6. Text scoring (TF-IDF + keyword boost/penalty)
7. Pre-rank to get top candidates
8. Semantic/tone enrichment only on top candidates
9. Merge semantic outputs back
10. Final ranking with reliability penalty and diversity guardrail
11. Build detail/media enrichment fields
12. Optional benchmark run (CeraVe brief)
13. ROI simulation
14. Strategy and memo generation
15. Persist artifacts (CSV, memo, ML table)
16. Render dashboard tabs

---

## 5) Data preparation details

### 5.1 Video-level cleaning

In `prepare_videos`:

- Deduplicate by `_video_id`
- Convert numeric columns:
  - `statistics__viewCount`
  - `statistics__likeCount`
  - `statistics__commentCount`
- Parse publication timestamp
- Build normalized text fields:
  - `video_title`, `video_description`, `tags_list`, `tags_text`, `full_text`

### 5.2 Include/exclude filtering

Include terms = built-in beauty terms + campaign `must_keywords`

Exclude terms = built-in noise terms + campaign `exclude_keywords`

Then keep rows where:
- include hit is true
- exclude hit is false

### 5.3 Hard metric guardrails

Keep rows with:
- `viewCount > 0`
- likes/comments non-negative

### 5.4 Engagement target for ML

Formulas:
- `engagement_rate = (likes + comments + 1.0) / (views + 100.0)`
- `engagement_target = log1p(engagement_rate)`

### 5.5 Additional features

Creates:
- `days_since_publish`
- `title_len`, `desc_len`
- `hashtag_count`, `tag_count`
- `log_views`, `log_likes`, `log_comments`

### 5.6 Comment preparation

In `prepare_comments`:
- Deduplicate by `_comment_id`
- Parse `comment_like_count`
- Parse timestamp
- Build `comment_len`

### 5.7 Channel table aggregation

Grouped by channel id and channel title:
- `n_videos`
- `median_views`
- `median_likes`
- `median_comments`
- `mean_engagement`
- `latest_publish`

Additional channel fields:
- representative video id (highest-view video)
- all tags (flattened)
- `channel_text` (used for text scoring)
- comment stats merged (`comments_n`, mean likes, median length)

---

## 6) Network analysis details

### 6.1 Graph construction

Node:
- one node per channel

Edge:
- connect two channels when they share tags
- edge weight = number of shared tags

Noise control:
- drop tags appearing in too many channels
- effective cap per tag = `min(max_channels_per_tag, ratio_cap)`
- keep edges where `weight >= min_shared_tags`

### 6.2 Centrality features

Computed from adjacency:
- `degree_centrality`
- `betweenness_centrality` (proxy)
- `eigenvector_centrality` proxy (normalized strength)

SNA composite:
- `sna_score_raw = 0.33*degree + 0.34*betweenness + 0.33*eigenvector`
- `sna_score = min-max(sna_score_raw)`

### 6.3 Community detection

- Label propagation style assignment
- Communities below `min_community_size` become `community_id = -1`
- Remaining community ids are reindexed

---

## 7) Text analysis details

### 7.1 TF-IDF relevance

- Corpus: each channel's `channel_text`
- Query: full brand brief markdown + must keywords
- Similarity: cosine similarity between channel vector and query vector

### 7.2 Keyword boost/penalty

For each channel text:
- `must_hit = count(must terms found)`
- `exclude_hit = count(exclude terms found)`
- `keyword_boost = 0.08*must_hit - 0.12*exclude_hit`

Then:
- `tfidf_similarity = min-max(raw_similarity + keyword_boost)`

---

## 8) Semantic/tone enrichment details

Applied only to preselected top candidates (faster and focused).

### 8.1 Semantic score

Base similarity + adjustments:
- `+0.04 * must_hit`
- `-0.08 * exclude_hit`

Clamp to `[0, 1]`.

### 8.2 Tone score

Tone dictionary depends on campaign goal:
- Conversion-oriented goal uses terms like `review`, `demo`, `before after`, `results`, `routine`
- Awareness-oriented goal uses terms like `story`, `favorites`, `tips`, `guide`

Tone match = ratio of tone terms found in channel text.

### 8.3 Red flags

Generated when:
- excluded keyword signals appear
- semantic score is very low (`<0.20`)
- low channel activity (`n_videos < 5`)

---

## 9) ML modeling details

### 9.1 Why this block exists

Purpose:
- Test if model-based engagement prediction gives measurable improvement over naive baseline
- Provide optional ML contribution to ranking only when justified

### 9.2 Features and target

Target:
- `engagement_target`

Features (8 numeric):
- `log_views`, `log_likes`, `log_comments`
- `days_since_publish`
- `title_len`, `desc_len`
- `hashtag_count`, `tag_count`

Standardization:
- `StandardScaler`

### 9.3 CV design

- `GroupKFold(n_splits=5)`
- Group by channel id to avoid same-channel leakage between train/test

### 9.4 Models

- LinearRegression
- LASSO
- Ridge
- CART
- RandomForest
- LightGBM (if installed)

Reference baseline:
- BaselineMedian

### 9.5 Metrics

- RMSE
- MAE
- R2

Best model criterion:
- lowest CV RMSE among valid models

### 9.6 ML gating rule for ranking

ML score is used in final ranking only if:
- best model improves RMSE by at least 2% vs baseline median

### 9.7 SHAP

If best model is tree-based and SHAP package exists:
- produce summary importance
- produce dependence data for top features

---

## 10) Final ranking engine (most important section)

### 10.1 Engagement score normalization

- `engagement_score = min-max(mean_engagement)`

### 10.2 Reliability evidence score

Components:
- `scale_score = min-max(log1p(median_views))`
- `activity_score = min-max(log1p(n_videos))`
- `interaction_score = min-max(log1p(median_likes + median_comments))`

Formula:
- `evidence_score = 0.55*scale + 0.30*activity + 0.15*interaction`

### 10.3 Credibility multiplier

Base:
- `credibility_multiplier = clip(0.35 + 0.65*evidence_score, 0.20, 1.00)`

Extra low-signal penalty:
- if `median_views < 100` and `median_likes <= 1` and `median_comments <= 1`
- multiply by `0.30`

Final clip:
- `[0.08, 1.00]`

### 10.4 Eligibility guard

Recommended pool eligibility if any is true:
- `evidence_score >= 0.20`
- `median_views >= 500`
- `n_videos >= 12`

### 10.5 Weighted base score

If ML enabled by gate:
- `0.30*SNA + 0.20*TFIDF + 0.15*Semantic + 0.10*Tone + 0.15*Engagement + 0.10*ML`

If ML not enabled:
- `0.34*SNA + 0.24*TFIDF + 0.18*Semantic + 0.10*Tone + 0.14*Engagement`

Then:
- `final_score_base = weighted_sum`
- `final_score = final_score_base * credibility_multiplier`

### 10.6 Diversity guardrail

After sorting, top list is adjusted to satisfy minimum community diversity when possible.

This reduces shortlist concentration risk.

---

## 11) Benchmark analysis (Anchor vs CeraVe)

If enabled:
- run the same ranking process again with fixed CeraVe brief

Dashboard compares:
- anchor Top-N mean score
- benchmark Top-N mean score
- score gap (anchor minus benchmark)

Purpose:
- Provide contextual sanity check for shortlist strength

---

## 12) Detail enrichment and qualitative context

From `channel_details.py`:
- profile text
- keyword summary
- recent video titles
- best video title/views/url
- recent comments
- top liked comment
- estimated subscriber/video counts (from master file when available)

From `channel_media.py`:
- channel thumbnail (YouTube API when available)
- fallback thumbnail from representative video
- channel/video links

---

## 13) ROI simulator

Inputs:
- Budget
- CPM
- CTR
- CVR
- AOV

Formulas:
- `impressions = (budget / cpm) * 1000`
- `clicks = impressions * ctr`
- `conversions = clicks * cvr`
- `revenue = conversions * aov`
- `roas = revenue / budget`

Also shows a simple uncertainty band:
- `roas_low = roas * 0.7`
- `roas_high = roas * 1.3`

Interpretation:
- This is scenario planning, not causal attribution.

---

## 14) Content Strategy and Executive Memo

Content strategy generation:
- If `OPENAI_API_KEY` exists, generate tailored strategy text per channel
- Otherwise use deterministic fallback templates

Executive memo generation:
- Uses top channels + ROI + risk flags
- Exports markdown and text

---

## 15) Dashboard tab-by-tab interpretation guide

## 15.1 Overview

Shows:
- data volume and model headline metrics
- campaign input snapshot
- reliability summary (average evidence)
- optional benchmark panel

## 15.2 Top Matches

This tab can re-rank with strategy presets.

Flow:
1. choose strategy
2. compute `display_score`
3. apply score/evidence filters
4. apply optional diversity preview
5. render top cards and detailed table

Preset weights in Top Matches:
- Network-first: SNA 0.46, TF-IDF 0.16, Semantic 0.14, Tone 0.08, Eng 0.14, ML 0.02
- Keyword-first: SNA 0.20, TF-IDF 0.42, Semantic 0.18, Tone 0.08, Eng 0.10, ML 0.02
- Performance-first: SNA 0.20, TF-IDF 0.12, Semantic 0.16, Tone 0.08, Eng 0.38, ML 0.06

If run has ML disabled, ML weight is zeroed and weights are normalized.

Card labels:
- Fit label from `display_score`
- Evidence label from `evidence_score`

## 15.3 Network Studio

- interactive graph with node/edge interpretation
- community distribution
- graph meta
- bias report (degree overlap vs hybrid top)

## 15.4 Text Intelligence

- TF-IDF vs semantic scatter
- top terms chart
- keyword coverage matrix
- leaderboard

## 15.5 ML Studio

- CV comparison bars
- per-model metrics table
- predicted vs actual scatter
- SHAP summary/dependence
- rerun with selected models

## 15.6 ROI Lab

- interactive scenario tuning
- funnel chart
- budget sensitivity (ROAS and conversions)

## 15.7 Content Strategy

- channel-wise strategy cards
- creative hook cards

## 15.8 Executive Memo

- sectioned memo viewer
- download buttons

## 15.9 Glossary

- client-friendly definitions of terms

---

## 16) Why recommendations change (or do not change)

Why small change in brand/product name may not move results much:
- names alone have weak direct impact unless they add meaningful terms in text query

What usually changes results strongly:
- must/exclude keywords
- campaign goal
- evidence threshold and strategy in Top Matches
- graph controls (edge strength, tag ratio, min community size)

---

## 17) Common confusion and correct interpretation

"If I change campaign input, should everything change?"
- Not necessarily. If data and key terms remain similar, overlap can stay high.

"A channel has high score but low views, why?"
- It may have high fit signals but gets reliability penalty.
- Check `credibility_multiplier` and `evidence_score` before decision.

"Is ROI output guaranteed?"
- No. It is assumption-based scenario output.

"Is ML always used in final score?"
- No. Only if CV improvement vs baseline passes gate.

---

## 18) Output artifacts and where they are saved

Main outputs:
- Top-N CSV: `artifacts/reports/top{N}_{brand}.csv`
- All scored channels CSV: `artifacts/reports/scored_channels_{brand}.csv`
- Memo: `artifacts/reports/memo_{brand}.md`
- ML CV results: `artifacts/reports/ml_cv_results.csv`

Other generated data:
- cache and plots under `artifacts/cache/` and `artifacts/plots/`

---

## 18.1) Analysis categories (requested grouped structure)

To make the project easy for first-time readers, the analysis/modeling work can be grouped as follows.

### Analysis: Class Concepts

1. Text analysis
2. TF-IDF
3. Sentiment Analysis & Tone enrichment
4. SNA - Social Network Analysis (degree, betweenness proxy, eigenvector proxy)
5. ROI Calculator & Simulation

Notes:
- \"Sentiment Analysis & Tone enrichment\" in this project is implemented primarily as tone enrichment and comment-context signals.
- There is no separate standalone sentiment classifier model in the current code.

### Additional categories (not listed in the prompt but implemented)

1. Data Engineering
   - data loading, cleaning, filtering, aggregation
2. Predictive Modeling
   - regression benchmark suite with GroupKFold CV
3. Explainability
   - SHAP summary/dependence for tree-model path
4. Decision Optimization
   - reliability multiplier, eligibility guard, diversity-aware selection
5. Reporting and Decision Support
   - benchmark panel, strategy generation, executive memo, export artifacts

Code mapping for this category table:
- `submission_colab_python/ai_mcn_submission/analysis_categories.py`
- `submission_colab_python/colab_walkthrough.py` -> `get_analysis_category_overview()`

---

## 19) Class-linked methods vs project extensions

Class-linked (based on lecture themes):
- Social Network Analysis: graph, centrality, community
- Text Analysis: TF-IDF and similarity-based relevance
- AI/ML modeling and evaluation concepts

Project-specific extensions:
- Reliability multiplier and eligibility guard
- Diversity-aware Top-N selector
- Optional ML gating into final rank
- Benchmark mode and ROI simulator
- LLM strategy generation and memo automation

---

## 20) Repro steps for teammates

Local run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Quick pipeline run:

```bash
python3 run_pipeline.py --no-benchmark
```

Bootstrap check:

```bash
python3 scripts/bootstrap_full_data_from_gdrive.py
```

---

## 21) Practical demo script (short)

When presenting to non-technical audience, explain in this order:

1. We start with campaign constraints.
2. We score creators across network, text, behavior, and optional ML.
3. We penalize weak-evidence channels automatically.
4. We enforce shortlist diversity to reduce concentration bias.
5. We provide transparent card-level rationale and risk flags.
6. We support planning with benchmark and ROI scenario tools.

---

## 22) Final takeaway

This system is not a black-box "pick the biggest influencer" tool.
It is a transparent decision-support workflow that helps teams:
- shortlist faster
- justify choices better
- reduce mismatch risk
- communicate assumptions clearly
