# Marketing AI MCN Demo Script (Follow Your Current Slide Order)

This version follows your exact current slide flow:
1. `DEMO-INPUT`
2. `LIVE DEMO`
3. `Business Use Case 1`
4. `Business Use Case 2`
5. `Business Use Case 3`

Use this as a speaking script. Sentences are short and easy to speak.

Quick number guide for the full script:
- Scores between 0 and 1: higher means stronger fit or stronger signal.
- Percent values: direct rates, such as CTR or CVR.
- `x` values like `x0.833`: multiplier applied to adjust score up/down.
- Counts: how many videos, channels, communities, or edges are included.
- Currency values: USD planning assumptions, not guaranteed outcomes.

---

## Slide 1: DEMO-INPUT

"Now I will start my demo section.
Before showing the tool, I will explain the campaign input."

"For this demo, we entered:
Brand: Beauty of Joseon,
Product: Relief Sun SPF + Glow Serum,
Category: Skincare,
Market: United States,
Budget: 50,000 dollars,
Target audience: US Gen Z and Millennial users with sensitive or acne-prone skin."

"How to read this number:
Budget 50,000 means total campaign spend assumption used in ROI simulation.
If we change this number, projected impressions, clicks, and conversions change immediately."

"We also set must-have keywords and excluded keywords.
Must-have: sunscreen, SPF, sensitive skin, k-beauty.
Excluded: music, gaming, movie, trailer."

"Each field is functional.
Brand, product, audience, and USP create the campaign brief text.
Must-have keywords increase relevance in text matching.
Excluded keywords reduce off-topic channels.
Budget goes directly into ROI simulation.
So this input changes filtering, scoring, and business output."

---

## Slide 2: LIVE DEMO (Open the link and demo live)

"Now I will move to the live demo.
I will click the demo link now."

---

## Live App: Campaign Brief Page (if shown first)

"This is the campaign brief form.
I already entered BOJ settings.
After I click 'Find Influencers,'
the pipeline runs data prep, text scoring, social network scoring, ML benchmark, and final ranking."

---

## Live App Tab 1: Overview

"Overview is the quality check tab.
Here I read the headline metrics first:
videos analyzed, channels scored, best ML model, and Top-10 community count."

"How to read these metric numbers:
Videos analyzed = number of cleaned video records used as evidence.
Channels scored = number of unique creators scored by the model.
Best ML model = model with the lowest cross-validation error in this run.
Top-10 community count = number of distinct creator clusters in shortlist."

"Top-10 Community Count means:
how many different creator clusters are represented in Top-10.
Higher count means better diversity and lower concentration risk."

"Then I read Data Reliability.
This tells us whether recommendations are backed by enough channel evidence.
Low-evidence channels are down-weighted automatically."

"Now the Benchmark Panel.
We show it because a raw score alone has no reference point.
Benchmark gives a relative standard."

"Why CeraVe?
CeraVe is a practical reference brand for this BOJ case:
same US skincare context, sensitive-skin positioning,
and enough comparable creator data in our dataset.
So it is a stable baseline."

"What exactly is 'comparable creator data' here:
BOJ keyword set has 4 must terms:
sunscreen, SPF, sensitive skin, k-beauty.
CeraVe benchmark keyword set also has 4 must terms:
cerave, cleanser, moisturizer, SPF.
In our current scored pool, BOJ-keyword-hit channels are 198 and CeraVe-keyword-hit channels are 188.
So both sides have enough keyword-linked creator volume for relative comparison."

"How to read these values:
4 terms vs 4 terms means both briefs are balanced in keyword scope.
198 and 188 are channel counts with at least one keyword hit per brand set.
These are coverage counts, not final recommendations."

"How to read benchmark values:
Anchor Mean Score = BOJ Top-N average final score.
Benchmark Mean Score = CeraVe Top-N average final score.
Score Gap = Anchor minus Benchmark.
If the gap is positive, our BOJ shortlist is stronger than benchmark under the same scoring framework."

"Number meaning here:
Anchor and Benchmark mean scores are normalized fit scores on a 0 to 1 scale.
Score Gap is a relative difference indicator, not an absolute sales lift value."

"Important note:
benchmark is a decision aid, not a sales guarantee.
It is comparative evidence for planning."

---

## Live App Tab 2: Top Matches

"This is the decision center.
At the top, I can adjust thresholds and ranking behavior."

