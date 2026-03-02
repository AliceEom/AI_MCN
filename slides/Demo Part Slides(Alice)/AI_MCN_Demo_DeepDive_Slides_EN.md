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

- Run timestamp (UTC): **2026-03-02T14:02:53Z**
- Videos analyzed: **42,750**
- Channels scored: **1,089**
- Best ML model: **LightGBM**
- Top-10 mean final score: **0.307**
- Top-10 mean evidence score: **0.702**
- Top-10 community coverage: **2 communities**
- BOJ vs CeraVe mean Top-N gap: **+0.047**
- ROI base scenario: **ROAS 1.14x** (0.80x-1.48x)

---

# Slide 6) BOJ Top-10 Recommended Influencers (latest synced output)

- #1 Robert Welsh (0.394)
- #2 Tati (0.327)
- #3 Beauty Within (0.324)
- #4 STEPHANIE TOMS (0.318)
- #5 MrsMelissaM (0.307)
- #6 Dr Alexis Stephens (0.307)
- #7 Mad About Skin (0.283)
- #8 Just Beauty by Julie P - makeup, beauty reviews (0.273)
- #9 James Welsh (0.270)
- #10 Morgan Turner (0.270)

Role split recommendation:
- Scale/Awareness: Robert Welsh, Tati, Beauty Within, James Welsh, Morgan Turner
- Conversion/Fit: STEPHANIE TOMS, Mad About Skin
- Education/Support: MrsMelissaM, Dr Alexis Stephens, Julie P

---

# Slide 7) Representative Deep Dive (Example: #1 Robert Welsh)

## Channel profile (from latest output)
- Final score: **0.394**
- Evidence score: **0.743**
- TF-IDF: **0.311**
- Semantic: **0.097**
- SNA: **1.000**
- Engagement: **0.305**
- Reliability multiplier: **0.833**
- n_videos used: **22**
- Median views: **39,296.5**
- Recent publish: **2026-02-24**

## Why this creator is useful for BOJ
- Very strong network position (SNA max), with stable evidence level
- Keyword-level fit is practical for sunscreen/skincare campaign intent
- Good candidate for trust-building educational review format

## Suggested content package
- Primary concept: **Concept 1 (Daily Routine)**
- Backup concept: **Concept 3 (Audience Q&A Conversion Hook)**
- Product angle: lightweight daily SPF for sensitive/acne-prone users

---

# Slide 8) BOJ Channel-to-Content Strategy Mapping

- **Concept 1 (Daily Routine)**
  - Robert Welsh, Tati, Beauty Within, James Welsh, Morgan Turner
- **Concept 3 (Q&A Conversion Hook)**
  - MrsMelissaM, Dr Alexis Stephens, Julie P
- **Concept 2 (Results comparison)**
  - STEPHANIE TOMS, Mad About Skin

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
- Robert Welsh: **~$5.7K**, **~170 conversions**
- Tati: **~$5.7K**, **~169 conversions**
- Beauty Within: **~$5.2K**, **~157 conversions**
- James Welsh: **~$5.1K**, **~154 conversions**
- Dr Alexis Stephens: **~$5.0K**, **~149 conversions**

Business interpretation:
- Reach-heavy creators = awareness scale
- Fit-heavy creators = conversion quality
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
