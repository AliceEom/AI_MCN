# Marketing AI MCN Demo Script (Very Detailed, Live Click-Through)

This script is written for your exact style:
- You click through the live Streamlit app.
- You explain each tab in detail.
- You return to slides and explain BOJ business actions.

Use short sentences. Speak clearly. Pause after each section.

---

## A) Opening (Slide 1: LIVE DEMO)

“Now I will show our live prototype.
I will start from campaign input, run the system, and explain every tab.
Please focus on three things:
how creators are scored,
why Top-10 is explainable,
and how this becomes a real business plan.”

“I will now open the demo link.”

---

## B) Live Demo Walkthrough (Detailed)

## 1) Landing Page / Campaign Brief

“This is the campaign input page.
This is not a static form.
Every field affects ranking or simulation.”

### 1-1. Brand & Product

“Brand Name is the campaign owner.
Product Name is the product we are matching creators to.
In this demo: Beauty of Joseon, Relief Sun SPF + Glow Serum.”

### 1-2. Product Category & Goal

“Product Category helps contextual filtering.
Campaign Goal changes tone preference and downstream strategy.
In this case, we use Awareness + trial conversion.”

### 1-3. Target Audience & Core Message

“Target Audience is converted into campaign brief text.
Core Message / USP is also injected into text matching.
So semantic alignment is affected by these two fields.”

### 1-4. Market, Budget, Top-N

“Market gives the business context.
Budget is used later in ROI Lab.
Top-N defines default shortlist size.
We use Top-10 in this demo.”

### 1-5. Must-Have Keywords / Excluded Keywords

“Must-Have keywords are positive relevance terms.
Excluded keywords remove irrelevant channels.
So this is one of the strongest quality-control settings.”

### 1-6. Advanced Controls

“Min Shared Tags per Edge controls graph strictness.
Max Tag Coverage Ratio removes overly common tags.
Min Community Size controls micro-cluster handling.
These three directly affect Network Studio and diversity behavior.”

### 1-7. ML and Benchmark toggles

“Enable ML Benchmark block adds model comparison and ML signal.
Run CeraVe Benchmark compares BOJ shortlist quality to competitor baseline.”

### 1-8. Run

“Now I click Find Influencers.
You can see the analysis pipeline stages:
data prep, network scoring, text scoring, ML benchmark, and synthesis.”

---

## 2) Dashboard Structure

“Now the dashboard opens.
Top bar summarizes brand, category, budget, and audience.
Below that, we have 9 tabs:
Overview, Top Matches, Network Studio, Text Intelligence, ML Studio, ROI Lab, Content Strategy, Executive Memo, Glossary.”

---

## 3) Overview Tab

“Overview is the quality gate before decision-making.”

### 3-1. Headline metrics

“Videos Analyzed: total video-level evidence used.
Channels Scored: creator candidates scored by model.
Best ML Model: best performer from cross-validation.
Top-10 Community Count: number of distinct creator communities represented in Top-10.
Higher count generally means better audience diversity and lower concentration risk.”

### 3-2. Data Reliability panel

“This panel shows average evidence level of current shortlist.
Low-evidence channels are down-weighted automatically.
So high keyword similarity alone is not enough.”

### 3-3. Campaign Input Snapshot

“This section restates campaign assumptions.
It is useful for client alignment and audit trail.”

### 3-4. Benchmark Panel (Anchor vs CeraVe)

“This compares BOJ shortlist mean score with CeraVe benchmark mean score.
Score gap = Anchor minus Benchmark.
Positive gap means current BOJ shortlist is stronger by our scoring framework.”

---

## 4) Top Matches Tab (Main Decision Center)

“This tab is where shortlist decisions happen.”

### 4-1. Control bar

“Min Match Score is a quality threshold.
Min Evidence prevents weak-data creators from entering shortlist.
Ranking Strategy changes signal weights:
Model Default, Network-first, Keyword-first, Performance-first.
Display Top-N controls output size.
Diversity Preview applies community guardrail.”