"Min Match Score sets strictness.
Min Evidence filters weak-data channels.
Ranking Strategy changes score emphasis.
Display Top-N controls shortlist size.
Diversity Preview checks whether we over-concentrate on one cluster."

"Now I show the interactive score breakdown chart.
Each creator has six signals."

"SNA:
network influence and connectivity in creator ecosystem."

"TF-IDF:
exact keyword overlap with our campaign brief and must-have terms."

"Semantic:
meaning-level alignment between channel text and campaign intent."

"Tone:
style match with campaign communication tone, such as educational or conversion-oriented."

"Engagement:
observed response quality from views, likes, and comments."

"ML Potential:
predicted engagement upside from the best ML model."

"The base score is a weighted blend:
0.30*SNA + 0.20*TF-IDF + 0.15*Semantic + 0.10*Tone + 0.15*Engagement + 0.10*ML.
Then reliability multiplier is applied to get final score."

"How to read the weights:
0.30 means SNA contributes 30 percent of base score weight, and so on.
All weights sum to 1.00, so this is a weighted average before reliability adjustment."

"Now I explain one example card in detail using Robert Welsh."

"Robert Welsh is rank #1 in this run.
Final Score is about 0.393.
Signal breakdown is:
SNA 1.000,
TF-IDF 0.311,
Semantic 0.097,
Tone 0.200,
Engagement 0.305,
ML 0.298."

"How to read these numbers:
Final Score 0.393 means his overall recommendation strength after reliability adjustment.
SNA 1.000 means he is the strongest network-positioned creator in this shortlist.
TF-IDF 0.311 means moderate direct keyword overlap with our campaign terms.
Semantic 0.097 means meaning-level alignment is present but relatively weak.
Tone 0.200 means partial tone fit with our campaign communication style.
Engagement 0.305 means moderate observed audience response quality.
ML 0.298 means moderate predicted upside from the ML model."

"Score controls for this card:
Base 0.472,
Reliability x0.833,
Community ID 0.
This means strong base relevance, then a reliability adjustment based on evidence."

"How to read score controls:
Base 0.472 is the weighted score before evidence adjustment.
Reliability x0.833 means we keep 83.3% of base score because evidence quality is good but not perfect.
Community ID 0 is his creator-cluster label used for diversity control, not a quality rank."

"Channel snapshot for Robert Welsh:
22 videos used,
median views about 39,296,
median likes about 3,570,
median comments about 186."

"How to read channel snapshot:
22 videos means the model used 22 recent channel videos as evidence.
Median views 39,296 means a typical video reaches around 39k views.
Median likes 3,570 means typical positive reaction volume per video.
Median comments 186 means typical conversation depth per video."

"The card also gives direct action links:
Open Channel,
Representative Video,
Best Video.
So the team can verify creator fit immediately."

"Below cards, we also show:
Detailed channel table,
and channels down-weighted for weak evidence.
This makes decision risk visible."

---

## Live App Tab 3: Network Studio

"This tab explains creator ecosystem structure using SNA."

"Why we do SNA:
text relevance alone can over-focus on isolated or repetitive creators.
SNA helps us find channels that are both relevant and structurally influential.
It also helps reduce concentration bias."

"How we do SNA:
we build a channel graph from shared tags.
One node is one channel.
An edge exists when channels share enough tags.
Then we compute degree, betweenness proxy, and eigenvector proxy.
These are combined into SNA score.
Then label-propagation detects communities."

"Now I explain this screen's current result."

"Control settings shown:
Nodes in View is 140,
Min Edge Strength is 2,
Communities to Show is 12."

"How to read these control numbers:
Nodes in View 140 means the graph displays up to 140 top nodes for readability.
Min Edge Strength 2 means we keep edges with at least two shared-tag links.
Communities to Show 12 means community summaries are capped for cleaner view."

"From Inspect Node Details,
selected channel is Robert Welsh,
Community is 0,
Final Score is 0.393,
Median Views is 39,296."

"How to read these values:
Community 0 is a cluster label, not a rank level.
Final Score 0.393 is this node's overall recommendation strength.
Median Views 39,296 is this channel's typical view level in our evidence window."

"How to read distance on this network map:
if nodes are visually closer, it usually means they share more topical links in this filtered graph.
if nodes are farther apart, it usually means weaker or fewer direct shared-tag links.
So distance is a relational map signal, not a geographic distance or exact similarity score."

"Community Distribution chart:
we see 5 communities shown.
Largest community share is 53.9 percent.
This means there is one dominant cluster, but still multiple clusters are represented."

