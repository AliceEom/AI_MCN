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

"Now I'll start my demo section. Before showing the demo, let me walk through the campaign input."

"For this demo, we entered:
Brand: Beauty of Joseon,
Product: Relief Sun SPF + Glow Serum,
Market: United States,
Budget: 50,000 dollars — this is the total campaign spend assumption used in the ROI simulation. If we change this number, projected impressions, clicks, and conversions change immediately.
Target audience: US Gen Z and Millennial users with sensitive or acne-prone skin."

"We also set must-have keywords and excluded keywords. Must-have keywords increase relevance in text matching, and excluded keywords reduce off-topic channels."

"Each field is functional, so this input directly changes filtering, scoring, and business output."

---

## Slide 2: LIVE DEMO (Open the link and demo live)

"Now I'll move to the live demo. I'll click the demo link now."

---

## Live App: Campaign Brief Page (if shown first)

"This is the campaign brief form. I've already entered the BOJ inputs I went through in the slides. After I click 'Find Influencers,' the pipeline runs data prep, text scoring, social network scoring, ML benchmark, and final ranking."

---

## Live App Tab 1: Overview

"Overview is the quality check tab. Let me walk through the headline metrics first.
Videos analyzed = number of cleaned video records used as evidence.
Channels scored = number of unique creators scored by the model.
Best ML model = model with the lowest cross-validation error in this run.
Top-10 community count = number of distinct creator clusters in shortlist — how many different creator clusters are represented in Top-10. Higher count means better diversity and lower concentration risk."

"Data Reliability tells us whether recommendations are backed by enough channel evidence. Low-evidence channels are down-weighted automatically."

"Now the Benchmark Panel. We show it because a raw score alone has no reference point — benchmark gives us a relative standard."

"We chose CeraVe as our benchmark brand. CeraVe is a practical reference for this BOJ case: same US skincare context, sensitive-skin positioning, and enough comparable creator data in our dataset. So it works as a stable baseline."

"Anchor Mean Score = BOJ Top-N average final score.
Benchmark Mean Score = CeraVe Top-N average final score.
Score Gap = Anchor minus Benchmark.
If the gap is positive, our BOJ shortlist is stronger than benchmark under the same scoring framework — that's comparative evidence for planning."

---

## Live App Tab 2: Top Matches

"This is the decision center. At the top, I can adjust thresholds and ranking behavior."

"Min Match Score sets strictness.
Min Evidence filters weak-data channels.
Ranking Strategy changes score emphasis.
Display Top-N controls shortlist size.
Diversity Preview checks whether we over-concentrate on one cluster."

"Now I'll show the interactive score breakdown chart. Each creator has six signals."

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

"Now let me walk through one example card in detail — Robert Welsh."

"Robert Welsh is rank #1 in this run.
Final Score 0.393 means his overall recommendation strength after reliability adjustment.
SNA 1.000 means he is the strongest network-positioned creator in this shortlist.
TF-IDF 0.311 means moderate direct keyword overlap with our campaign terms.
Semantic 0.097 means meaning-level alignment is present but relatively weak.
Tone 0.200 means partial tone fit with our campaign communication style.
Engagement 0.305 means moderate observed audience response quality.
ML 0.298 means moderate predicted upside from the ML model."

"Score controls for this card:
Base 0.472 is the weighted score before evidence adjustment.
Reliability x0.833 means we keep 83.3% of base score because evidence quality is good but not perfect.
Community ID 0 is his creator-cluster label used for diversity control, not a quality rank."

"Channel snapshot for Robert Welsh:
22 videos means the model used 22 recent channel videos as evidence.
Median views 39,296 means a typical video reaches around 39k views.
Median likes 3,570 means typical positive reaction volume per video.
Median comments 186 means typical conversation depth per video."

"We can also see Channel Snapshot, Keywords, Best Videos, Recent Video Titles, and Recent Audience Comments if data is available."

"The card also gives direct action links — Open Channel, Representative Video, and Best Video — so the team can verify creator fit immediately."

"Below the cards, we also show a detailed channel table, and channels down-weighted for weak evidence. This makes decision risk visible."

---