### 4-2. Top Influencer Score Breakdown chart

“This interactive grouped bar chart compares signal components by channel.
Signals:
SNA, TF-IDF, Semantic, Tone, Engagement, ML Potential.”

### 4-3. Channel card anatomy (use #1 as example)

“Now I open the first card.
This card shows:
image,
channel name,
Open Channel / Representative Video / Best Video buttons,
fit/evidence badges,
Final Match Score,
and rationale sentence.”

“For example, Robert Welsh is #1 in this default run.
You can see Final Match Score, then supporting diagnostics.”

### 4-4. Signal Breakdown bar (per channel)

“This horizontal bar explains score composition.
Each bar is 0 to 1.
This is important for non-technical clients.
They can see whether ranking came from network, keywords, engagement, or ML.”

### 4-5. Score Controls bar (per channel)

“Base means raw weighted score before reliability adjustment.
Final means displayed score after reliability.
Reliability is the multiplier based on observed evidence.
So if reliability is lower, Final will be reduced.”

### 4-6. Additional evidence fields

“Community ID is cluster label.
Freshness shows latest publish date and recency.
Channel snapshot, keyword summary, best video title, recent videos, and recent comments are also shown.”

### 4-7. Bottom diagnostics

“Detailed Channel Table gives comparison view.
Channels Down-weighted for Weak Evidence shows risk control behavior.”

---

## 5) Network Studio Tab

“This tab explains creator ecosystem structure, not just individual score.”

### 5-1. Controls

“Nodes in View controls graph size.
Min Edge Strength filters weak relationships.
Communities to Show controls community chart detail.
Include micro/isolated toggles tiny clusters.”

### 5-2. Network graph meaning (say this clearly)

“Each node is one channel.
Node size is proportional to Final Score.
Node color is Community ID.
Each edge means topic/tag overlap relationship.
Stronger edge threshold means tighter topical similarity.”

### 5-3. Node detail demo

“I choose one node in Inspect Node Details.
Now we can read:
Selected Channel,
Community,
Final Score,
Median Views.”

“If I choose Robert Welsh, I can quickly compare role and strength against other creators.”

### 5-4. Community diagnostics + graph meta

“Community Diagnostics shows cluster distribution.
Graph Meta shows node count, edge count, and dropped over-common tags.”

### 5-5. Bias report

“Degree Top Overlap checks how much our shortlist overlaps pure popularity ranking.
Lower overlap can indicate reduced popularity bias.
Unique Communities in Top-N and Unique Channels in Top-N support diversity validation.”

---

## 6) Text Intelligence Tab

“This tab explains language and message fit.”

### 6-1. Scatter map

“X-axis is TF-IDF similarity.
Y-axis is semantic alignment.
Color reflects evidence level.
Bubble size reflects reach proxy from median views.”

“So top-right creators are usually strong candidates for message fit.”

### 6-2. Top terms

“This chart shows frequent terms in selected candidate text.
It helps check if campaign language appears naturally.”

### 6-3. Keyword coverage matrix

“This matrix checks per-channel coverage of chosen keywords.
Coverage-rate chart summarizes which keywords are strongly represented.”

### 6-4. Leaderboard

“TF-IDF, Semantic, Tone, Final Score are shown side-by-side for quick comparison.”

---

## 7) ML Studio Tab

“This tab validates predictive quality for stakeholder confidence.”

### 7-1. Model rerun controls

“I can re-run with selected models or disable ML for a faster run.”

### 7-2. CV RMSE chart

“This bar chart compares 5-fold CV RMSE by model.
Lower RMSE is better.
Status indicates whether model is valid or baseline reference.”

### 7-3. Model metric panel

“For selected model, we show RMSE, MAE, and R2.
This gives compact model quality summary.”

### 7-4. Predicted vs Actual scatter

“Each dot is one observation.
Dashed diagonal is perfect fit.
Closer to diagonal means better predictive fit.”