"Number meaning:
5 communities shown = 5 distinct clusters visible under current filter settings.
53.9 percent = the largest single cluster contains 53.9 percent of currently shown channels."

"Graph Meta cards:
Nodes 240,
Edges 952,
Dropped Tags 0.
So we are analyzing a fairly dense graph with no over-common tags removed in this view."

"Number meaning:
Nodes 240 = 240 creator channels included in graph construction.
Edges 952 = 952 channel-to-channel topical links after filtering.
Dropped Tags 0 = no ultra-common tags were removed in this specific run."

"Bias Report:
Degree Top Overlap is 5 out of 10.
Unique Communities in Top-N is 2.
Unique Channels in Top-N is 10."

"How to read these three numbers:
5 out of 10 overlap means half of degree-only top list is shared with final hybrid top list.
2 communities means shortlist is spread across two creator clusters.
10 unique channels means no duplicates in Top-10 output."

"Interpretation:
5/10 overlap means final ranking is not just popularity ranking.
It mixes network + text + reliability + ML.
And Top-10 still spans two communities, which gives minimum diversity guardrail."

---

## Live App Tab 4: Text Intelligence

"This tab explains language fit between campaign brief and creator content."

"How we analyze text:
first, TF-IDF compares keyword overlap.
second, semantic score checks meaning-level similarity.
third, tone score checks communication style match.
we also add keyword coverage matrix for must-have terms."

"Current controls in this screen:
Channels for Text Analysis = 30,
Top Terms to Show = 25,
Min Document Frequency = 4."

"Control number meaning:
30 means we analyze top 30 channels for this text view.
25 means we display top 25 frequent terms.
Min document frequency 4 means a term must appear in at least 4 channel documents."

"Text Match Map:
X-axis is TF-IDF similarity.
Y-axis is Semantic alignment.
Color is evidence score.
Bubble size reflects reach proxy from channel scale."

"How to read it:
upper-right is strongest text fit.
If a point is far right but low on Y, keywords match but deeper meaning is weaker.
If Y is high but X is low, meaning is close but explicit keyword coverage is lower."

"Top frequent terms chart shows real vocabulary from candidate channels.
In this run, terms like skin, skincare, products, review, tutorial, and k-beauty style terms appear often.
This supports that shortlisted channels are skincare-focused."

"Keyword Coverage Matrix shows whether each top channel covers:
sunscreen, sensitive skin, SPF, and k-beauty.
Coverage rate chart summarizes this by keyword.
This helps us check message consistency before outreach."

"Leaderboard compares TF-IDF, semantic, tone, and final score together.
So we can explain why a channel ranks high or low in plain language."

---

## Live App Tab 5: ML Studio

"This tab validates prediction quality and model transparency."

"How we do ML:
we run a five-fold cross-validation benchmark.
Models include Linear Regression, LASSO, Ridge, CART, Random Forest, and LightGBM.
Baseline Median is the reference model."

"Five-fold means:
the training data is split into 5 parts, and each part is used once as validation.
This gives a more stable performance estimate than a single split."

"Current result in this screen:
best model is LightGBM.
RMSE is 0.0097,
MAE is 0.0048,
R-squared is 0.9308."

"How to read ML metric numbers:
RMSE 0.0097 is the typical prediction error size; lower is better.
MAE 0.0048 is mean absolute error; lower is better.
R-squared 0.9308 means the model explains about 93 percent of target variance."

"The note below shows baseline comparison:
Baseline RMSE 0.038600 vs LightGBM RMSE 0.009670.
Relative gain is about 74.95 percent."

"Meaning:
0.038600 is error from simple baseline model.
0.009670 is error from best model.
74.95 percent gain means error reduction versus baseline, not revenue increase."

"Predicted vs Actual scatter:
points near diagonal mean better fit.
Color bar is absolute error.
So we can visually check error concentration."

"SHAP section explains feature impact.
In this run, high-impact features include log_views, log_likes, and log_comments.
Dependence plot shows how one selected feature changes prediction contribution."

"This is important for client trust:
we do not only say who is recommended,
we also explain why the model expects upside."

---

## Live App Tab 6: ROI Lab

"This tab converts recommendations into business scenarios."

"How it works:
we input Budget, CPM, CTR, CVR, and AOV.
Then the app calculates impressions, clicks, conversions, revenue, and ROAS."