## Live App Tab 3: Network Studio

"This tab explains creator ecosystem structure using SNA."

"Why we do SNA: text relevance alone can over-focus on isolated or repetitive creators. SNA helps us find channels that are both relevant and structurally influential, and it helps reduce concentration bias."

"How we do SNA: we build a channel graph from shared tags. One node is one channel, and an edge exists when channels share enough tags. Then we compute degree, betweenness proxy, and eigenvector proxy — these are combined into the SNA score. Label-propagation then detects communities."

"Now I'll explain what we're seeing in this screen."

"Control settings shown:
Nodes in View 140 means the graph displays up to 140 top nodes for readability.
Min Edge Strength 2 means we keep edges with at least two shared-tag links.
Communities to Show 12 means community summaries are capped for a cleaner view."

"How to read distance on this network map: if nodes are visually closer, it usually means they share more topical links in this filtered graph. If nodes are farther apart, it usually means weaker or fewer direct shared-tag links. So distance is a relational map signal — not a geographic distance or exact similarity score."

"From Inspect Node Details:
selected channel is Robert Welsh.
Community 0 is a cluster label, not a rank level.
Final Score 0.393 is this node's overall recommendation strength.
Median Views 39,296 is this channel's typical view level in our evidence window."

"Community Distribution chart: we see 5 communities shown. The largest community share is 82 channels for cluster 0 — so there is one dominant cluster 0, but multiple clusters are still represented."

"Graph Meta cards:
Nodes 240 = 240 creator channels included in graph construction.
Edges 952 = 952 channel-to-channel topical links after filtering.
Dropped Tags 0 = no ultra-common tags were removed in this specific run."

"Bias Report: 5 out of 10 overlap means half of the degree-only top list is shared with the final hybrid top list — so the final ranking is not just a popularity ranking. 2 communities means the shortlist is spread across two creator clusters. 10 unique channels means no duplicates in the Top-10 output. Top-10 still spans two communities, which gives a minimum diversity guardrail."

---

## Live App Tab 4: Text Intelligence

"This tab explains language fit between the campaign brief and creator content."

"What text is analyzed here: the primary input is channel-level content text, not raw comment text. This channel text is built from representative video title, video description, and aggregated channel tags."

"How we analyze text: first, TF-IDF compares keyword overlap. Second, semantic score checks meaning-level similarity. Third, tone score checks communication style match. We also add a keyword coverage matrix for must-have terms."

"Current controls in this screen:
30 means we analyze top 30 channels for this text view.
25 means we display top 25 frequent terms.
Min document frequency 4 means a term must appear in at least 4 channel documents."

"Text Match Map:
X-axis is TF-IDF similarity.
Y-axis is Semantic alignment.
Color is evidence score.
Bubble size reflects reach proxy from channel scale."

"How to read it: upper-right is strongest text fit — the creator's content language matches our campaign brief with low translation risk. In other words, BOJ's intended message can be delivered naturally in that creator's usual content style."

"If a point is far right but low on Y, keywords match but deeper meaning is weaker. The channel uses similar words such as SPF or sunscreen, but often in a different context than our target campaign intent. So vocabulary overlap exists, but message intent overlap is limited."

"If Y is high but X is low, meaning is close but explicit keyword coverage is lower. The channel talks about relevant concerns like sensitive skin routines, but uses different wording than our exact keyword list. So this creator can still be valuable, but the brief should provide clearer keyword anchors."

"Simple quadrant interpretation:
upper-right = best immediate message fit.
lower-right = keyword hit but possible context mismatch.
upper-left = good intent fit with different wording.
lower-left = weak fit on both keyword and intent."

"Top frequent terms chart shows real vocabulary from candidate channels. In this run, terms like skin, skincare, products, review, tutorial, and k-beauty style terms appear often — this supports that shortlisted channels are skincare-focused."

"Keyword Coverage Matrix shows whether each top channel covers sunscreen, sensitive skin, SPF, and k-beauty. Coverage rate chart summarizes this by keyword. This helps us check message consistency before outreach."

"Leaderboard compares TF-IDF, semantic, tone, and final score together, so we can explain why a channel ranks high or low in plain language."

