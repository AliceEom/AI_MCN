# AI-MCN Demo + BOJ Business Insight Deck (Synced to Latest Default Run)

## Presentation flow
1. Slide 1: click live demo link
2. Live demo: explain all tabs
3. Return to slides: BOJ business application from this exact run
4. Return to slides: beauty-industry operating insights

---

# Slide 1) Live Demo Link

- Put Streamlit URL as clickable button/text
- One-sentence objective:
  - "I will show how campaign input becomes a Top-10 influencer execution plan with explainable evidence."

---

# Slide 2) Live Demo Roadmap (all tabs)

- Campaign Input
- Overview
- Top Matches
- Network Studio
- Text Intelligence
- ML Studio
- ROI Lab
- Content Strategy
- Executive Memo / Glossary / Export

---

# Slide 3) Live Demo checkpoint (what audience should observe)

- What each score means
- Why each creator is ranked
- How threshold controls change shortlist risk
- How ROI and strategy outputs connect to business decisions

---

# Slide 4) BOJ Context: Why this client case matters

- BOJ is a K-beauty brand scaling in global skincare markets
- Demo product: **Relief Sun SPF + Glow Serum**
- BOJ challenge in U.S. influencer marketing:
  - find creators with both relevance and purchase intent
  - reduce mismatch between high reach and low product fit
  - reduce manual screening time