"Current scenario values on screen:
Budget 50,000 dollars,
CPM 18,
CTR 1.8 percent,
CVR 3.0 percent,
AOV 38 dollars."

"How to read these inputs:
Budget 50,000 = total spend.
CPM 18 = cost per 1,000 impressions is 18 dollars.
CTR 1.8 percent = 1.8 percent of impressions become clicks.
CVR 3.0 percent = 3.0 percent of clicks become conversions.
AOV 38 = average order value per conversion is 38 dollars."

"Result:
Impressions 2,777,777,
Clicks 49,999,
Conversions 1,499,
Expected ROAS 1.14x."

"How to read these outputs:
Impressions 2,777,777 = estimated ad exposures.
Clicks 49,999 = estimated traffic from those exposures.
Conversions 1,499 = estimated purchases/actions.
ROAS 1.14x = expected revenue is 1.14 times spend under this scenario."

"Funnel chart shows each stage from impressions to revenue.
ROAS range shows scenario uncertainty:
about 0.80x to 1.48x."

"Range meaning:
0.80x is conservative scenario, where campaign may not break even.
1.48x is optimistic scenario, where returns are stronger.
This is a scenario band, not a guaranteed interval."

"Budget Sensitivity chart shows two outputs together:
ROAS and conversions over budget grid.
In this setup, conversions increase with budget,
while ROAS is relatively stable unless CTR, CVR, or AOV assumptions change."

"So this tab is not finance decoration.
It is used for spend planning and risk discussion."

---

## Live App Tab 7: Content Strategy

"This tab turns ranking output into creator-ready execution."

"Now I explain one concrete example from this run:
Robert Welsh card."

"Robert Welsh card shows:
Match Score 0.393,
Median Views 39,296,
plus direct channel and representative video links."

"Number meaning:
Match Score 0.393 is his overall fit score after reliability adjustment.
Median Views 39,296 is expected typical reach level for planning."

"Campaign Structure block suggests concepts.
For Concept 1 in this screen:
Daily Routine Integration,
format is tutorial integration,
tone is educational plus authentic,
posting window is weekday evening, 7 to 9 PM local time."

"Time meaning:
7 to 9 PM is a suggested publishing window based on practical audience attention timing,
not a fixed requirement."

"Example ad-copy lines shown in the app:
I added this step because it is easy and lightweight on busy mornings.
If your skin gets irritated easily, this texture and finish are worth testing first."

"Creative Thumbnail Hooks are also generated.
For Robert Welsh, examples include:
7-day real test hook,
problem-solution hook,
and before-after breakdown hook for his audience."

"Meaning of 7-day:
it frames proof period length for audience trust and repeat engagement."

"This means BOJ team does not start from blank page.
The app gives channel-level creative starting points immediately."

---

## Live App Tab 8: Executive Memo

"This tab summarizes recommendations into a client memo.
Sections are organized for quick sharing.
We can download markdown or text for team review."

---

## Live App Tab 9: Glossary + Export

"Glossary defines business terms in plain language.
This helps non-technical stakeholders understand score logic."

"Export Center downloads:
Top-N CSV,
all scored channels CSV,
and executive memo."

"Now I will return to slides and show three BOJ business use cases."

---

## Slide 3: Business Use Case 1 (BOJ Influencer Funnel Execution)

"Use Case 1 is how BOJ should activate Top-10 as a working funnel, not a simple list."

"Top-10 means:
default shortlist size of 10 creators for practical decision review."

"Current Top-10 includes:
Robert Welsh, Tati, Beauty Within, STEPHANIE TOMS, MrsMelissaM,
Dr Alexis Stephens, Mad About Skin, Just Beauty by Julie P, James Welsh, and Morgan Turner."

"Action step 1:
assign funnel roles by signal pattern, not only rank position."

"Awareness-heavy creators:
Tati, Beauty Within, Robert Welsh.
Use broader reach and high discoverability for first exposure."

"What 'Awareness-heavy' means:
these creators are best for upper-funnel discovery.
Their job is to maximize qualified reach and initial product recall,
not immediate hard conversion."

"What BOJ should ask Awareness creators to do:
show product in the first 5 to 10 seconds,
state one clear message such as lightweight SPF for sensitive skin,
and use broad but relevant hooks for discovery."

"How to evaluate Awareness creators:
track CPM, reach, video completion rate, saves, and profile visits.
If reach is high but retention is low, change opening hook first."

"Education and trust creators:
Dr Alexis Stephens, Mad About Skin, James Welsh.
Use myth-busting, ingredient explanation, sensitive-skin routine proof."

