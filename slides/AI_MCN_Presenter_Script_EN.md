# AI-MCN Presentation Script (Professor Guide Aligned, 15 Minutes)

## 0:00-1:00 | Speaker A | Title and Team
- Introduce project title, team members, and client scenario.
- One-line value proposition: "We built an AI system that helps brands replace manual MCN-style influencer matching."

## 1:00-3:30 | Speaker A | Business Context and Problem
- Explain current MCN workflow and why brands pay for matching support.
- State pain points: opaque logic, mismatch risk, high campaign cost.
- Define decision to improve: from popularity-led selection to evidence-based shortlist.

## 3:30-5:30 | Speaker A | Why Beauty and Why BOJ
- Use market context briefly: influencer spend growth + beauty growth + digital commerce relevance.
- Explain BOJ as a strong demonstration case (viral sunscreen + U.S. market activation).
- Transition: "Now we show how our data supports this case."

## 5:30-7:30 | Speaker B | Data and Features
- Present data source and scale.
- Cover preprocessing: dedupe, beauty filtering, channel aggregation.
- Show one to two EDA visuals and what we learned from them.

## 7:30-10:30 | Speaker B | AI/ML Approach (Class-Centered)
- Emphasize class concepts:
  1) SNA for influence structure,
  2) TF-IDF/semantic fit for campaign relevance,
  3) regression suite + GroupKFold CV,
  4) SHAP for explainability.
- Explain why hybrid outperforms single-signal alternatives.
- Show model benchmark and baseline improvement.

## 10:30-13:30 | Speaker C | Live Prototype Demo
- Walk through input -> output:
  1) campaign brief input,
  2) Top-N influencer results,
  3) rationale/risk panel,
  4) network/text/ML/ROI tabs.
- Highlight two concrete use cases:
  - BOJ launch planning,
  - CeraVe benchmark calibration.

## 13:30-14:30 | Speaker C | Impact, Limitations, Next Steps
- Impact: faster shortlist, better transparency, less mismatch risk.
- Limitations: pre-collected data, scenario-based ROI, remaining cluster concentration.
- Next steps: live connectors, fairness constraints, real pilot calibration.

## 14:30-15:00 | Speaker C (or All) | AI Tools Note and Q&A
- Briefly state how AI tools were used (ideation, coding, debugging, docs).
- Clarify human ownership of framing, evaluation, and business recommendations.
- Open Q&A.

## Likely Q&A prompts to prepare
- "How does this reduce dependence on MCNs in practice?"
- "How do you avoid recommending flashy but low-quality creators?"
- "What changes if campaign objective is conversion only?"
- "How would this run as a weekly production workflow?"