---

## Live App Tab 5: ML Studio

"This tab validates prediction quality and model transparency."

"How we do ML: we run a five-fold cross-validation benchmark. Models include Linear Regression, LASSO, Ridge, CART, Random Forest, and LightGBM. Baseline Median is the reference model."

"Five-fold means the training data is split into 5 parts, and each part is used once as validation. This gives a more stable performance estimate than a single split."

"Current result in this screen:
RMSE 0.0097 is the typical prediction error size; lower is better.
MAE 0.0048 is mean absolute error; lower is better.
R-squared 0.9308 means the model explains about 93 percent of target variance."

"The note below shows baseline comparison: Baseline RMSE 0.038600 is from the simple baseline model, versus LightGBM RMSE 0.009670 from the best model. Relative gain is about 74.95 percent — that is error reduction versus baseline, not revenue increase."

"Predicted vs Actual scatter: points near the diagonal mean better fit. Color bar is absolute error, so we can visually check where errors concentrate."

"SHAP section explains feature impact. In this run, high-impact features include log_views, log_likes, and log_comments. Dependence plot shows how one selected feature changes prediction contribution."

"This matters for client trust: we do not only say who is recommended — we also explain why the model expects upside."

---

## Live App Tab 6: ROI Lab

"This tab converts recommendations into business scenarios."

"How it works: we input Budget, CPM, CTR, CVR, and AOV. The app then calculates impressions, clicks, conversions, revenue, and ROAS."

"Current scenario values on screen:
Budget 50,000 = total spend.
CPM 18 = cost per 1,000 impressions is 18 dollars.
CTR 1.8 percent = 1.8 percent of impressions become clicks.
CVR 3.0 percent = 3.0 percent of clicks become conversions.
AOV 38 = average order value per conversion is 38 dollars."

"Result:
Impressions 2,777,777 = estimated ad exposures.
Clicks 49,999 = estimated traffic from those exposures.
Conversions 1,499 = estimated purchases/actions.
ROAS 1.14x = expected revenue is 1.14 times spend under this scenario."

"Funnel chart shows each stage from impressions to revenue. ROAS range shows scenario uncertainty: 0.80x is the conservative scenario, where the campaign may not break even. 1.48x is the optimistic scenario, where returns are stronger. This is a scenario band, not a guaranteed interval."

"Budget Sensitivity chart shows two outputs together: ROAS and conversions over a budget grid. In this setup, conversions increase with budget, while ROAS stays relatively stable unless CTR, CVR, or AOV assumptions change."

"So this tab is not finance decoration — it is used for spend planning and risk discussion."

---

## Live App Tab 7: Content Strategy

"This tab turns ranking output into creator-ready execution."

"Let me walk through one concrete example from this run: the Robert Welsh card."

"Robert Welsh card shows:
Match Score 0.393 — his overall fit score after reliability adjustment.
Median Views 39,296 — expected typical reach level for planning.
Plus direct channel and representative video links."

"Campaign Structure block suggests concepts. For Concept 1 in this screen:
Daily Routine Integration,
format is tutorial integration,
tone is educational plus authentic,
posting window is weekday evening, 7 to 9 PM local time."

"On the time window: 7 to 9 PM is a suggested publishing window based on practical audience attention timing — not a fixed requirement."

"Example ad-copy lines shown in the app:
'I added this step because it is easy and lightweight on busy mornings.'
'If your skin gets irritated easily, this texture and finish are worth testing first.'"

"Creative Thumbnail Hooks are also generated. For Robert Welsh, examples include a 7-day real test hook, a problem-solution hook, and a before-after breakdown hook for his audience."

"On the 7-day framing: it frames proof period length for audience trust and repeat engagement."

"What this means for the BOJ team: they don't start from a blank page. The app gives channel-level creative starting points immediately."

---

## Live App Tab 8: Executive Memo

"This tab summarizes recommendations into a client memo. Sections are organized for quick sharing, and we can download markdown or text for team review."

---

## Live App Tab 9: Glossary + Export

"Glossary defines business terms in plain language — this helps non-technical stakeholders understand the score logic."

"Now I'll return to slides and show three BOJ business use cases."