"What 'Education and trust' means:
these creators reduce uncertainty in the middle funnel.
Their role is to answer audience questions and remove objections,
such as irritation concern, texture concern, or routine order confusion."

"What BOJ should ask Education creators to do:
publish explainers on ingredient function,
show day and night routine placement,
and respond to top comment objections in follow-up content."

"How to evaluate Education creators:
track meaningful comments, saves, return viewers, and objection resolution rate.
If objection comments remain high, create targeted Q&A clips quickly."

"Conversion-support creators:
STEPHANIE TOMS, MrsMelissaM, Morgan Turner, Julie P.
Use direct try-now CTAs, routine checklists, and before-after framing."

"What 'Conversion-support' means:
these creators are lower-funnel operators.
Their job is to move interested users from intent to purchase action."

"What BOJ should ask Conversion creators to do:
use explicit CTA with link or code,
share concise trial protocol like 7-day or 14-day routine check,
and provide practical decision cues such as skin-type fit and finish."

"How to evaluate Conversion creators:
track CTR, CVR, code usage, checkout-start rate, and ROAS.
If CTR is high but CVR is low, improve landing page-message consistency."

"How to run the funnel operationally:
start with Awareness to fill audience pool,
retarget engaged viewers with Education content,
then push Conversion content to high-intent segments.
This sequence reduces wasted spend versus one-message-for-all execution."

"Action step 2:
allocate budget by role.
Example split:
40 percent Awareness,
35 percent Education,
25 percent Conversion."

"How to read this split:
40/35/25 sums to 100 percent of spend.
This is a starting allocation template that should be updated with weekly KPI results."

"Action step 3:
apply community guardrail.
Keep at least two communities in Top-N to reduce concentration risk."

"Meaning of 'at least two':
it prevents full dependence on one creator cluster and improves audience coverage diversity."

"Action step 4:
set weekly KPI gates by role.
Awareness: CPM, video completion, saves.
Education: comment quality, objection resolution rate.
Conversion: CTR, CVR, code-use rate, and ROAS."

"So BOJ can manage influencer marketing like a structured performance funnel."

---

## Slide 4: Business Use Case 2 (BOJ Content Playbook from Live Output)

"Use Case 2 is content execution using generated strategy blocks."

"Robert Welsh example from our live output:
Concept 1 Daily Routine Integration is already provided.
The app also gives ready thumbnail hooks and posting window."

"Before execution, we define the meaning of each concept clearly."

"Concept 1: Daily Routine Integration.
Meaning:
position BOJ product as an easy daily habit step.
This concept reduces usage friction and increases repeated use probability."

"When to use Concept 1:
for broad audience onboarding and routine adoption.
Best for Awareness and early Consideration stages."

"How to execute Concept 1:
show exact routine order,
highlight texture and comfort for sensitive skin,
and use practical lines like morning routine fit.
Primary CTA should be soft: save this routine, try this step, or test for 7 days."

"Concept 2: Results-Focused Comparison.
Meaning:
provide evidence and differentiation versus alternatives.
This concept builds rational confidence for undecided users."

"When to use Concept 2:
for users already aware of the product but still comparing options.
Best for mid-funnel Education and consideration conversion."

"How to execute Concept 2:
use side-by-side comparison, wear test, before-after, or ingredient-based contrast.
Define one comparison axis per post:
finish, irritation risk, white cast, or routine compatibility.
Primary CTA should be decision-oriented: compare and choose, check full review, or click for detailed breakdown."

"Concept 3: Audience Q&A Conversion Hook.
Meaning:
answer real audience objections and convert intent into action.
This concept turns comment-level questions into purchase-level clarity."

"When to use Concept 3:
for high-intent audiences close to purchase.
Best for lower-funnel conversion support."

"How to execute Concept 3:
pick top objections from comments,
answer in short FAQ format,
and connect each answer to a direct action:
shop link, promo code, or trial checklist.
Primary CTA should be hard CTA: use code now, start trial today, or shop this routine."

"How BOJ should use this in practice:
first, send each creator a customized brief from their strategy card.
second, keep one core message fixed:
lightweight SPF for sensitive or acne-prone skin.
third, allow creator-specific style variation in hook and demonstration format."

"Strategic application rule:
keep product truth fixed, but change concept by funnel stage.
Week 1 should lean Concept 1,
Week 2 to 3 should mix Concept 2,
Week 3 to 4 should increase Concept 3 share for conversion."