### 7-5. SHAP explainability

“SHAP importance shows which features influenced prediction most.
SHAP dependence shows direction and pattern by feature values.
This improves explainability for non-technical decision makers.”

---

## 8) ROI Lab Tab

“This tab turns shortlist into financial scenarios.”

### 8-1. Input controls

“Budget, CPM, CTR, CVR, AOV are editable assumptions.”

### 8-2. KPI outputs

“Outputs:
Impressions,
Clicks,
Conversions,
Expected ROAS.”

### 8-3. ROI Funnel chart

“This chart visualizes funnel conversion from media spend to revenue.”

### 8-4. Budget sensitivity chart

“This chart shows how ROAS and conversions change when budget changes.
It helps planning for conservative vs aggressive spend.”

---

## 9) Content Strategy Tab

“This tab converts analytics into creator execution.”

### 9-1. Strategy card structure

“Left side:
creator identity, match score, median views, links.
Right side:
campaign structure tabs from generated strategy.”

### 9-2. Creative Thumbnail Hooks

“Each creator gets three hook suggestions:
headline hook,
problem-solution hook,
CTA-oriented hook.”

“This helps marketing teams move from analysis to content production quickly.”

---

## 10) Executive Memo Tab

“This tab provides client-facing summary.
Memo is split into sections in tabs.
You can download markdown or text version for sharing.”

---

## 11) Glossary Tab

“Glossary defines client-facing terms:
Match Score,
Data Reliability,
SNA,
TF-IDF,
Semantic,
Tone,
Engagement,
ML Potential,
Reliability Multiplier,
Community ID.”

“This is very useful during Q&A.”

---

## 12) Export Center (bottom panel)

“Export Center lets us download:
Top-N recommendations CSV,
all scored channels CSV,
and executive memo.”

“So the app is not only analysis UI.
It is also a handoff system for business teams.”

---

## C) Return to Slides (Business Use Case)

## Slide 3: Influencer Funnel

“Now I connect demo output to BOJ action.
We use three tracks:
Scale & Awareness,
Education & Support,
Conversion & Fit.
This prevents one-message-for-all inefficiency.”

“Creators are assigned by role:
Scale & Awareness: Robert Welsh, Tati, Beauty Within, James Welsh, Morgan Turner.
Education & Support: MrsMelissaM, Dr Alexis Stephens, Julie P.
Conversion & Fit: STEPHANIE TOMS, Mad About Skin.”

## Slide 4: Content Strategy

“We execute in 4 weeks:
Week 1 Awareness,
Week 2 Education + routine detail,
Week 3 Product proof/comparison,
Week 4 Conversion CTA + recap.
Then we re-rank weekly with KPI feedback.”

“Concept mapping:
Concept 1 for awareness creators.
Concept 2 for conversion-focused comparison creators.
Concept 3 for objection-handling Q&A creators.”

## Slide 5: Operating Plan

“0-30 days:
launch Top-10, assign budget tiers, standardize KPI tracking.

31-60 days:
re-rank by observed conversion data, reallocate budget.

61-90 days:
scale winners, build BOJ creator playbook, run monthly competitor benchmark.”

---

## D) Closing Lines (Choose one)

Option 1:
“This system does not only recommend creators.
It provides an explainable operating workflow from brief to execution.”

Option 2:
“For BOJ, this is a practical decision engine.
For beauty brands, this can replace manual, expensive matching cycles.”

---

## E) Backup Q&A Lines (Fast)

Q: “Does changing input matter?”
A: “Yes. Keywords, audience text, and controls directly change filtering, scoring, and strategy outputs.”

Q: “Why not rank by followers only?”
A: “Follower scale is only one signal. We combine relevance, evidence, network, engagement, and reliability to reduce mismatch risk.”

Q: “Is ML required?”
A: “No. You can disable ML. The app still runs rule-based and text/network scoring. ML adds benchmark depth and explainability.”
