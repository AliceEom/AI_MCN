# AI-MCN: Replacing Traditional MCN Matching with an AI Decision System
## MSIS 521 Course Project | Research-Expanded Version (15-minute core + backup slides)

- Team: [Add names]
- Client case used in demo: Beauty of Joseon (BOJ), U.S. sunscreen campaign
- Core product: Streamlit decision dashboard + Python AI pipeline
- Positioning: Reduce manual MCN dependency for influencer discovery, ranking, and campaign planning

**Sources (this slide):**
- Internal repo overview: [README](/Users/alice/521_Marketing/README.md)
- Internal app entry: [app.py](/Users/alice/521_Marketing/app.py)

---

# 1) Agenda and Time Split (Professor Guide Aligned)

1. Title and team (1 min)
2. Business context and problem (2-3 min)
3. Data and features (1-3 min)
4. AI/ML approach (3-4 min)
5. Prototype demo (3-4 min)
6. Impact, limitations, next steps (2-3 min)
7. How we used AI tools (1-2 min)

How to present this expanded deck:
- Use slides 1-15 for the strict 15-minute version
- Use slides 16+ as backup for deeper Q&A and rubric depth

**Sources (this slide):**
- Instructor-provided MSIS 521 presentation structure

---

# 2) Problem Statement: Why This Project Exists

Business reality for brands:
- Influencer spend is now a core media budget line, not an experiment.
- Wrong creator selection can burn budget quickly (low conversion, poor brand fit, compliance risk).
- Teams still rely on fragmented workflows: agency decks, manual search, spreadsheet comparisons.

Our decision problem:
- Input: campaign brief (brand, product, audience, market, constraints)
- Output: evidence-based Top-N creators with transparent rationale and risk controls

What we are replacing:
- From opaque/manual MCN-style matching
- To traceable, data-first ranking with explainable sub-scores