Reference links for slide notes:
- [NIQ K-beauty landscape (2025)](https://nielseniq.com/global/en/news-center/2025/how-k-beauty-is-shaping-the-global-beauty-landscape/)
- [Fashionista BOJ U.S. strategy feature (Nov 13, 2024)](https://fashionista.com/2024/11/beauty-of-joseon-k-beauty-skin-care-us-launch-strategy)
- [BOJ official campaign page](https://beautyofjoseon.com/pages/rice-wonderland)

---

# Slide 5) BOJ Run Facts (latest synced output)

- Run timestamp (UTC): **2026-03-02T15:03:00Z**
- Videos analyzed: **42,750**
- Channels scored: **1,089**
- Best ML model: **LightGBM**
- Top-10 mean final score: **0.266**
- Top-10 mean evidence score: **0.657**
- Top-10 community coverage: **2 communities**
- BOJ vs CeraVe mean Top-N gap: **+0.047**
- ROI base scenario: **ROAS 1.14x** (0.80x–1.48x)

---

# Slide 6) BOJ Top-10 Recommended Influencers (latest synced output)

- #1 AliceintheRabbitHole (0.304)
- #2 Dr. Sam Ellis (0.292)
- #3 NikkieTutorials (0.291)
- #4 Fit beauty (0.278)
- #5 James Welsh (0.277)
- #6 Dr. Usama Syed (0.257)
- #7 Mixed Makeup (0.254)
- #8 Dr Madiha Nisar (0.239)
- #9 Lab Muffin Beauty Science (0.233)
- #10 Cassandra Bankson (0.231)

Role split recommendation:
- Scale/Awareness: NikkieTutorials, Fit beauty, James Welsh, Mixed Makeup, Cassandra Bankson
- Education/Support: Dr. Sam Ellis, Dr. Usama Syed, Lab Muffin Beauty Science
- Conversion/Fit: AliceintheRabbitHole, Dr Madiha Nisar

---

# Slide 7) Representative Deep Dive (Example: #1 AliceintheRabbitHole)

## Channel profile (from latest output)
- Final score: **0.304**
- Evidence score: **0.547**
- TF-IDF: **0.784** ← highest in shortlist
- Semantic: **0.227**
- SNA: **0.522**
- Tone: **0.400**
- Engagement: **0.130**
- ML: **0.233**
- Base score: **0.430**
- Reliability multiplier: **x0.706**
- Community ID: **0**
- n_videos used: **89**
- Median views: **10,858**
- Median likes: **586**
- Subscribers (est.): **57,700**
- Recent publish: **2026-02-27**

## Why this creator is useful for BOJ
- Highest TF-IDF in the shortlist (0.784) — content vocabulary is most closely aligned with campaign keywords
- K-beauty and acne-prone/dry skin focused channel, directly matching target audience profile
- Recent content includes BOJ-adjacent K-beauty hauls and sunscreen reviews
- Good candidate for conversion-support or routine integration format

## Suggested content package
- Primary concept: **Concept 1 (Daily Routine Integration)**
- Backup concept: **Concept 3 (Audience Q&A Conversion Hook)**
- Product angle: lightweight daily SPF for sensitive/acne-prone users

---

# Slide 8) BOJ Channel-to-Content Strategy Mapping

- **Concept 1 (Daily Routine Integration)**
  - AliceintheRabbitHole, NikkieTutorials, Fit beauty, James Welsh
- **Concept 2 (Results-Focused Comparison)**
  - Mixed Makeup, Dr Madiha Nisar, Cassandra Bankson
- **Concept 3 (Audience Q&A Conversion Hook)**
  - Dr. Sam Ellis, Dr. Usama Syed, Lab Muffin Beauty Science

Execution cadence:
- Week 1: awareness launch
- Week 2: education + routine detail
- Week 3: objection handling + conversion CTA
- Week 4: recap + re-allocation based on KPI

---

# Slide 9) BOJ Budget Allocation Scenario (latest synced run)

## Assumption
- Total budget: **$50,000**
- Allocation weight = 55% final score + 25% evidence + 20% reach index

## Example outputs
- AliceintheRabbitHole: **~$4.8K** (conversion track lead)
- Dr. Sam Ellis: **~$5.2K** (education track lead, 790K subs)
- NikkieTutorials: **~$6.5K** (awareness track lead, 15M subs)
- Fit beauty: **~$5.5K** (awareness support, 6M subs)
- James Welsh: **~$5.0K** (awareness + K-beauty angle, 1.56M subs)

Business interpretation:
- Reach-heavy creators = awareness scale (NikkieTutorials, Fit beauty)
- Fit-heavy creators = conversion quality (AliceintheRabbitHole, Dr Madiha Nisar)
- Run both tracks in parallel with weekly re-ranking

---

# Slide 10) Analysis-to-Action Framework for BOJ

- **Top Matches / Final Score**
  - Use as shortlist, not final budget decision alone
- **Evidence + Reliability Multiplier**
  - Core spend only above evidence threshold
  - Pilot cap for low-activity channels
- **Text Intelligence (TF-IDF + Semantic)**
  - Assign conversion creatives to high language+meaning fit channels
- **Network Studio (Community/SNA)**
  - Keep at least 2 clusters in active spend
- **ML Studio**
  - Validate score stability before major reallocation
- **ROI Lab**
  - Use scenario ranges in budget approval and weekly optimization

---

# Slide 11) BOJ 30-60-90 Day Action Plan

## 0-30 days
- Launch Top-10 with tiered budget
- Start with lead creators + support creators + pilots

## 31-60 days
- Re-rank with observed CTR/CVR/ROAS
- Move budget from weak pilots to strong converters

## 61-90 days
- Build BOJ creator playbook by sub-segment
- Run monthly benchmark vs competitor profile

---

# Slide 12) BOJ KPI Governance (weekly)

- CTR
- CVR
- ROAS
- Branded search lift
- Comment quality / repeated objections
- Community concentration ratio

Decision rules:
- Increase: stable CVR + stable evidence
- Hold/test: mixed but strategic
- Reduce/exit: weak CVR + low evidence + off-message

---

# Slide 13) Beauty Industry Insight #1 (from this run)

- High network strength and high semantic fit are not always the same creators
- Single flat top-list can waste spend
- Better structure:
  - awareness track
  - conversion track
  - controlled test track

---

# Slide 14) Beauty Industry Insight #2 (scalable model)

- Standard cycle:
  - brief input -> explainable ranking -> strategy mapping -> ROI scenarios -> export
- Repeat every launch, not one-off
- Keep audit trail:
  - rationale text
  - risk flags
  - benchmark deltas
  - exported decision files

---

# Slide 15) Closing

- "For BOJ, this is not only a recommendation list; it is an execution plan."
- "For beauty brands, AI-MCN turns influencer marketing into measurable decision operations."
