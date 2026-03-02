# AI-MCN Execution Plan (English)

## 1) Mission
Build an English-only, presentation-ready AI influencer matching prototype for beauty brands, using:
- Anchor case: Beauty of Joseon
- Benchmark case: CeraVe
- Data-driven matching + ML benchmarking + explainability

## 2) Scope Lock
- Product scope: industry tool for beauty influencer selection.
- Demo scope: one concrete case (BOJ) with one benchmark (CeraVe).
- Delivery: Streamlit app + model outputs + visualizations + executive memo.

## 3) Data Inputs
- `data/videos_text_ready_combined.csv`
- `data/comments_raw_combined.csv`
- `data/master_prd_slim_combined.csv`

## 4) Core Pipeline
1. Data cleaning and beauty filtering.
2. Channel-level aggregation.
3. SNA graph and centrality/community scoring.
4. TF-IDF brand relevance scoring.
5. Engagement score creation.
6. ML block (Linear, LASSO, Ridge, CART, RF, LightGBM) with 5-fold GroupCV.
7. SHAP explainability on tree best-model (if available).
8. Top-20 semantic enrichment.
9. Final composite ranking and Top-5 with diversity constraints.
10. ROI scenario simulation.
11. Content strategy generation and executive memo.
12. BOJ vs CeraVe benchmark comparison.

## 5) Final Ranking Formula
`final_score = 0.30*SNA + 0.20*TFIDF + 0.15*Semantic + 0.10*Tone + 0.15*ObservedEngagement + 0.10*MLPotential`

Fallback rule:
- If ML does not beat baseline materially, set MLPotential contribution to 0 and renormalize.

## 6) ML Design
- Target: `log1p((likes + comments + 1)/(views + 100))` at video level.
- CV: `GroupKFold(5)` grouped by channel ID.
- Metrics: MAE, RMSE, R2.
- Baseline: median predictor.
- Outputs: CV table, best model, predicted-vs-actual plot, SHAP plots.

## 7) Demo UX (English only)
Input fields:
- Brand name, product name, category, target audience, campaign goal, budget, USP,
  must-have keywords, excluded keywords, market.

Output sections:
- Overview, Top recommendations, Network/diversity, ML benchmark, ROI, Content strategy, Executive memo.

## 8) Channel Cards
Each recommendation card shows:
- Channel image
- Channel name
- Channel URL
- Score breakdown
- Rationale and risk flags

Image strategy:
- First: YouTube channel thumbnail API (if key available)
- Fallback: representative video thumbnail

## 9) Artifacts
- `artifacts/reports/top5_<brand>.csv`
- `artifacts/reports/scored_channels_<brand>.csv`
- `artifacts/reports/memo_<brand>.md`
- `artifacts/reports/ml_cv_results.csv`
- `artifacts/plots/*` (CV, prediction, SHAP)

## 10) Acceptance Criteria
- End-to-end run without crash.
- All major sections rendered in English.
- 5-fold CV completed for available models.
- SHAP generated when supported.
- Top-5 includes diversity guardrail behavior.
- BOJ and CeraVe outputs both available.

## 11) Risks and Mitigation
- API instability -> cache first + fallback templates.
- Data contamination -> explicit beauty filtering and reporting.
- Overclaiming -> ROI labeled as scenario simulation.
- Model instability -> baseline comparison + fallback weighting.