**Sources (this slide):**
- [EMARKETER press release (Mar 13, 2025)](https://www.emarketer.com/press-releases/us-influencer-marketing-spending-will-surpass-10-billion-in-2025/)
- [IAB Creator Economy press release (Nov 20, 2025)](https://www.iab.com/news/creator-economy-ad-spend-to-reach-37-billion-in-2025-growing-4x-faster-than-total-media-industry-according-to-iab/)

---

# 3) Market Scale: Why Decision Quality Matters More Now

Recent market signals:
- U.S. influencer marketing spend projected at **$10.52B in 2025** (EMARKETER, March 13, 2025).
- IAB estimates U.S. creator-economy ad spend at **$37B in 2025**, with forecast to **$52B by 2030** (Nov 20, 2025 release).
- IAB reports **85%** of agencies/brands plan to maintain or increase creator investment.

Implication for brands:
- As spend scales, matching error is no longer a small tactical issue.
- Selection quality, explainability, and monitoring become strategic requirements.

**Sources (this slide):**
- [EMARKETER (Mar 13, 2025)](https://www.emarketer.com/press-releases/us-influencer-marketing-spending-will-surpass-10-billion-in-2025/)
- [IAB (Nov 20, 2025)](https://www.iab.com/news/creator-economy-ad-spend-to-reach-37-billion-in-2025-growing-4x-faster-than-total-media-industry-according-to-iab/)
- [IAB Full Report PDF landing page](https://www.iab.com/wp-content/uploads/2025/11/IAB_Creator_Economy_Spend_Investment_2025.pdf)

---

# 4) Operational Pain: Where Teams Lose Time

Execution bottlenecks from market surveys:
- IAB reports one of the top hurdles is finding the right creators (about one-third of respondents in 2025 report framing).
- Sprout Social reports **39%** of social teams spend 2+ hours/day on manual tasks (research, reporting, handoffs).
- Linqia's 2023 benchmark also flags time-to-execution as a major influencer marketing challenge.

What this means operationally:
- Campaign velocity slows when discovery and screening are manual.
- Teams spend effort collecting data instead of deciding with confidence.

Project response:
- We automate discovery, scoring, shortlist generation, and exportable outputs in one flow.

**Sources (this slide):**
- [IAB Creator Economy findings (Nov 20, 2025)](https://www.iab.com/news/creator-economy-ad-spend-to-reach-37-billion-in-2025-growing-4x-faster-than-total-media-industry-according-to-iab/)
- [Sprout Social Index findings on manual workload](https://sproutsocial.com/insights/data/social-media-teams-wear-many-hats-to-reach-business-goals/)
- [Linqia State of Influencer Marketing 2023 (PDF)](https://www.linqia.com/wp-content/uploads/2023/06/The-State-of-Influencer-Marketing-2023.pdf)

---

# 5) Budget Waste Risk: ROI and Measurement Friction

Persistent measurement issues:
- IAB: proving ROI remains one of the most-cited creator marketing challenges.
- Linqia 2026 benchmark: brands still report ROI proof/attribution as top pain despite budget growth.
- Linqia 2026: **57%** expect budget increases; **48%** report influencer marketing takes over half of marketing budget.

Interpretation:
- Budget is increasing faster than measurement maturity.
- High spend + weak attribution = higher risk of inefficient creator allocation.

Project response:
- Pair recommendation with measurable signals (score components, evidence controls, benchmark panel, ROI simulator).

**Sources (this slide):**
- [IAB press release (Nov 20, 2025)](https://www.iab.com/news/creator-economy-ad-spend-to-reach-37-billion-in-2025-growing-4x-faster-than-total-media-industry-according-to-iab/)
- [Linqia 2026 Benchmark](https://www.linqia.com/industry/influencer-marketing-benchmark-report-2026/)
- [Linqia 2023 Benchmark PDF](https://www.linqia.com/wp-content/uploads/2023/06/The-State-of-Influencer-Marketing-2023.pdf)

---

# 6) MCN Context: What They Solve and Where Gaps Remain

Why MCN/intermediaries exist:
- Centralize creator-channel data, rights operations, and campaign coordination.
- Provide scalable account handling for brands managing many creators.

Known limitations for brand decision teams:
- Matching logic can be opaque or hard to audit.
- Quality control varies by partner and process.
- Business teams may still need independent verification before committing spend.

Why our framing is “AI-MCN”:
- Keep core strengths (scale, structure, repeatability)
- Replace opaque ranking with transparent score architecture and controllable constraints

**Sources (this slide):**
- [YouTube Help: Link channels to Content Manager](https://support.google.com/youtube/answer/106934?hl=en-EN)
- [YouTube Help: MCN Content ID setup](https://support.google.com/youtube/answer/7296308?hl=en-GB)
- [FTC Endorsement Guides overview](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides)

---

# 7) Why Beauty Is an Especially Hard Category

Category pressure is structurally high:
- NIQ reports global beauty grew **7.3% YoY** (reported Feb 25, 2025).
- NIQ reports U.S. beauty is heavily digital, with large e-commerce and social-commerce contribution.
- McKinsey (Aug 28, 2025): social-media influence on beauty purchases remains above 40%, while customer acquisition costs have sharply increased.

Why this creates matching difficulty:
- High content velocity and trend turnover
- High competition for attention in skincare narratives
- Expensive mismatch risk due to high CAC and high content dependency

**Sources (this slide):**
- [NIQ global beauty growth release (Feb 25, 2025)](https://nielseniq.com/global/en/news-center/2025/niq-reports-7-3-year-over-year-value-growth-in-global-beauty-sector/)
- [McKinsey beauty outlook (Aug 28, 2025)](https://www.mckinsey.com/industries/consumer-packaged-goods/our-insights/a-close-look-at-the-global-beauty-industry-in-2025)
- [IAB creator economy release (Nov 20, 2025)](https://www.iab.com/news/creator-economy-ad-spend-to-reach-37-billion-in-2025-growing-4x-faster-than-total-media-industry-according-to-iab/)

---

# 8) Why BOJ Is a Good Demo Client Case

Case selection logic:
- Clear product story (sunscreen + lightweight skincare)
- Clear audience framing (U.S. Gen Z/Millennial, sensitive/acne-prone skin)
- Publicly visible U.S. campaign expansion narrative

External signals supporting case relevance:
- NIQ K-beauty report highlights strong U.S. growth and rising market share.
- BOJ campaign pages and U.S. activations provide concrete go-to-market context.

Strategic fit for course project:
- Complex enough for ML+SNA+text methods
- Specific enough for explainable recommendation demo

**Sources (this slide):**
- [NIQ: How K-beauty is shaping global beauty (2025)](https://nielseniq.com/global/en/news-center/2025/how-k-beauty-is-shaping-the-global-beauty-landscape/)
- [Fashionista BOJ U.S. strategy feature (Nov 13, 2024)](https://fashionista.com/2024/11/beauty-of-joseon-k-beauty-skin-care-us-launch-strategy)
- [BOJ official Rice Wonderland page](https://beautyofjoseon.com/pages/rice-wonderland)

---

# 9) Data Used in This Project

Primary data source:
- Team-collected YouTube API exports (videos, comments, channel/master fields)

Current full-run scale:
- Videos analyzed: **42,750**
- Channels scored: **1,089**

Data modules:
- Video metadata and performance signals
- Comment signals
- Channel-level master statistics

Design principle:
- Use only observed, reproducible dataset fields for scoring logic.

**Sources (this slide):**
- Internal data folder: [data/](/Users/alice/521_Marketing/data)
- Internal summary: [presentation_summary_boj.json](/Users/alice/521_Marketing/artifacts/reports/presentation_summary_boj.json)
- [YouTube Data API reference](https://developers.google.com/youtube/v3)

---

# 10) Data Preparation and Quality Controls

Preprocessing pipeline:
- Video-level deduplication by `_video_id`
- Numeric/date normalization
- Include filters (beauty + campaign keywords)
- Exclude filters (noise categories + excluded keywords)
- Engagement target engineering for ML

Quality guardrails:
- Remove impossible metric cases (e.g., non-positive views)
- Penalize weak-evidence channels later in ranking stage

Why this matters:
- Reduces noisy channels dominating recommendation due to accidental keyword overlap.

**Sources (this slide):**
- Internal preprocessing logic: [data_prep.py](/Users/alice/521_Marketing/src/data_prep.py)
- Internal explainers: [AI_MCN_Analysis_Explainer_EN.md](/Users/alice/521_Marketing/docs/AI_MCN_Analysis_Explainer_EN.md)

---

# 11) Feature Engineering Architecture

Signal families used:
- Network signals: degree/betweenness/eigenvector proxies + community structure
- Text signals: TF-IDF similarity + semantic and tone alignment
- Performance signals: engagement/scale/activity/interaction
- ML potential: model-based expected engagement contribution
- Reliability controls: evidence score + credibility multiplier

Principle:
- No single signal decides ranking.
- Final recommendation is hybrid and penalty-aware.

**Sources (this slide):**
- Network module: [network_scoring.py](/Users/alice/521_Marketing/src/network_scoring.py)
- Text module: [text_scoring.py](/Users/alice/521_Marketing/src/text_scoring.py)
- Ranking module: [ranking.py](/Users/alice/521_Marketing/src/ranking.py)

---

# 12) Network Analysis (SNA) Details

Graph construction:
- Node = channel
- Edge = shared tags between channels
- Edge weight = count of shared tags

Anti-noise controls:
- Require minimum shared tags
- Drop over-common tags (coverage-ratio ceiling)
- Reassign tiny communities to `-1` (micro/other)

SNA score composition:
- 0.33 degree + 0.34 betweenness proxy + 0.33 eigenvector proxy
- Min-max scaled into `sna_score`

Why this helps:
- Finds structurally influential creators, not just large subscriber counts.

**Sources (this slide):**
- Internal SNA code: [network_scoring.py](/Users/alice/521_Marketing/src/network_scoring.py)
- Internal network tab rendering: [app.py](/Users/alice/521_Marketing/app.py)

---

# 13) Text Intelligence Details

TF-IDF relevance:
- Query = full campaign brief + must keywords
- Compare against each channel's aggregated text

Keyword logic:
- Must keyword hits increase score
- Excluded keyword hits reduce score

Semantic/tone enrichment:
- Applied to top pre-candidates
- Adds meaning-level fit and campaign-goal tone match
- Emits red flags for low semantic fit, excluded-signal overlap, low activity

Why this helps:
- Prevents pure popularity rankings that ignore message fit.

**Sources (this slide):**
- Text scoring: [text_scoring.py](/Users/alice/521_Marketing/src/text_scoring.py)
- Semantic enrichment: [semantic_enrichment.py](/Users/alice/521_Marketing/src/semantic_enrichment.py)

---

# 14) ML Benchmark Design (Class-Centered)

Models trained:
- Linear Regression, LASSO, Ridge, CART, Random Forest, LightGBM

Validation design:
- 5-fold `GroupKFold` by channel id (reduces leakage across same-channel videos)
- BaselineMedian included as reference model

Explainability:
- SHAP summary and dependence charts (tree-model path)

Safety rule:
- ML score only affects final ranking when best model outperforms baseline by at least 2% RMSE.

**Sources (this slide):**
- Internal ML pipeline: [ml_modeling.py](/Users/alice/521_Marketing/src/ml_modeling.py)
- [scikit-learn GroupKFold docs](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html)
- [LightGBM docs](https://lightgbm.readthedocs.io/en/latest/)
- [SHAP docs](https://shap.readthedocs.io/en/latest/)

---

# 15) Final Ranking Formula (Core Decision Engine)

When ML is active:
- `0.30*SNA + 0.20*TFIDF + 0.15*Semantic + 0.10*Tone + 0.15*Engagement + 0.10*ML`

When ML is inactive:
- `0.34*SNA + 0.24*TFIDF + 0.18*Semantic + 0.10*Tone + 0.14*Engagement`

Reliability penalty:
- `final_score = final_score_base * credibility_multiplier`
- Weak-evidence channels receive strong down-weighting

Diversity guardrail:
- Top-N selection tries to preserve minimum community diversity to reduce popularity bias.

**Sources (this slide):**
- Ranking logic: [ranking.py](/Users/alice/521_Marketing/src/ranking.py)
- Diversity selector: [ranking.py](/Users/alice/521_Marketing/src/ranking.py)

---

# 16) Model Performance Snapshot (Current BOJ Run)

Run output (full data setup):
- Best model: **LightGBM**
- Best RMSE: **0.00996**
- Baseline RMSE: **0.03800**
- Relative RMSE reduction: **73.8%**

Interpretation:
- Predictive signal quality is materially better than a naive median baseline.

Visual:
![Model Benchmark](assets/model_benchmark_rmse.png)

**Sources (this slide):**
- Internal CV summary: [ml_cv_results.csv](/Users/alice/521_Marketing/artifacts/reports/ml_cv_results.csv)
- Internal run summary: [presentation_summary_boj.json](/Users/alice/521_Marketing/artifacts/reports/presentation_summary_boj.json)

---

# 17) Top-Match Output: What Client Actually Gets

Client-facing outputs per recommended channel:
- Final score and component score breakdown
- Reliability/evidence classification
- Channel metadata (image, urls, best video, recent videos, sample comments)
- Rationale text + red-flag indicators

Decision utility:
- Not just “who is top,” but “why this creator,” “what risk exists,” and “how strong the evidence is.”

**Sources (this slide):**
- App top-match tab implementation: [app.py](/Users/alice/521_Marketing/app.py)
- Channel detail enrichment: [channel_details.py](/Users/alice/521_Marketing/src/channel_details.py)
- Channel media enrichment: [channel_media.py](/Users/alice/521_Marketing/src/channel_media.py)

---

# 18) Network Studio: Bias and Diversity Diagnostics

What this tab is for:
- Visualize community concentration and structural concentration risk
- Compare degree-only ranking overlap vs final hybrid ranking

Bias diagnostics included:
- Degree Top Overlap
- Unique communities in Top-N
- Unique channels in Top-N
- Narrative summary to explain de-biasing impact

Business interpretation:
- Helps client avoid over-concentrated creator portfolios.

**Sources (this slide):**
- Bias report generation: [orchestrator.py](/Users/alice/521_Marketing/src/orchestrator.py)
- Network UI: [app.py](/Users/alice/521_Marketing/app.py)

---

# 19) Text Intelligence: Message-Market Fit Diagnostics

Key views:
- TF-IDF vs Semantic map
- Frequent term chart
- Keyword coverage matrix
- Text leaderboard

What client learns:
- Which shortlisted creators actually speak the campaign language
- Which required keywords have weak representation
- Where content-style mismatch risk exists

**Sources (this slide):**
- Text tab implementation: [app.py](/Users/alice/521_Marketing/app.py)
- Text scoring engine: [text_scoring.py](/Users/alice/521_Marketing/src/text_scoring.py)

---

# 20) ROI Lab: Planning Instead of Guessing

Scenario controls:
- Budget, CPM, CTR, CVR, AOV

Outputs:
- Impressions, clicks, conversions, revenue, ROAS
- Sensitivity chart over budget range

Important caveat:
- This is scenario simulation, not causal attribution.
- It is for planning and expectation setting, not outcome guarantee.

**Sources (this slide):**
- ROI simulation engine: [roi_simulation.py](/Users/alice/521_Marketing/src/roi_simulation.py)
- ROI tab implementation: [app.py](/Users/alice/521_Marketing/app.py)

---

# 21) Business Impact for Brand Teams

Decision speed impact:
- Faster shortlist generation and review cycles
- Lower manual workload for multi-signal creator evaluation

Decision quality impact:
- Transparent score components for stakeholder buy-in
- Reliability penalties reduce weak-evidence false positives
- Diversity controls reduce over-concentration risk

Organizational impact:
- Supports “in-house AI-MCN” operating model
- Reduces dependency on opaque external matching processes

**Sources (this slide):**
- [IAB 2025 creator economy findings](https://www.iab.com/news/creator-economy-ad-spend-to-reach-37-billion-in-2025-growing-4x-faster-than-total-media-industry-according-to-iab/)
- [Sprout workload findings](https://sproutsocial.com/insights/data/social-media-teams-wear-many-hats-to-reach-business-goals/)
- Internal decision artifacts: [artifacts/reports/](/Users/alice/521_Marketing/artifacts/reports)

---

# 22) Limitations and Responsible Use

Current limitations:
- Dataset is pre-collected (not fully live, multi-platform ingestion)
- ROI block is assumptions-based scenario modeling
- Results depend on keyword quality and dataset coverage

Governance and compliance:
- Sponsored-content disclosure requirements must be enforced
- Endorsement compliance and claim safety need legal review
- Brand safety and authenticity checks should be operationalized

**Sources (this slide):**
- [FTC Influencer Disclosures 101](https://www.ftc.gov/influencers)
- [FTC Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides)
- [FDA Sunscreen Innovation Act background](https://www.fda.gov/drugs/guidance-compliance-regulatory-information/sunscreen-innovation-act-sia)

---

# 23) 90-Day Roadmap (If This Becomes a Real Client Product)

Phase 1 (0-30 days):
- Stabilize weekly pipeline and dashboards
- Add alerting on weak-evidence recommendations
- Define decision SLA and reviewer workflow

Phase 2 (31-60 days):
- Add live connectors (multi-platform ingestion)
- Extend benchmark set by category and market
- Introduce A/B experimentation design templates

Phase 3 (61-90 days):
- Pilot with real outreach cycle
- Compare predicted vs realized performance
- Retrain and recalibrate weights from pilot outcomes

**Sources (this slide):**
- Internal implementation architecture: [orchestrator.py](/Users/alice/521_Marketing/src/orchestrator.py)
- Internal app workflow: [app.py](/Users/alice/521_Marketing/app.py)

---

# 24) How We Used AI Tools (And What Stayed Human)

AI-assisted tasks:
- Ideation and scope expansion
- Coding acceleration and debugging
- Documentation and slide drafting

Human-owned decisions:
- Business framing and client narrative
- Model choice and validation design
- Interpretation and final recommendation accountability

**Sources (this slide):**
- Internal commit history and project artifacts

---

# 25) Consolidated References (Research Library for Team)

Market and spend:
- [EMARKETER (Mar 13, 2025)](https://www.emarketer.com/press-releases/us-influencer-marketing-spending-will-surpass-10-billion-in-2025/)
- [IAB Creator Economy (Nov 20, 2025)](https://www.iab.com/news/creator-economy-ad-spend-to-reach-37-billion-in-2025-growing-4x-faster-than-total-media-industry-according-to-iab/)
- [Goldman Sachs Creator Economy outlook](https://www.goldmansachs.com/insights/articles/the-creator-economy-could-approach-half-a-trillion-dollars-by-2027)

Operational pain and measurement:
- [Sprout Social manual-task findings](https://sproutsocial.com/insights/data/social-media-teams-wear-many-hats-to-reach-business-goals/)
- [Linqia 2026 Benchmark](https://www.linqia.com/industry/influencer-marketing-benchmark-report-2026/)
- [Linqia 2023 Benchmark PDF](https://www.linqia.com/wp-content/uploads/2023/06/The-State-of-Influencer-Marketing-2023.pdf)

Beauty and BOJ context:
- [NIQ global beauty growth (Feb 25, 2025)](https://nielseniq.com/global/en/news-center/2025/niq-reports-7-3-year-over-year-value-growth-in-global-beauty-sector/)
- [NIQ K-beauty landscape (2025)](https://nielseniq.com/global/en/news-center/2025/how-k-beauty-is-shaping-the-global-beauty-landscape/)
- [McKinsey beauty outlook (Aug 28, 2025)](https://www.mckinsey.com/industries/consumer-packaged-goods/our-insights/a-close-look-at-the-global-beauty-industry-in-2025)
- [Fashionista BOJ U.S. strategy](https://fashionista.com/2024/11/beauty-of-joseon-k-beauty-skin-care-us-launch-strategy)
- [BOJ official campaign page](https://beautyofjoseon.com/pages/rice-wonderland)

MCN/compliance context:
- [YouTube Content Manager linking](https://support.google.com/youtube/answer/106934?hl=en-EN)
- [YouTube MCN Content ID setup](https://support.google.com/youtube/answer/7296308?hl=en-GB)
- [FTC Influencer Disclosures](https://www.ftc.gov/influencers)
- [FTC Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides)
- [FDA SIA background](https://www.fda.gov/drugs/guidance-compliance-regulatory-information/sunscreen-innovation-act-sia)

Q&A