---

## Slide 3: Business Use Case 1 (BOJ Influencer Funnel Execution)

"Use Case 1 is The Influencer Funnel."

"Core message from the slide: use different creative objectives by role, not one message for all creators."

"Why this matters: a role split improves budget efficiency across the full customer journey."

"Role Group 1 creators: Robert Welsh, Tati, Beauty Within, James Welsh, Morgan Turner."

"How to use Role Group 1: this is the upper-funnel awareness group. BOJ should ask them to maximize discovery with broad hooks, clear first-impression messaging, and easy routine entry points."

"Role Group 2 creators: MrsMelissaM, Dr Alexis Stephens, Julie P."

"How to use Role Group 2: this is the education and consideration support group. BOJ should ask them for ingredient explanation, routine detail, and objection-handling content."

"Role Group 3 creators: STEPHANIE TOMS, Mad About Skin."

"How to use Role Group 3: this is the conversion support group. BOJ should ask them for direct CTA content, trial protocol, and purchase-oriented recap."

"Execution rule: do not send one identical brief to all creators. Send role-specific briefs, role-specific KPIs, and role-specific CTAs."

---

## Slide 4: Business Use Case 2 (BOJ Content Playbook from Live Output)

"Use Case 2 is Content Strategy."

"Core message from the slide: execute by week, then re-rank with weekly KPI feedback."

"Week 1: Awareness.
Week 2: Education plus routine detail.
Week 3: Product proof and comparison.
Week 4: Conversion CTA plus recap."

"What each week means in practice:
Week 1 builds initial reach and message recall.
Week 2 reduces uncertainty with tutorial and explanation content.
Week 3 gives proof with comparison and performance evidence.
Week 4 pushes action with explicit CTA and summarizes winning messages."

"How to execute each week:
Week 1: lead creators publish discovery hooks and simple product framing.
Week 2: support creators publish routine order and sensitive-skin guidance.
Week 3: creators publish proof formats — comparison, wear test, or before-after.
Week 4: conversion-focused creators publish direct CTA content with link and code reminders."

"Concept mapping for this slide:
Concept 1 means Daily Routine Integration.
Concept 2 means Results-Focused Comparison.
Concept 3 means Audience Q&A Conversion Hook."

"How to apply Concept 1, 2, and 3:
Use Concept 1 in Week 1 to make product use feel easy and natural.
Use Concept 2 in Weeks 2 and 3 to build confidence with evidence.
Use Concept 3 in Weeks 3 and 4 to convert high-intent users from question to action."

"Operational note: after each week, review KPI outcomes and re-rank creators. Then shift next-week content focus toward the best-performing concept-creator combinations."

---

## Slide 5: Business Use Case 3 (BOJ 90-Day Operating Plan)

"Use Case 3 is how BOJ can run this as an ongoing operating system."

"0 to 30 Days: Launch and Track. Launch Top-10 with tiered budget allocation. Deploy 3 lead creators, 4 support creators, and 3 pilots. Standardize tracking links and KPI definitions such as CTR, CVR, and ROAS."

"What this phase means: this is controlled market entry. Tiered allocation limits risk while BOJ learns which creator roles and concepts perform best."

"Why 3 lead, 4 support, 3 pilots: lead creators secure reach, support creators stabilize education, and pilots test upside with limited risk before scale."

"31 to 60 Days: Re-Rank and Reallocate. Re-rank creators by observed conversion data. Shift budget from weak pilots to the strongest conversion creators. Update AI keyword exclusion logic based on comment feedback."

"What this phase means: this is optimization. BOJ replaces assumption-based allocation with observed performance-based allocation."

"Expected effect: lower wasted spend, stronger conversion efficiency, and cleaner targeting logic."

"61 to 90 Days: Scale and Playbook. Build Beauty of Joseon's creator playbook by sub-segment, such as acne-prone and daily-use groups. Run continuous monthly competitor benchmarks."

"What this phase means: this is standardization and scale. BOJ turns one campaign into repeatable operating knowledge."

"Expected effect: faster future campaign setup, consistent execution quality, and ongoing competitive calibration with monthly benchmark checks."
