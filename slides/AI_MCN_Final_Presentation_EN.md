# AI-MCN: Replacing Traditional MCN Matching with an AI Decision System
## MSIS 521 Course Project (15-minute Presentation)

- Team: [Add names]
- Client case: Beauty of Joseon (BOJ), U.S. sunscreen campaign
- Prototype: Streamlit decision dashboard + Python AI pipeline

---

# 1) Agenda and Timing (Professor Guide)

1. Title & team (1 min)
2. Business context and problem (2-3 min)
3. Data and features (1-3 min)
4. AI/ML approach (3-4 min)
5. Prototype demo (3-4 min)
6. Impact, limitations, next steps (2-3 min)
7. How we used AI tools (1-2 min)

---

# 2) Business Context: Why This Problem Matters

What MCNs do today:
- Collect influencer data
- Match creators to brand campaigns
- Charge agency/management fees

Client pain point:
- Brands still pay high coordination cost but often get non-transparent matching logic.
- Mismatch risk is expensive because influencer budget is large and outcomes are uncertain.

Our objective:
- Build an AI system that helps brands directly find best-fit influencers.
- Reduce mismatch risk and improve campaign ROI consistency.

---

# 3) Client and Decision to Improve

Client scenario (hypothetical but realistic):
- Brand: Beauty of Joseon (BOJ)
- Product: Relief Sun SPF + Glow Serum
- Market: United States

Decision/process to improve:
- From: manual / popularity-based creator selection
- To: evidence-based shortlist + transparent rationale + ROI simulation

Core business questions:
- Which creators are best-fit for this specific product and audience?
- Which shortlist is diverse and lower-risk?
- What performance range can marketing managers expect before launch?

---

# 4) Why Now + Why Beauty + Why BOJ

Industry signal (external research):
- US influencer marketing spend is projected at **$10.52B in 2025** (EMARKETER, Mar 13, 2025).
- Over half of US marketers are expected to use influencer marketing on YouTube in 2025 (EMARKETER).
- Global beauty grew **7.3% YoY** in 2025; US beauty sales are heavily digital (**41% e-commerce**) (NIQ, Feb 25, 2025).
- McKinsey projects beauty core segments to reach **$590B by 2030**, with skincare as the largest segment.

Why BOJ for demo:
- Strong social virality and concrete U.S. expansion story.
- BOJ's sunscreen case is visible, product-specific, and fits our matching task.

---

# 5) BOJ Research Snapshot (Case Fit)

From published brand coverage:
- BOJ's Relief Sun content generated broad social traction (Fashionista, Nov 13, 2024).
- BOJ launched U.S. pop-up activation and U.S.-specific sunscreen adaptation.

From our dataset:
- `videos_text_ready_combined.csv` (67,283 videos, 2,220 channels)
- keyword coverage supports use case feasibility:
  - sunscreen: 3,981 videos / 340 channels
  - spf: 3,850 videos / 344 channels
  - beauty of joseon: 286 videos / 69 channels
  - cerave: 747 videos / 118 channels

Inference:
- Our data is sufficiently rich for BOJ-centered influencer matching and competitor benchmark.

---

# 6) Data and Features

Data used:
- Team-collected YouTube API exports (videos, comments, channel-level fields)
- Main files: videos, comments, master merged table

Pipeline input scale (full run):
- Videos analyzed: 42,750
- Channels scored: 1,089

Key feature groups:
- Network: degree/eigenvector/betweenness proxies, community ID
- Text: TF-IDF similarity, semantic score, tone score
- Behavioral: views/likes/comments, engagement-derived signals
- Reliability: evidence score and credibility multiplier

---

# 7) Preprocessing + EDA (Course Concepts Applied)

Preprocessing:
- Duplicate removal and type normalization
- Beauty include filter + non-beauty noise exclusion
- Channel-level aggregation and recency features

Simple EDA outputs:
- Community distribution (cluster concentration check)
- Top recommendation score breakdown
- Keyword coverage over candidate channels

What we learned:
- Skincare creators form a dominant cluster, so diversity guardrail is required.
- High keyword match alone is not enough; low-evidence channels must be down-weighted.

---

# 8) AI/ML Approach (Focused on Class-Learned Methods)