"Creator assignment rule:
Awareness creators get Concept 1-heavy briefs.
Education creators get Concept 2-heavy briefs.
Conversion creators get Concept 3-heavy briefs.
This prevents random content mix and improves role clarity."

"Suggested 4-week content cadence:
Week 1: awareness launch videos from top reach creators.
Week 2: educational routine and ingredient explanation.
Week 3: proof content, comparison, and objection handling.
Week 4: conversion push with CTA and recap."

"Week-number meaning:
Week numbers represent execution phases, not strict calendar limits.
The team can compress or extend each phase based on campaign timeline."

"Operationally, after each posting week:
collect top comments,
update exclusion keywords,
and refresh ranking before next wave."

"Optimization rule by concept:
if Concept 1 has reach but low saves, improve opening hook.
if Concept 2 has watch time but low clicks, simplify comparison conclusion.
if Concept 3 has clicks but low CVR, improve landing page and offer clarity."

"This creates a closed loop:
ranking -> content execution -> feedback -> re-ranking."

---

## Slide 5: Business Use Case 3 (BOJ 90-Day Operating Plan)

"Use Case 3 is how BOJ can run this as an ongoing operating system."

"Phase 1, day 0 to 30:
launch pilot with Top-5 creators.
Track base funnel metrics.
In our current ROI base scenario, expected output is about 1,499 conversions at 1.14x ROAS."

"Why Phase 1 is needed:
this period validates assumptions with controlled risk before full-scale spending.
Top-5 means an intentionally focused pilot set.
1,499 conversions and 1.14x ROAS are planning outputs under current assumptions, not guaranteed outcomes."

"Phase 1 day-level strategy:
Day 0 to 7: finalize creator briefs, KPI definitions, and tracking setup.
Reason: without consistent tracking, later optimization is unreliable.
Expected effect: clean baseline data and fewer reporting gaps."

"Day 8 to 20: run first content wave across Awareness, Education, and Conversion roles.
Reason: we need enough live variation to observe role-specific performance.
Expected effect: early signal on which creator-concept pairs produce qualified engagement."

"Day 21 to 30: collect results, diagnose failure points, and lock baseline benchmarks.
Reason: month-1 decisions should be data-led, not intuition-led.
Expected effect: clear keep/fix/pause list for each creator."

"Phase 2, day 31 to 60:
re-rank using observed performance.
Shift budget from weak creators to strong creators.
If conversion is weak, adjust creative angle first before dropping creator."

"Why Phase 2 is needed:
creator performance diverges after first exposure.
If we keep original allocation, budget leakage increases."

"Phase 2 day-level strategy:
Day 31 to 40: re-score creators with observed CTR, CVR, and comment signals.
Reason: replace prior assumptions with real market response.
Expected effect: ranking becomes behavior-based, not only model-based."

"Day 41 to 50: reallocate spend toward top-performing creator-concept pairs.
Reason: concentration on winners improves efficiency.
Expected effect: stronger conversion density per dollar."

"Day 51 to 60: run second-wave validation on revised briefs.
Reason: verify that improvements are repeatable.
Expected effect: reduced false positives and higher confidence before scaling."

"Phase 3, day 61 to 90:
scale winning creator-concept pairs.
Build BOJ creator playbook by audience segment and content type.
Run monthly benchmark check against CeraVe baseline to monitor relative competitiveness."

"Why Phase 3 is needed:
after validation, BOJ should turn one campaign into a repeatable operating system."

"Phase 3 day-level strategy:
Day 61 to 75: scale proven creator-concept combinations to larger spend.
Reason: maximize return from validated assets.
Expected effect: higher absolute conversion volume with controlled risk."

"Day 76 to 85: codify playbook by segment, creator type, and content format.
Reason: institutional memory reduces re-learning cost.
Expected effect: faster launch cycles and more consistent campaign quality."

"Day 86 to 90: executive review, benchmark check, and next-cycle planning.
Reason: leadership needs decision-ready summary for budget approval.
Expected effect: disciplined continuation plan with clear scale/pause criteria."

"Expected business impact of the 90-day system:
faster creator selection cycle,
lower mismatch risk,
better explainability to management,
and more disciplined budget decisions."

---

## Closing

"To conclude, this system is not only a recommendation list.
It is a full workflow:
from campaign brief,
to ranked creators,
to ML validation,
to ROI simulation,
to execution strategy and operating plan."
