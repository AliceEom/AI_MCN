# AI-MCN Presentation Script (15 Minutes, English)

## 0:00-2:00 | Speaker A: Problem and Scope
- Introduce the business problem: influencer selection is manual, slow, and often biased.
- Introduce BOJ scenario and campaign objective.
- Clarify prototype scope and why it is realistic for a class quarter.

## 2:00-5:30 | Speaker B: Data and Pipeline
- Explain dataset scale: 42,750 videos, 1,089 channels.
- Walk through hybrid pipeline:
  - filtering and aggregation,
  - network scoring,
  - text + semantic alignment,
  - ML benchmark,
  - ranking and guardrails.
- Emphasize explainability and sanity checks.

## 5:30-8:30 | Speaker B: Evaluation
- Show model benchmark slide:
  - LightGBM best RMSE 0.00996 vs baseline 0.03800.
- Explain practical meaning of 73.8% RMSE reduction.
- Show SHAP slide and connect to stakeholder trust.

## 8:30-12:30 | Speaker C: Live Demo
- In app:
  1. Enter campaign input.
  2. Run and show analyzing flow.
  3. Show Top-N recommendations and rationale cards.
  4. Change ranking strategy and diversity settings.
  5. Show Text Intelligence and ROI Lab.
  6. Show ML Studio and memo export.

## 12:30-14:00 | Speaker C: Business Impact and Caveats
- Summarize ROI scenario output (1.14x expected ROAS).
- Highlight bias guardrail and evidence penalty.
- State limitations honestly (pre-collected data, scenario-based ROI).
- Share future roadmap.

## 14:00-15:00 | All: Q&A
- Possible likely questions:
  - How is this better than follower-count filtering?
  - Is the model overfitting?
  - How would this run on live data weekly?
  - What if the campaign objective changes to conversions only?