We prioritized these course-relevant methods:
1. **SNA (Social Networks Analysis)**: creator graph, centrality, communities
2. **Text relevance (TF-IDF + semantic enrichment)**: campaign-to-channel language fit
3. **Supervised regression suite**: Linear, LASSO, Ridge, CART, RandomForest, LightGBM
4. **5-fold GroupKFold CV**: channel-grouped validation to reduce leakage
5. **Model explainability (SHAP)**: interpretable feature contribution

Extensions shown in demo (not deeply covered in talk):
- ROI simulator, content strategy generator, executive memo automation

---

# 9) Why These Methods (and Not Simpler Alternatives)

Why not follower-count ranking only:
- misses topical fit, audience quality, and recency

Why hybrid instead of one model:
- SNA captures influence structure
- TF-IDF/semantic captures campaign relevance
- regression predicts engagement potential
- guardrails reduce low-signal bias

How final ranking works (brief):
- weighted hybrid score + reliability multiplier
- diversity-aware Top-N selection
- benchmark comparison (BOJ vs CeraVe)

---

# 10) Model Results and Validation

5-fold CV highlight (BOJ run):
- Best model: LightGBM
- RMSE: 0.00996
- Baseline median RMSE: 0.03800
- Relative reduction: 73.8%

Interpretation:
- Predictive block materially improves over naive baseline.
- We only use ML potential weight when benchmark gain is meaningful.

Visual:
![Model Benchmark](assets/model_benchmark_rmse.png)

---

# 11) Prototype Demo (Input -> Output)

Live flow:
1. Enter campaign brief (brand/product/audience/keywords/budget)
2. Generate Top-N influencer shortlist
3. Inspect channel cards with rationale and risk flags
4. Explore network, text match, ML benchmark, and ROI tabs

Use case A (primary):
- BOJ sunscreen launch planning (awareness + trial conversion)

Use case B (secondary):
- Benchmark against CeraVe to calibrate shortlist quality and positioning

---

# 12) Business Impact

How this changes decisions:
- Faster creator shortlisting with transparent evidence
- Less dependence on manual MCN-style matching workflows
- Better pre-campaign risk control using reliability and diversity checks
- Better budget planning through scenario-based ROI analysis

Who benefits:
- Brand managers, performance marketers, partnerships teams, agencies

---

# 13) Limitations, Ethics, and Next Steps

Limitations:
- Current prototype is based on pre-collected YouTube data (not full live multi-platform ingestion)
- ROI is a scenario estimate, not causal proof
- Some cluster concentration remains in beauty sub-niches

Ethics / bias / privacy:
- Popularity bias risk monitored through overlap diagnostics
- Low-evidence channels automatically penalized
- No personal sensitive user profiling in this prototype

Next steps:
- Add live connectors (YouTube + TikTok + Instagram)
- Add stronger fairness/diversity constraints
- Run real campaign pilot for calibration

---

# 14) How We Used AI Tools in This Project

AI tools were used for:
- idea generation and scope refinement
- coding acceleration (pipeline/app implementation)
- debugging and error triage
- documentation, memo drafting, and presentation polishing

Human role remained central for:
- problem framing
- method selection and validation design
- interpretation of results
- business recommendation decisions

---

# 15) Conclusion and References

Conclusion:
- AI-MCN is a practical decision-support prototype that can reduce manual MCN dependence and improve influencer campaign quality.

References (external):
- [EMARKETER Press Release (Mar 13, 2025): US influencer spending forecast](https://www.emarketer.com/press-releases/us-influencer-marketing-spending-will-surpass-10-billion-in-2025/)
- [NIQ Press Release (Feb 25, 2025): global beauty growth, e-commerce/social commerce indicators](https://nielseniq.com/global/en/news-center/2025/niq-reports-7-3-year-over-year-value-growth-in-global-beauty-sector/)
- [McKinsey (Aug 28, 2025): global beauty outlook to 2030](https://www.mckinsey.com/industries/consumer-packaged-goods/our-insights/a-close-look-at-the-global-beauty-industry-in-2025)
- [Fashionista (Nov 13, 2024): BOJ U.S. expansion and virality context](https://fashionista.com/2024/11/beauty-of-joseon-k-beauty-skin-care-us-launch-strategy)

References (technical):
- YouTube Data API docs
- scikit-learn docs (regression + GroupKFold)
- LightGBM docs
- SHAP docs
- Streamlit docs

Q&A
