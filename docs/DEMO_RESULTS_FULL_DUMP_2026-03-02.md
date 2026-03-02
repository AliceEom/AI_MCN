# AI-MCN Demo Result Full Dump (Synced to Latest Interactive Top-10)

- Generated UTC: 2026-03-02T14:18:56.836201+00:00
- Workspace: `/Users/alice/521_Marketing`
- Sync rule: All top-match references in this file use `artifacts/reports/top10_beauty_of_joseon.csv`.
- Purpose: single source dump for PPT/script generation and audit trail.

## 1) Artifact Inventory
### /Users/alice/521_Marketing/artifacts/reports/presentation_summary_boj.json
- exists: True
- size_bytes: 6873
- mtime_utc: 2026-03-02T14:14:50.698496+00:00

### /Users/alice/521_Marketing/artifacts/reports/top10_beauty_of_joseon.csv
- exists: True
- size_bytes: 93172
- mtime_utc: 2026-03-02T14:14:50.696245+00:00

### /Users/alice/521_Marketing/artifacts/reports/scored_channels_beauty_of_joseon.csv
- exists: True
- size_bytes: 5879455
- mtime_utc: 2026-03-02T14:02:53.244614+00:00

### /Users/alice/521_Marketing/artifacts/reports/ml_cv_results.csv
- exists: True
- size_bytes: 978
- mtime_utc: 2026-03-02T14:02:53.245265+00:00

### /Users/alice/521_Marketing/artifacts/reports/memo_beauty_of_joseon.md
- exists: True
- size_bytes: 1372
- mtime_utc: 2026-03-02T14:02:53.244923+00:00

## 2) Run Snapshot (Current Synced Values)
- timestamp_utc: `2026-03-02T14:02:53Z`
- videos_analyzed: `42750`
- channels_scored: `1089`
- best_ml_model: `LightGBM`
- top10_mean_final_score: `0.307211`
- top10_mean_evidence_score: `0.702420`
- top10_community_count: `2`
- benchmark_brand: `CeraVe`
- benchmark_topn_mean: `0.259856`
- boj_minus_benchmark_gap: `+0.047355`

## 3) Top-10 Table (Exact Current CSV)
```text
                                  channel_title  final_score  evidence_score  community_id  n_videos  median_views  median_likes  median_comments  sna_score  tfidf_similarity  semantic_score  tone_match_score  engagement_score  credibility_multiplier
                                   Robert Welsh     0.393585        0.743473             0        22       39296.5        3570.0            186.5   1.000000          0.311260        0.096838               0.2          0.305069                0.833258
                                           Tati     0.326544        0.803944             0        24      122059.0        5625.0            334.0   0.969146          0.070467        0.030354               0.2          0.191023                0.872563
                                  Beauty Within     0.323781        0.723207             1        22       32834.0        1236.5             57.0   0.618970          0.557558        0.187303               0.4          0.117745                0.820085
                                 STEPHANIE TOMS     0.318391        0.669059             0        17       17045.0        1222.0            133.0   0.629922          0.481461        0.141638               0.4          0.235372                0.784888
                                    MrsMelissaM     0.307128        0.656373             1        25        4915.0         742.0             71.0   0.728540          0.098924        0.040012               0.4          0.442807                0.776642
                             Dr Alexis Stephens     0.306796        0.672531             1        15       28608.0        1007.0             27.0   0.671867          0.477018        0.164154               0.4          0.100353                0.787145
                                 Mad About Skin     0.283049        0.715017             1        25       19289.0        1069.0             86.0   0.548257          0.348039        0.105646               0.4          0.246363                0.814761
Just Beauty by Julie P - makeup, beauty reviews     0.273338        0.556961             0        25         903.0           0.0             59.0   0.890528          0.098134        0.038602               0.4          0.216166                0.712025
                                    James Welsh     0.269791        0.762113             1        22       63281.0        3335.5            333.0   0.494865          0.424015        0.143647               0.2          0.180098                0.845374
                                  Morgan Turner     0.269705        0.721522             0        23       24748.0        1768.0            107.0   0.802862          0.038389        0.016092               0.2          0.252106                0.818989
```

## 4) Top-10 Ranked List (Short Form)
- #1 Robert Welsh | final=0.393585 | evidence=0.743473
- #2 Tati | final=0.326544 | evidence=0.803944
- #3 Beauty Within | final=0.323781 | evidence=0.723207
- #4 STEPHANIE TOMS | final=0.318391 | evidence=0.669059
- #5 MrsMelissaM | final=0.307128 | evidence=0.656373
- #6 Dr Alexis Stephens | final=0.306796 | evidence=0.672531
- #7 Mad About Skin | final=0.283049 | evidence=0.715017
- #8 Just Beauty by Julie P - makeup, beauty reviews | final=0.273338 | evidence=0.556961
- #9 James Welsh | final=0.269791 | evidence=0.762113
- #10 Morgan Turner | final=0.269705 | evidence=0.721522

## 5) Top-1 Detailed Breakdown (Current #1)
- channel_title: `Robert Welsh`
- final_score: `0.3935849124594588`
- final_score_base: `0.4723448034483355`
- credibility_multiplier: `0.833257632107111`
- evidence_score: `0.7434732801647861`
- sna_score: `1.0`
- tfidf_similarity: `0.3112602038855218`
- semantic_score: `0.0968382421611037`
- tone_match_score: `0.2`
- engagement_score: `0.3050693261320708`
- n_videos: `22`
- median_views: `39296.5`
- median_likes: `3570.0`
- median_comments: `186.5`
- community_id: `0`
- latest_publish: `2026-02-24 20:30:00+00:00`
- channel_url: `https://www.youtube.com/channel/UC2GUcyD6KYjmU_ofQtPTSSA`

## 6) Formula Dictionary (How scores are combined)
- `final_score_base = 0.30*SNA + 0.20*TF-IDF + 0.15*Semantic + 0.10*Tone + 0.15*Engagement + 0.10*ML`
- `final_score = final_score_base * credibility_multiplier`
- `credibility_multiplier = clip(0.35 + 0.65*evidence_score, 0.20, 1.00)`
- ROI base formulas:
  - `impressions = (budget/cpm)*1000`
  - `clicks = impressions*ctr`
  - `conversions = clicks*cvr`
  - `revenue = conversions*aov`
  - `roas = revenue/budget`

## 7) Derived Budget Plan (Current Top-10)
```text
                                  channel_title activation_tier                 content_concept  plan_budget_usd  plan_clicks  plan_conversions  plan_revenue_usd
                                   Robert Welsh        Balanced               Concept 1 + 3 Mix           5674.0       5674.0             170.0            6465.0
                                           Tati        Balanced               Concept 1 + 3 Mix           5651.0       5651.0             169.0            6438.0
                                  Beauty Within        Balanced Concept 3 (Q&A Conversion Hook)           5222.0       5221.0             157.0            5949.0
                                    James Welsh        Balanced               Concept 1 + 3 Mix           5136.0       5136.0             154.0            5851.0
                             Dr Alexis Stephens        Balanced Concept 3 (Q&A Conversion Hook)           4984.0       4984.0             149.0            5678.0
                                 STEPHANIE TOMS        Balanced Concept 3 (Q&A Conversion Hook)           4952.0       4952.0             148.0            5642.0
                                 Mad About Skin        Balanced Concept 3 (Q&A Conversion Hook)           4895.0       4895.0             147.0            5577.0
                                  Morgan Turner        Balanced               Concept 1 + 3 Mix           4881.0       4881.0             146.0            5561.0
                                    MrsMelissaM        Balanced Concept 3 (Q&A Conversion Hook)           4654.0       4654.0             140.0            5302.0
Just Beauty by Julie P - makeup, beauty reviews        Balanced Concept 3 (Q&A Conversion Hook)           3950.0       3950.0             118.0            4500.0
```

## 8) ML CV Table (Current)
```text
           model    status  mae_mean  mae_std  rmse_mean  rmse_std   r2_mean   r2_std
        LightGBM        ok  0.004481 0.000929   0.009949  0.004414  0.924341 0.051196
    RandomForest        ok  0.006939 0.001414   0.014626  0.005052  0.839615 0.074729
            CART        ok  0.012186 0.001288   0.020768  0.003553  0.677443 0.059913
           LASSO        ok  0.017386 0.001268   0.027381  0.004706  0.443109 0.080518
           Ridge        ok  0.017411 0.001266   0.027397  0.004701  0.440396 0.100052
LinearRegression        ok  0.017413 0.001268   0.027405  0.004705  0.439945 0.101242
  BaselineMedian reference  0.024488 0.000000   0.038003  0.000000 -0.054314 0.000000
```

## 9) ROI Snapshot (Current)
```json
{
  "budget_usd": 50000.0,
  "cpm": 18.0,
  "ctr": 0.018,
  "cvr": 0.03,
  "aov": 38.0,
  "impressions": 2777777,
  "clicks": 49999,
  "conversions": 1499,
  "revenue": 56962.0,
  "roas": 1.13924,
  "roas_low": 0.797468,
  "roas_high": 1.481012
}
```

## 10) Bias + Benchmark Snapshot (Current)
```json
{
  "bias_report": {
    "degree_top_overlap": 3,
    "degree_top_channels": [
      {
        "channel_title": "NikkieTutorials",
        "degree_centrality": 0.17095588235294118
      },
      {
        "channel_title": "Sephora",
        "degree_centrality": 0.15900735294117646
      },
      {
        "channel_title": "Ruth Crilly",
        "degree_centrality": 0.14154411764705882
      },
      {
        "channel_title": "SLMD Skincare",
        "degree_centrality": 0.13878676470588236
      },
      {
        "channel_title": "LOLA Beauty and Acne Treatment",
        "degree_centrality": 0.13511029411764705
      },
      {
        "channel_title": "Beauty By Soane",
        "degree_centrality": 0.1332720588235294
      },
      {
        "channel_title": "Dermatologist's Choice Skincare DermChoice",
        "degree_centrality": 0.12959558823529413
      },
      {
        "channel_title": "best sunscreen online",
        "degree_centrality": 0.12683823529411764
      },
      {
        "channel_title": "Fit beauty",
        "degree_centrality": 0.12683823529411764
      },
      {
        "channel_title": "MJ makeup artist 1234",
        "degree_centrality": 0.125
      }
    ],
    "top_n": 10,
    "n_unique_final": 10,
    "n_unique_communities_topn": 2,
    "narrative": "Overlap between degree-only top-10 and hybrid top-10 is 3/10. Lower overlap indicates reduced popularity bias."
  },
  "benchmark": {
    "brand": "CeraVe",
    "top_channel": "Dr. Usama Syed",
    "top_score": 0.31309977456026467,
    "topn_mean_score": 0.2598561438540761,
    "top5_mean_score": 0.28159725105430533
  }
}
```

## 11) Memo Snapshot (Current)
```text
# Brand Partnership Recommendation Memo
**Brand:** Beauty of Joseon
**Product:** Relief Sun SPF + Glow Serum
**Budget:** $50,000

## Executive Summary
The model identified 10 high-fit creators for Beauty of Joseon. The expected ROAS under base assumptions is 1.14x (range: 0.80x-1.48x).

## Priority Recommendation
Prioritize **AliceintheRabbitHole** first. Final score=0.302, SNA=0.522, Text fit=0.741, Engagement=0.130.

## Campaign Structure (4 Weeks)
1. Week 1: Awareness launch with creator #1 and #2.
2. Week 2: Education-focused tutorials and Q&A clips.
3. Week 3: Product proof and comparison content.
4. Week 4: Conversion push with promo CTA and recap content.

## Risk Flags
- NikkieTutorials: Low semantic relevance to brand brief
- James Welsh: Low semantic relevance to brand brief
- Fit beauty: Low semantic relevance to brand brief
- Dr. Sam Ellis: Low semantic relevance to brand brief
- Dr. Usama Syed: Low semantic relevance to brand brief
- Mixed Makeup: Low semantic relevance to brand brief
- Mandvi Singh : Low semantic relevance to brand brief
- Dr Madiha Nisar: Low semantic relevance to brand brief
- Dermatologist's Choice Skincare DermChoice: Low semantic relevance to brand brief

## Next Steps
1. Confirm creator availability and rate cards.
2. Finalize creative brief and legal requirements.
3. Launch a 2-week test and monitor CTR/CVR/ROAS.
```

## 12) Raw Top-10 Channel JSON (All fields)
### #1 Robert Welsh
```json
{
  "_channel_id": "UC2GUcyD6KYjmU_ofQtPTSSA",
  "n_videos": 22,
  "median_views": 39296.5,
  "median_likes": 3570.0,
  "median_comments": 186.5,
  "mean_engagement": 0.0884248909073552,
  "latest_publish": "2026-02-24 20:30:00+00:00",
  "representative_video_id": "NHuwDL5eEYI",
  "video_title": "PAINFUL lip plumper!! But is it worth it? #lipplumper #lipgloss",
  "tags_text": "lip plumper kbeauty vt reedle shot lip yesstyle yesstyle coupon code korean skincare",
  "video_description": "Using VT reedle shit plumping lip gloss EXTREME plumping gloss!!\n\nyou can find it here (if you can stand the pain) - https://tidd.ly/4t6yimS\n\n\n\n\n*LET’S STAY CONNECTED!*\n\nSubscribe to my new Beauty Blog \"Brushed Up\" - https://robertwelsh.substack.com/?r=4nf54q&utm_medium=ios&utm_source=profile\n\nInstagram - @RobertWLSH\nTwitter - @RWLSHmakeup\nTikTok - RobertWelshMUA\n\n*DISCOUNTS*\n\n\nYESSTYLE | 10% OFF ORDERS OVER $49\nCODE | ROBERT10\nhttps://shrsl.com/4it5e\n\nSIGMA BEAUTY | 10% OFF\nCODE | Robert10\nHttps://sigmabeauty.com/ROBERT10\n\nCOLOURPOP | 10% OFF\nCODE | ROBERT\nhttps://colourpop.sjv.io/P26Z6\n\nOlive young KBeauty \nCODE | ROBERTW1 \nhttps://global.oliveyoung.com/if/rd?su=DZLODI8A\n\nFlower Knows | 5% OFF\nCODE | RobertMUA\nhttps://flowerknows.co/?ref=RobertMUA",
  "all_tags": "['foundation repair', 'makeup', 'mua', 'foundation', 'long lasting foundation', 'foundation application', 'shorts', 'makeup tutorial for beginners', 'makeup tutorial', 'skincare', 'beauty', 'beginner makeup tutorial', 'everyday makeup tutorial', 'how to do makeup', 'beauty tips', 'make up', 'how to makeup', 'robert welsh', 'robert welsh mua', 'makeup dupes', 'beauty dupes', 'drugstore makeup', 'high end makeup', 'makeup comparison', 'beauty review', 'viral makeup', 'affordable makeup', 'luxury makeup', 'makeup testing', 'dupes vs high end', 'beauty youtube', 'makeup review', 'viral beauty products', 'makeup wear test', 'beauty influencer', 'makeup swatches', 'honest beauty review', 'makeup by mario', 'makeup by mario jelly jar', 'makeup by mario jelly', 'makeup by mario jelly blush', 'fwee', 'fwee makeup', 'fwee pudding pot', 'fwee pudding pot swatch', 'beauty drama', 'makeup drama', 'beauty community drama', 'beauty brands scandals', 'makeup brands controversy', 'cancelled beauty brands', 'problematic brands', 'beauty commentary', 'makeup commentary', 'influencer drama', 'beauty industry drama', 'unethical brands', 'brand scandals', 'makeup brands exposed', 'beauty community tea', 'iso clean', 'bperfect cosmetics', 'il makiage', 'elf', 'sheglam', 'she glam cosmetics', 'sheglam cosmetics', 'robert welsh', 'robert welsh mua', 'kbeauty', 'kbeauty', 'k-beauty', 'fwee', 'fwee', 'fwee lip gloss', 'fwee lip tint', 'korean makeup', 'olive young haul', 'k beauty', 'korean beauty']",
  "channel_text": "painful lip plumper!! but is it worth it? #lipplumper #lipgloss using vt reedle shit plumping lip gloss extreme plumping gloss!! you can find it here (if you can stand the pain) - https://tidd.ly/4t6yims *let’s stay connected!* subscribe to my new beauty blog \"brushed up\" - https://robertwelsh.substack.com/?r=4nf54q&utm_medium=ios&utm_source=profile instagram - @robertwlsh twitter - @rwlshmakeup tiktok - robertwelshmua *discounts* yesstyle | 10% off orders over $49 code | robert10 https://shrsl.com/4it5e sigma beauty | 10% off code | robert10 https://sigmabeauty.com/robert10 colourpop | 10% off code | robert https://colourpop.sjv.io/p26z6 olive young kbeauty code | robertw1 https://global.oliveyoung.com/if/rd?su=dzlodi8a flower knows | 5% off code | robertmua https://flowerknows.co/?ref=robertmua foundation repair makeup mua foundation long lasting foundation foundation application shorts makeup tutorial for beginners makeup tutorial skincare beauty beginner makeup tutorial everyday makeup tutorial how to do makeup beauty tips make up how to makeup robert welsh robert welsh mua makeup dupes beauty dupes drugstore makeup high end makeup makeup comparison beauty review viral makeup affordable makeup luxury makeup makeup testing dupes vs high end beauty youtube makeup review viral beauty products makeup wear test beauty influencer makeup swatches honest beauty review makeup by mario makeup by mario jelly jar makeup by mario jelly makeup by mario jelly blush fwee fwee makeup fwee pudding pot fwee pudding pot swatch beauty drama makeup drama beauty community drama beauty brands scandals makeup brands controversy cancelled beauty brands problematic brands beauty commentary makeup commentary influencer drama beauty industry drama unethical brands brand scandals makeup brands exposed beauty community tea iso clean bperfect cosmetics il makiage elf sheglam she glam cosmetics sheglam cosmetics robert welsh robert welsh mua kbeauty kbeauty k-beauty fwee fwee fwee lip gloss fwee lip tint korean makeup olive young haul k beauty korean beauty",
  "days_since_latest": 5,
  "comments_n": 0.0,
  "comments_like_mean": 0.0,
  "comment_len_median": 0.0,
  "channel_title": "Robert Welsh",
  "degree_centrality": 0.1924686192468619,
  "betweenness_centrality": 0.0127445932551803,
  "eigenvector_centrality": 1.0,
  "sna_score_raw": 0.3978478060582258,
  "sna_score": 1.0,
  "community_id_raw": 0,
  "community_size": 82,
  "community_id": 0,
  "graph_degree": 46,
  "is_isolated": false,
  "ml_potential_score": 0.2980662742725503,
  "tfidf_similarity_raw": 0.0765979149092766,
  "keyword_boost": 0.08,
  "tfidf_similarity": 0.3112602038855218,
  "semantic_score": 0.0968382421611037,
  "tone_match_score": 0.2,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.10, tone match=0.20, must-keyword hits=1, exclusion hits=0.",
  "engagement_score": 0.3050693261320708,
  "scale_score": 0.6480291116588985,
  "activity_score": 0.9522008800151638,
  "interaction_score": 0.6759800316522849,
  "evidence_score": 0.7434732801647861,
  "credibility_multiplier": 0.833257632107111,
  "eligible_recommendation": true,
  "final_score_base": 0.4723448034483355,
  "final_score": 0.3935849124594588,
  "channel_profile_text": "If your foundation separates or just comes away from your face throughout the day, this could help!! This is how you make your foundation last longer and, in turn, help other products last longer too. *LET’S STAY CONNECTED!* Subscribe to my new Beauty Blog \"Brushed Up\" - https://robertwelsh.substack.com/?r=4nf54q&utm_medium=ios&utm_source=profile Instagram - @RobertWLSH Twitter - @RWLSHmakeup Tik…",
  "channel_keyword_summary": "robert welsh, robert welsh mua, robert welsh makeup, kbeauty, tirtir, fwee, foundation, everyday makeup tutorial, drugstore makeup, viral makeup",
  "recent_video_titles": "[\"2026-02-24 | Foundation Blending Mistake You're Making Right Now! #FOUNDATION #makeup #skincare (30,539 views)\", '2026-02-23 | Same Product… Higher Price?! Testing Viral Beauty Dupes! (35,768 views)', '2026-02-22 | Beauty Brands I’ll NEVER Support Again (After These Scandals!!) (92,209 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=SIna06hx7OI', 'https://www.youtube.com/watch?v=uUzHdjDANfQ', 'https://www.youtube.com/watch?v=9oyn1T-xmik']",
  "best_video_title": "PAINFUL lip plumper!! But is it worth it? #lipplumper #lipgloss",
  "best_video_views": 93964,
  "best_video_url": "https://www.youtube.com/watch?v=NHuwDL5eEYI",
  "recent_comments": "[]",
  "top_liked_comment": NaN,
  "comment_samples_n": 0.0,
  "est_subscribers": 0.0,
  "est_video_count": 0.0,
  "image_url": "https://i.ytimg.com/vi/NHuwDL5eEYI/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UC2GUcyD6KYjmU_ofQtPTSSA",
  "video_url": "https://www.youtube.com/watch?v=NHuwDL5eEYI",
  "display_score": 0.3935849124594588
}
```

### #2 Tati
```json
{
  "_channel_id": "UC4qk9TtGhBKCkoWz5qGJcGg",
  "n_videos": 24,
  "median_views": 122059.0,
  "median_likes": 5625.0,
  "median_comments": 334.0,
  "mean_engagement": 0.056249637457009,
  "latest_publish": "2026-02-23 16:29:06+00:00",
  "representative_video_id": "HzLKfHJpy1k",
  "video_title": "Best Drugstore Makeup of 2025 ...",
  "tags_text": "youtube beauty makeup tutorial review tati westbrook glamlifeguru how to drugstore luxury favorites best new makeup cosmetics foundation concealer highlight bronzer powder primer eyeshadow palette eyeliner lipstick skincare tips lips eyes mascara sephora best drugstrore makeup of 2025 l’oréal paris essence carlsan catrice nyx covergirl laka beauty creations honest beauty medicube cetaphil naturium pixi pure instinct",
  "video_description": "*click ... More to expand for Products and Links*\n💕 xo's Tati \n\n\n🦋 *▸ ENTER MY GIVEAWAYS & JOIN THE TATI LIST:* \n https://www.TheTatiList.com  \n\n\n📌 *▸DETAILS By TATI - LUXURY MAKEUP BRUSHES* \nhttps://detailsbytati.com\n\n\n*▸ VIDEO MENTIONED:*\nWorst Drugstore Makeup of 2025\nhttps://youtu.be/uK5rvi-zQEc\n\n\n*▸ PRODUCTS MENTIONED* \nL’Oréal Paris Infallible Blur-Fection Longwear Loose Setting Powder\nhttps://go.shopmy.us/p-36575571\n\nEssence Flawless Skin Trio Loose Setting Powder\nhttps://go.shopmy.us/p-36575989\n\nCarlsan Waterproof Setting Powder\nhttps://bit.ly/491UDsA\n\nCatrice Magic Shaper Face Cream Palette\nhttps://go.shopmy.us/p-36576073\n\nCatrice Blur Balm Blush Palette\nhttps://go.shopmy.us/p-36576149\n\nEssence Foundation Stick\nhttps://go.shopmy.us/p-36576398\n\nL’Oréal Paris Colour Riche Intense Volume Matte Lipstick // Worth It 601, Rebellious 108\nhttps://go.shopmy.us/p-36576561\n\nNYX Retractable Vivid Rich Mechanical \nEyeliner Pencil // Under the Moonstone\nhttps://go.shopmy.us/p-36576624\n\nessence Blend & Line Eyeshadow Stick // Full of Beans\nhttps://amzn.to/4p8u23j\n\nCoverGirl Perfect Point Plus Lashline Micro Eye Pencil // Bright-Eyed Beige\nhttps://amzn.to/4jnQggs\n\nLaka Monochrome Single Glitter Eyeshadow // Allure\nhttps://amzn.to/4axTMm3\n\nBeauty Creations Riding Solo Single Shadow // Howdy\nhttps://amzn.to/4s5RIrA\n\nHonest Beauty Makeup Remover Wipes\nhttps://amzn.to/4b8xqHV\n\nmedicube Collagen Night Wrapping Mask\nhttps://amzn.to/3YMpuVi\n\nCetaphil Nourishing Oil to Foam Cleanser\nhttps://amzn.to/4p8w8Qr\n\nNaturium Retinaldehyde Cream Serum 0.10%\nhttps://amzn.to/4sbSL9o\n\nL’Oreal Glossing 5-Min Lamination Hair Mask\nhttps://amzn.to/4pWTZE9\n\nCatrice Drunk’n Diamonds Glitter Eyeshadow\nhttps://go.shopmy.us/p-36576197\n\nL’Oréal Paris Infallible 3-Second Setting Mist\nhttps://go.shopmy.us/p-36577192\n\nL’Oréal Paris Infallible Brow Lamination\nhttps://go.shopmy.us/p-36577329\n\nPixiPerfume Eau de Parfum // PixiMimosa\nhttps://bit.ly/4oMRFz5\n\nPure Instinct Pheromone Perfume Oil // Original, Lucky\nhttps://amzn.to/4bdLsb8\n\n\n*▸ LET’S CONNECT*\n_Instagram_  glamlifeguru\n_TikTok_  TatiWestbrook\n_Snapchat_  TatiWestbrook\n_Twitter_  glamlifeguru \n_Email_  Tati@GlamLifeGuru.com\n\n\n*▸﻿ New PR Mailing Address*\nTATI, Inc.\n2300 W. 7th St\nSuite 108, Box 211\nFort Worth, TX  76107\n\n\nFTC DISCLAIMER:  This video is Not Sponsored, however I sometimes provide affiliate links where I earn a small commission with purchase.  Thank you for your support.\n\n\nAll Rights Reserved © 2025, Tati Westbrook \n\n\n\n\n\n\n\n\n\n\n\nHi I'm Tati Westbrook, thank you for watching, please be sure to check out my collection of new makeup review videos where you'll find my best beauty tips, tricks and favorites on everything from top luxury cosmetics to my favorite drugstore makeup. Whether you're looking for a new product review, tutorials, beauty tips, haul or perhaps even a giveaway, I hope you enjoy watching.",
  "all_tags": "['youtube', 'beauty', 'makeup', 'tutorial', 'review', 'tati', 'westbrook', 'glamlifeguru', 'how to', 'drugstore', 'luxury', 'favorites', 'best', 'new makeup', 'cosmetics', 'foundation', 'concealer', 'highlight', 'bronzer', 'powder', 'primer', 'eyeshadow', 'palette', 'eyeliner', 'lipstick', 'skincare', 'tips', 'lips', 'eyes', 'mascara', 'sephora', 'color theory', 'color blocking', 'color analysis', 'youtube', 'beauty', 'makeup', 'tutorial', 'review', 'tati', 'westbrook', 'glamlifeguru', 'how to', 'drugstore', 'luxury', 'favorites', 'best', 'new makeup', 'cosmetics', 'foundation', 'concealer', 'highlight', 'bronzer', 'powder', 'primer', 'eyeshadow', 'palette', 'eyeliner', 'lipstick', 'skincare', 'tips', 'lips', 'eyes', 'mascara', 'sephora', 'save your cash', 'product fails', 'do not buy these products', 'neutrogena', 'caliray', 'benefit', 'el blanc', 'palladio', 'tarte', 'e.l.f.', 'fenty beauty', 'juvia’s place', 'covergirl', 'l’oréal paris', 'unleashia']",
  "channel_text": "best drugstore makeup of 2025 ... *click ... more to expand for products and links* 💕 xo's tati 🦋 *▸ enter my giveaways & join the tati list:* https://www.thetatilist.com 📌 *▸details by tati - luxury makeup brushes* https://detailsbytati.com *▸ video mentioned:* worst drugstore makeup of 2025 https://youtu.be/uk5rvi-zqec *▸ products mentioned* l’oréal paris infallible blur-fection longwear loose setting powder https://go.shopmy.us/p-36575571 essence flawless skin trio loose setting powder https://go.shopmy.us/p-36575989 carlsan waterproof setting powder https://bit.ly/491udsa catrice magic shaper face cream palette https://go.shopmy.us/p-36576073 catrice blur balm blush palette https://go.shopmy.us/p-36576149 essence foundation stick https://go.shopmy.us/p-36576398 l’oréal paris colour riche intense volume matte lipstick // worth it 601, rebellious 108 https://go.shopmy.us/p-36576561 nyx retractable vivid rich mechanical eyeliner pencil // under the moonstone https://go.shopmy.us/p-36576624 essence blend & line eyeshadow stick // full of beans https://amzn.to/4p8u23j covergirl perfect point plus lashline micro eye pencil // bright-eyed beige https://amzn.to/4jnqggs laka monochrome single glitter eyeshadow // allure https://amzn.to/4axtmm3 beauty creations riding solo single shadow // howdy https://amzn.to/4s5rira honest beauty makeup remover wipes https://amzn.to/4b8xqhv medicube collagen night wrapping mask https://amzn.to/3ympuvi cetaphil nourishing oil to foam cleanser https://amzn.to/4p8w8qr naturium retinaldehyde cream serum 0.10% https://amzn.to/4sbsl9o l’oreal glossing 5-min lamination hair mask https://amzn.to/4pwtze9 catrice drunk’n diamonds glitter eyeshadow https://go.shopmy.us/p-36576197 l’oréal paris infallible 3-second setting mist https://go.shopmy.us/p-36577192 l’oréal paris infallible brow lamination https://go.shopmy.us/p-36577329 pixiperfume eau de parfum // piximimosa https://bit.ly/4omrfz5 pure instinct pheromone perfume oil // original, lucky https://amzn.to/4bdlsb8 *▸ let’s connect* _instagram_ glamlifeguru _tiktok_ tatiwestbrook _snapchat_ tatiwestbrook _twitter_ glamlifeguru _email_ tati@glamlifeguru.com *▸﻿ new pr mailing address* tati, inc. 2300 w. 7th st suite 108, box 211 fort worth, tx 76107 ftc disclaimer: this video is not sponsored, however i sometimes provide affiliate links where i earn a small commission with purchase. thank you for your support. all rights reserved © 2025, tati westbrook hi i'm tati westbrook, thank you for watching, please be sure to check out my collection of new makeup review videos where you'll find my best beauty tips, tricks and favorites on everything from top luxury cosmetics to my favorite drugstore makeup. whether you're looking for a new product review, tutorials, beauty tips, haul or perhaps even a giveaway, i hope you enjoy watching. youtube beauty makeup tutorial review tati westbrook glamlifeguru how to drugstore luxury favorites best new makeup cosmetics foundation concealer highlight bronzer powder primer eyeshadow palette eyeliner lipstick skincare tips lips eyes mascara sephora color theory color blocking color analysis youtube beauty makeup tutorial review tati westbrook glamlifeguru how to drugstore luxury favorites best new makeup cosmetics foundation concealer highlight bronzer powder primer eyeshadow palette eyeliner lipstick skincare tips lips eyes mascara sephora save your cash product fails do not buy these products neutrogena caliray benefit el blanc palladio tarte e.l.f. fenty beauty juvia’s place covergirl l’oréal paris unleashia",
  "days_since_latest": 6,
  "comments_n": 20.0,
  "comments_like_mean": 2010.7,
  "comment_len_median": 99.0,
  "channel_title": "Tati",
  "degree_centrality": 0.1841004184100418,
  "betweenness_centrality": 0.0135211149428176,
  "eigenvector_centrality": 0.9703703703703704,
  "sna_score_raw": 0.385572539378094,
  "sna_score": 0.96914582286691,
  "community_id_raw": 0,
  "community_size": 82,
  "community_id": 0,
  "graph_degree": 44,
  "is_isolated": false,
  "ml_potential_score": 0.1619177812119589,
  "tfidf_similarity_raw": 0.0354527839477858,
  "keyword_boost": 0.0,
  "tfidf_similarity": 0.0704673543468967,
  "semantic_score": 0.0303537127819009,
  "tone_match_score": 0.2,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.03, tone match=0.20, must-keyword hits=0, exclusion hits=0.",
  "engagement_score": 0.1910233285730395,
  "scale_score": 0.7299117979484528,
  "activity_score": 0.9847089717232868,
  "interaction_score": 0.7138638305087853,
  "evidence_score": 0.803943754964953,
  "credibility_multiplier": 0.8725634407272195,
  "eligible_recommendation": true,
  "final_score_base": 0.3742355520538893,
  "final_score": 0.3265442609425921,
  "channel_profile_text": "Everyone give a big thanks to Rebecca for coming on my channel! IG: https://www.instagram.com/Colorpolitan Website: https://colorpolitan.com *▸ Follow me on ShopMy to see all of my current favorites* https://shopmy.us/Tati 📌 *▸ PRODUCTS MENTIONED / MAKEUP WORN:* DETAILS By TATI - MAKEUP BRUSHES* https://detailsbytati.com *▸ LET’S CONNECT* _Instagram_ glamlifeguru _TikTok_ TatiWestbrook _Snapchat_…",
  "channel_keyword_summary": "youtube, beauty, makeup, tutorial, review, tati, westbrook, how to, luxury, favorites",
  "recent_video_titles": "['2026-02-23 | I DID COLOR ANALYSIS … Everyone was wrong! (200,951 views)', \"2026-02-20 | Don't Buy These Products ... Save your Cash! (98,730 views)\", '2026-02-16 | 12 DRUGSTORE MAKEUP DUPES ... Save Your Cash! (155,357 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=fYz05BZO63U', 'https://www.youtube.com/watch?v=YbNNSepuois', 'https://www.youtube.com/watch?v=d0JN3POODAs']",
  "best_video_title": "Best Drugstore Makeup of 2025 ...",
  "best_video_views": 232126,
  "best_video_url": "https://www.youtube.com/watch?v=HzLKfHJpy1k",
  "recent_comments": "['2026-01-14 | @gtfoangell: came back to watch this after jlo looked crazy at the golden globe LOL', '2023-03-06 | @remingtonfriel: tati you look like a literal supermodel in this video! decided to rewatch this years later and gosh i’m living for this glowy fantasy !', '2022-09-06 | @lgannawa: This is and will forever be one of my favorite makeup “tutorials”. Between the solid beauty tips, the content is wonderful. Playful, fun, and gorgeous!!! Just …']",
  "top_liked_comment": "@smittywerbenjagermanjensen6278: petition for Scott to start youtube cause we need more of him pleaseeeee (likes 23626)",
  "comment_samples_n": 20.0,
  "est_subscribers": 0.0,
  "est_video_count": 0.0,
  "image_url": "https://i.ytimg.com/vi/HzLKfHJpy1k/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UC4qk9TtGhBKCkoWz5qGJcGg",
  "video_url": "https://www.youtube.com/watch?v=HzLKfHJpy1k",
  "display_score": 0.3265442609425921
}
```

### #3 Beauty Within
```json
{
  "_channel_id": "UC8f2CDyLibpGYSN3O2LfDwg",
  "n_videos": 22,
  "median_views": 32834.0,
  "median_likes": 1236.5,
  "median_comments": 57.0,
  "mean_engagement": 0.0355760092511774,
  "latest_publish": "2026-02-22 15:00:07+00:00",
  "representative_video_id": "U5lH23oLIc8",
  "video_title": "Korean body care SECRET I learned for the SMOOTHEST skin 🤭 *rub rub rub*",
  "tags_text": "beauty within skincare oily skin dry skin affordable skin care routine skin care wellness skincare routine skin types skincare routine beauty tips step by step skincare products skincare trends sephora sale skincare dupes beginner skincare routine skincare routines for acne anti aging routine anti aging skincare glowing skin skincare tips",
  "video_description": "🧤Thank you SKIMS for sponsoring today's video! Shop my favorite bras and underwear styles at https://skims.yt.link/LMVDBbr #skimspartner. Today I'm sharing the ONE secret to getting the softest, glowing skin after learning what the girlies do in Korea. Bath culture is huge all over Asia, and we're missing out! I experienced a Korean body scrub for the first time when I visited earlier in the year and was shocked at the results after being completely scrubbed away by an ahjumma (korean grandma 👵🏼). The amount of dead skin, good lord I hope nobody ever has to witness that. Good bye, acne, texture, keratosis pilaris, dry & dull skin! Let me know your thoughts and if you've ever tried it out, and share your bath/showering secrets with meeee! - fel x \n\n💖 Visit our BW Skincare Shop (full of our personal faves!):  https://bwth.in/shop \n💖 Sign up for our newsletter to get weekly updates & inspiration: https://bwth.in/newsletter \n💖 Check out our Shop My and Amazon Storefront for skincare, hair, beauty faves + other handy essentials: https://shopmy.us/public/beautywithin + https://amzn.to/2wrRzHG \n\nTimestamps \n00:00 What's the secret to soft, milky, glowing skin?\n00:42 let's strip it down & talk about bras 🤭\n3:36 time to steam 🧖🏼‍♀️\n5:18 what are the Korean italy towels? which one suits your skin? 🧤\n6:32 scrub it all off 👀\n8:57 wash, cleanse & shave\n9:25 when to exfoliate, moisturize & nourish 🧴\n\n- P R O D U C T   M E N T I O N S -\n\nSee our full collection on Shop My Shelf: https://shopmy.us/collections/2682053\n\nSkims Bras:\n👙 Fits everybody Scoop Bralette (Color: sienna, size: S *note: you can also size up because they're super stretchy and SKIMS sizes can run smaller*)\n👙 Fits Everybody Unlined Demi Bra (Color: ochre, size: 34C *note: unlined means there's no padding in the cup so it's much thinner*)\n👙 Fits Everybody Strapless Bra (Color: onyx, size: 34C)\n\n🧤Resorè | Face Wash Cloth: https://go.shopmy.us/p-28704611\n🧤Tatuo | Korean Exfoliating Mitt (3 Pieces): https://go.shopmy.us/p-28704774\n🧤AVIALAN | Exfoliating Glove (for Sensitive Skin): https://go.shopmy.us/p-28704971\n🧤Tatuo | Korean Exfoliating Mitt (8 Pieces): https://go.shopmy.us/p-28705160\n🧤VT COSMETICS | 7% Glycolic Acid Reedle Shot Head-to-Toe Mist: https://go.shopmy.us/p-28705261\n🧤Saltair | Santal Bloom Nourishing Body Oil: https://go.shopmy.us/p-28705356\n🧤Kaimu Bench | Waterproof Shower Bench: https://go.shopmy.us/p-28705549\n🧤L'OCCITANE | Almond Milk Concentrate Lotion: https://go.shopmy.us/p-28705609\n\nNeed more codes? Check out our full list of exclusive discounts: https://shopmy.us/public/beautywithin/discount-codes \n\nDon't be a stranger 👻 :\nBW Instagram: https://bwth.in/ig\nFelicia's IG:https://bwth.in/FeliciaLeeInstagram \nRowena's IG: https://bwth.in/RowenaTsaiInstagram \n\nFor a full list of our recommended products: https://amzn.to/2wrRzHG\n_________________\n\nBeauty Within explores the world of skincare, beauty and wellness. \n\nFor business inquiries: collab@beautywithin.com \n----------------------------\n© All Rights Reserved.",
  "all_tags": "['beauty within', 'skincare', 'oily skin', 'dry skin', 'affordable', 'skin care routine', 'skin care', 'wellness', 'skincare routine', 'skin types', 'skincare routine', 'beauty tips', 'step by step', 'skincare products', 'skincare trends', 'sephora sale', 'skincare dupes', 'beginner skincare routine', 'skincare routines for acne', 'anti aging routine', 'anti aging skincare', 'glowing skin', 'skincare tips', 'beauty within', 'wellness', 'skin types', 'skincare trends', 'glowing skin', 'tcm', 'chinese', 'chinese trend', 'beauty within', 'skincare', 'oily skin', 'dry skin', 'affordable', 'skin care routine', 'skin care', 'wellness', 'skincare routine', 'skin types', 'skincare routine', 'beauty tips', 'step by step', 'skincare products', 'skincare trends', 'sephora sale', 'skincare dupes', 'beginner skincare routine', 'skincare routines for acne', 'anti aging routine', 'anti aging skincare', 'glowing skin', 'skincare tips', 'beauty within', 'chicken soup', 'nourishing soup', 'period soup', 'period food', 'period health', 'female health', 'cycle syncing', 'period drinks', 'tcm soup', 'chinese herbal soup', 'beauty within', 'skincare', 'oily skin', 'dry skin', 'affordable', 'skin care routine', 'skin care', 'wellness', 'skincare routine', 'skin types', 'skincare routine', 'beauty tips', 'step by step', 'skincare products', 'skincare trends']",
  "channel_text": "korean body care secret i learned for the smoothest skin 🤭 *rub rub rub* 🧤thank you skims for sponsoring today's video! shop my favorite bras and underwear styles at https://skims.yt.link/lmvdbbr #skimspartner. today i'm sharing the one secret to getting the softest, glowing skin after learning what the girlies do in korea. bath culture is huge all over asia, and we're missing out! i experienced a korean body scrub for the first time when i visited earlier in the year and was shocked at the results after being completely scrubbed away by an ahjumma (korean grandma 👵🏼). the amount of dead skin, good lord i hope nobody ever has to witness that. good bye, acne, texture, keratosis pilaris, dry & dull skin! let me know your thoughts and if you've ever tried it out, and share your bath/showering secrets with meeee! - fel x 💖 visit our bw skincare shop (full of our personal faves!): https://bwth.in/shop 💖 sign up for our newsletter to get weekly updates & inspiration: https://bwth.in/newsletter 💖 check out our shop my and amazon storefront for skincare, hair, beauty faves + other handy essentials: https://shopmy.us/public/beautywithin + https://amzn.to/2wrrzhg timestamps 00:00 what's the secret to soft, milky, glowing skin? 00:42 let's strip it down & talk about bras 🤭 3:36 time to steam 🧖🏼‍♀️ 5:18 what are the korean italy towels? which one suits your skin? 🧤 6:32 scrub it all off 👀 8:57 wash, cleanse & shave 9:25 when to exfoliate, moisturize & nourish 🧴 - p r o d u c t m e n t i o n s - see our full collection on shop my shelf: https://shopmy.us/collections/2682053 skims bras: 👙 fits everybody scoop bralette (color: sienna, size: s *note: you can also size up because they're super stretchy and skims sizes can run smaller*) 👙 fits everybody unlined demi bra (color: ochre, size: 34c *note: unlined means there's no padding in the cup so it's much thinner*) 👙 fits everybody strapless bra (color: onyx, size: 34c) 🧤resorè | face wash cloth: https://go.shopmy.us/p-28704611 🧤tatuo | korean exfoliating mitt (3 pieces): https://go.shopmy.us/p-28704774 🧤avialan | exfoliating glove (for sensitive skin): https://go.shopmy.us/p-28704971 🧤tatuo | korean exfoliating mitt (8 pieces): https://go.shopmy.us/p-28705160 🧤vt cosmetics | 7% glycolic acid reedle shot head-to-toe mist: https://go.shopmy.us/p-28705261 🧤saltair | santal bloom nourishing body oil: https://go.shopmy.us/p-28705356 🧤kaimu bench | waterproof shower bench: https://go.shopmy.us/p-28705549 🧤l'occitane | almond milk concentrate lotion: https://go.shopmy.us/p-28705609 need more codes? check out our full list of exclusive discounts: https://shopmy.us/public/beautywithin/discount-codes don't be a stranger 👻 : bw instagram: https://bwth.in/ig felicia's ig:https://bwth.in/felicialeeinstagram rowena's ig: https://bwth.in/rowenatsaiinstagram for a full list of our recommended products: https://amzn.to/2wrrzhg _________________ beauty within explores the world of skincare, beauty and wellness. for business inquiries: collab@beautywithin.com ---------------------------- © all rights reserved. beauty within skincare oily skin dry skin affordable skin care routine skin care wellness skincare routine skin types skincare routine beauty tips step by step skincare products skincare trends sephora sale skincare dupes beginner skincare routine skincare routines for acne anti aging routine anti aging skincare glowing skin skincare tips beauty within wellness skin types skincare trends glowing skin tcm chinese chinese trend beauty within skincare oily skin dry skin affordable skin care routine skin care wellness skincare routine skin types skincare routine beauty tips step by step skincare products skincare trends sephora sale skincare dupes beginner skincare routine skincare routines for acne anti aging routine anti aging skincare glowing skin skincare tips beauty within chicken soup nourishing soup period soup period food period health female health cycle syncing period drinks tcm soup chinese herbal soup beauty within skincare oily skin dry skin affordable skin care routine skin care wellness skincare routine skin types skincare routine beauty tips step by step skincare products skincare trends",
  "days_since_latest": 7,
  "comments_n": 0.0,
  "comments_like_mean": 0.0,
  "comment_len_median": 0.0,
  "channel_title": "Beauty Within",
  "degree_centrality": 0.1171548117154811,
  "betweenness_centrality": 0.0066512792220156,
  "eigenvector_centrality": 0.6222222222222222,
  "sna_score_raw": 0.2462558561349274,
  "sna_score": 0.6189699990425168,
  "community_id_raw": 1,
  "community_size": 40,
  "community_id": 1,
  "graph_degree": 28,
  "is_isolated": false,
  "ml_potential_score": 0.1185419450475427,
  "tfidf_similarity_raw": 0.2005126363172104,
  "keyword_boost": 0.08,
  "tfidf_similarity": 0.557558000840201,
  "semantic_score": 0.1873028569188779,
  "tone_match_score": 0.4,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.19, tone match=0.40, must-keyword hits=1, exclusion hits=0.",
  "engagement_score": 0.1177451318515395,
  "scale_score": 0.6350485658922105,
  "activity_score": 0.9522008800151638,
  "interaction_score": 0.5884694509718877,
  "evidence_score": 0.7232073928910481,
  "credibility_multiplier": 0.8200848053791812,
  "eligible_recommendation": true,
  "final_score_base": 0.3948139927011121,
  "final_score": 0.323780956365269,
  "channel_profile_text": "We’re getting real, intimate, and talking about something that honestly doesn’t get discussed enough on this platform — feminine hygiene. Check out Pair Eyewear here https://paireyewear.yt.link/lBidjUZ and use code \"BEAUTYWITHINGIFT15\"for a free gift with purchase! Thank you Pair for sponsoring a portion of this video! So I know this topic can feel a little awkward or taboo, but taking care of ou…",
  "channel_keyword_summary": "skincare routine, beauty within, skincare, oily skin, glowing skin, dry skin, skin care routine, skin care, wellness, skin types",
  "recent_video_titles": "['2026-02-22 | My PERIOD + feminine HYGIENE routine 👀 *secrets nobody tells you* (30,439 views)', '2026-02-11 | You met me at a very chinese time (17,233 views)', '2026-02-07 | My ULTIMATE healing soup 🍲 *drink this everyday* (20,589 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=Sf8gIFy3pEU', 'https://www.youtube.com/watch?v=DUx-TmajQY0', 'https://www.youtube.com/watch?v=V1iZTDfreiY']",
  "best_video_title": "Korean body care SECRET I learned for the SMOOTHEST skin 🤭 *rub rub rub*",
  "best_video_views": 229655,
  "best_video_url": "https://www.youtube.com/watch?v=U5lH23oLIc8",
  "recent_comments": "[]",
  "top_liked_comment": NaN,
  "comment_samples_n": 0.0,
  "est_subscribers": 0.0,
  "est_video_count": 0.0,
  "image_url": "https://i.ytimg.com/vi/U5lH23oLIc8/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UC8f2CDyLibpGYSN3O2LfDwg",
  "video_url": "https://www.youtube.com/watch?v=U5lH23oLIc8",
  "display_score": 0.323780956365269
}
```

### #4 STEPHANIE TOMS
```json
{
  "_channel_id": "UCeOYFSJpQT27y3V6faZNC2g",
  "n_videos": 17,
  "median_views": 17045.0,
  "median_likes": 1222.0,
  "median_comments": 133.0,
  "mean_engagement": 0.0687614291599051,
  "latest_publish": "2026-02-17 20:00:07+00:00",
  "representative_video_id": "nt1glaQqoEk",
  "video_title": "I SMELL A LAWSUIT! Testing NEW Primark Makeup!",
  "tags_text": "testing new primark makeup primark review affordable makeup cheap makeup viral makeup dupes tiktok makeup dupes viral makeup primark dupes steph toms steph toms boyfriend",
  "video_description": "Shop haruharu wonder Black Rice Moisture Airyfit Daily Sunscreen SPF 50+ / PA++++\nhttps://bit.ly/4kcY4Av \n(33% on Amazon Prime Day!)\n\n----------------------------------------------------------------------------------------------------------------- \n\nPRODUCTS USED: \n(All in store, but will try and link online!)\n\n-----------------------------------------------------------------------------------------------------------------\n\nFOLLOW ME:\nInstagram:   http://instagram.com/itsstephtoms\nTiktok: @itsstephtoms\nTwitter / X http://twitter.com/itsstephtoms\n\nBUSINESS EMAIL: stephtoms@mcsaatchisocial.com\n\n-----------------------------------------------------------------------------------------------------------------\n\nDISCOUNT CODES:\nCult Beauty (Use 'STEPHXCB' for up to 20% off) https://slooks.top/kfKo7lT/64\nMy contacts (Use 'STEPHTOMS' for 10% off) www.solotica.com\nDermatica (Use 'STEPH' for ££ off) https://dermati.ca/74e522\n\n-----------------------------------------------------------------------------------------------------------------\n\n\n#makeupwithspf #glassskin #spf #haruharuSuncream",
  "all_tags": "['testing new makeup', 'full face of first impressions', 'how to', 'new makeup', 'viral makeup', 'drugstore makeup', 'viral tiktok', 'hopescope childhood products', 'discontinued childhood products', 'zoella', 'tanyaburr', 'collection 2000', '2000 makeup', 'testing drugstore makeup', 'drugstore makeup dupes', 'best and worst drugstore makeup', 'uk beauty blogger', 'zoe sugg', 'drugstore makeup haul', 'honest makeup review', 'full face of expired makeup', 'mouldy makeup', 'cheap makeup', 'makeup routine', 'emo', 'emo makeup', 'makeup', 'kbeauty', 'korean makeup', 'blusher', 'valentine’s day', 'valentine', 'asmr', 'review', '2016 makeup', '2016 vs 2026', '2016 vs 2026 makeup', '2016 makeup tutorial', 'james charles', 'tati westbrook', 'jeffree star', 'manny mua', 'laura lee', 'nikkietutorials', 'jaclyn hill', 'beauty gurus', '2016 makeup trends', 'makeup challenge', 'hot or not', 'uk beauty guru', 'the power of makeup', 'makeup tutorial', 'champagne pop', 'contouring tutorial', 'kylie cosmetics', 'kylie jenner', 'too faced', 'huda beauty', 'makeup challenge tiktok', 'tiktok trends', '2016 makeup compilation', 'tiktok makeup', 'steph toms', 'steph toms', 'ranking viral products', 'ranking tiktok viral products *brutally honest*', 'rating tiktok products', 'rating viral tiktok products', 'drugstore makeup', 'sacheu lip stain', 'makeup fail', 'best and worst', 'drugstore makeup dupes', 'sacheu lip stain pinked', 'black friday discount', 'kbeauty', 'k beauty', 'korean skincare', 'jaclyn hill', 'desi perkins']",
  "channel_text": "i smell a lawsuit! testing new primark makeup! shop haruharu wonder black rice moisture airyfit daily sunscreen spf 50+ / pa++++ https://bit.ly/4kcy4av (33% on amazon prime day!) ----------------------------------------------------------------------------------------------------------------- products used: (all in store, but will try and link online!) ----------------------------------------------------------------------------------------------------------------- follow me: instagram: http://instagram.com/itsstephtoms tiktok: @itsstephtoms twitter / x http://twitter.com/itsstephtoms business email: stephtoms@mcsaatchisocial.com ----------------------------------------------------------------------------------------------------------------- discount codes: cult beauty (use 'stephxcb' for up to 20% off) https://slooks.top/kfko7lt/64 my contacts (use 'stephtoms' for 10% off) www.solotica.com dermatica (use 'steph' for ££ off) https://dermati.ca/74e522 ----------------------------------------------------------------------------------------------------------------- #makeupwithspf #glassskin #spf #haruharusuncream testing new makeup full face of first impressions how to new makeup viral makeup drugstore makeup viral tiktok hopescope childhood products discontinued childhood products zoella tanyaburr collection 2000 2000 makeup testing drugstore makeup drugstore makeup dupes best and worst drugstore makeup uk beauty blogger zoe sugg drugstore makeup haul honest makeup review full face of expired makeup mouldy makeup cheap makeup makeup routine emo emo makeup makeup kbeauty korean makeup blusher valentine’s day valentine asmr review 2016 makeup 2016 vs 2026 2016 vs 2026 makeup 2016 makeup tutorial james charles tati westbrook jeffree star manny mua laura lee nikkietutorials jaclyn hill beauty gurus 2016 makeup trends makeup challenge hot or not uk beauty guru the power of makeup makeup tutorial champagne pop contouring tutorial kylie cosmetics kylie jenner too faced huda beauty makeup challenge tiktok tiktok trends 2016 makeup compilation tiktok makeup steph toms steph toms ranking viral products ranking tiktok viral products *brutally honest* rating tiktok products rating viral tiktok products drugstore makeup sacheu lip stain makeup fail best and worst drugstore makeup dupes sacheu lip stain pinked black friday discount kbeauty k beauty korean skincare jaclyn hill desi perkins",
  "days_since_latest": 12,
  "comments_n": 0.0,
  "comments_like_mean": 0.0,
  "comment_len_median": 0.0,
  "channel_title": "STEPHANIE TOMS",
  "degree_centrality": 0.1297071129707113,
  "betweenness_centrality": 0.0072833856276209,
  "eigenvector_centrality": 0.6222222222222222,
  "sna_score_raw": 0.2506130317270592,
  "sna_score": 0.6299218643683597,
  "community_id_raw": 0,
  "community_size": 82,
  "community_id": 0,
  "graph_degree": 31,
  "is_isolated": false,
  "ml_potential_score": 0.2383110298615412,
  "tfidf_similarity_raw": 0.0822273777260137,
  "keyword_boost": 0.16,
  "tfidf_similarity": 0.4814607079623895,
  "semantic_score": 0.1416381420049975,
  "tone_match_score": 0.4,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.14, tone match=0.40, must-keyword hits=2, exclusion hits=0.",
  "engagement_score": 0.2353716899063749,
  "scale_score": 0.5876840978354703,
  "activity_score": 0.8566346820627893,
  "interaction_score": 0.5922810715586916,
  "evidence_score": 0.6690588191621492,
  "credibility_multiplier": 0.784888232455397,
  "eligible_recommendation": true,
  "final_score_base": 0.4056512786758458,
  "final_score": 0.3183909151131563,
  "channel_profile_text": "Did someone say....NEW SERIES? You guys know I loveeeee trying out every makeup brand I can get my hands on, so I figured, why not start with the OG (!!!!!) Youtuber makeup brand...Collection! Or Collection 2000 if you're a 90s kid like me xoxox. Today I'm reviewing as many Collection makeup products as I can get my hands on...even the ones I probably shouldn't put on my face lol. Are any of you …",
  "channel_keyword_summary": "steph toms, steph toms boyfriend, best and worst, testing new makeup, full face of first impressions, viral makeup, james charles, makeup tutorial, affordable makeup, drugstore makeup",
  "recent_video_titles": "['2026-02-17 | I should NOT be using this 😂 Testing COLLECTION Makeup! (First Impressions) (14,615 views)', '2026-02-15 | testing heart shaped blusher 💘 #kbeauty #heart #blusher (8,492 views)', '2026-01-20 | I Tried 2016 vs 2026 Makeup! | STEPH TOMS (17,045 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=B9---fdsip8', 'https://www.youtube.com/watch?v=RoHpciJq6xU', 'https://www.youtube.com/watch?v=JN8z5JK35m8']",
  "best_video_title": "I SMELL A LAWSUIT! Testing NEW Primark Makeup!",
  "best_video_views": 47027,
  "best_video_url": "https://www.youtube.com/watch?v=nt1glaQqoEk",
  "recent_comments": "[]",
  "top_liked_comment": NaN,
  "comment_samples_n": 0.0,
  "est_subscribers": 0.0,
  "est_video_count": 0.0,
  "image_url": "https://i.ytimg.com/vi/nt1glaQqoEk/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UCeOYFSJpQT27y3V6faZNC2g",
  "video_url": "https://www.youtube.com/watch?v=nt1glaQqoEk",
  "display_score": 0.3183909151131563
}
```

### #5 MrsMelissaM
```json
{
  "_channel_id": "UC8gaiQHu6uEfWa87kZ0_FkQ",
  "n_videos": 25,
  "median_views": 4915.0,
  "median_likes": 742.0,
  "median_comments": 71.0,
  "mean_engagement": 0.1272841901263323,
  "latest_publish": "2026-02-24 20:46:44+00:00",
  "representative_video_id": "V6k4AT4C4m4",
  "video_title": "Drugstore Makeup That Rivals High End - Save SERIOUS Cash!!!",
  "tags_text": "mrs melissa m over 50 makeup makeup for older women stephanie marie makeup tutorials over 40 makeup risa does makeup cheap makeup dominique sachse makeup over 40 drugstore makeup best affordable makeup makeup over 50 pretty over fifty high end makeup dupes drugstore dupes for charlotte tilbury affordable makeup best drugstore makeup drugstore dupes hotandflashy",
  "video_description": "Tired of spending a fortune on high end and  luxury beauty products? In this video, I'm sharing the best-kept secrets at the drugstore that will make you say goodbye to those pricey high-end products! Affordable alternatives to luxury skincare staples & your favorite designer makeup, we're covering it all. Get ready to save some serious cash and upgrade your beauty routine without breaking the bank! Whether you're a beauty newbie or a seasoned pro, you won't want to miss these game-changing drugstore products. Come  discover the ultimate drugstore products that will make you look and feel like a million bucks!\n\nPrevious \"Buy This Not That\" videos\nhttps://youtu.be/JMYAVXs5H10\nhttps://youtu.be/3mIIkNGUH5s\n\n*My Amazon Storefront https://amzn.to/2AhOI3t \nWhen you shop on my Amazon page I get a small commission. Makeup listed below.\n\n*Products Mentioned:\n1- Murad Exfoliating Cleanser\nhttps://howl.link/8tw29m1fnksa5\nAlternative:\nhttps://howl.link/209lgiv218ny0\n\n2- Patrick Ta Major Dimensions III Palette\nhttps://howl.link/etdhmxrnf8zwl\nAlternative\nUlta: https://howl.link/w57kjupuhs3dz\nAmazon: https://amzn.to/49pfS9p\n\n3- Charlotte Tilbury Contour Wand in Fair/Medium\nhttps://howl.link/d1g544tx951w0\nAlternative in Summer Nights\nUlta: https://howl.link/5jm1xbb8iqb7i\nAmazon: https://amzn.to/49AiXSD\n\n4- Mac Extra Dimension Highlighter in Doublegleam\nhttps://howl.link/mu3bbcju5ozmr\nAlternative in Stardust\nhttps://amzn.to/49pgewL\n\n5- Charlotte Tilbury Flawless Filter in 2 light\nhttps://howl.link/8kxf3zocir88y\nAlternative in Light\nhttps://amzn.to/4qozYGL\n\n6- Persona Eyeliner in Brown\nUlta: https://howl.link/ch260o6twvo3p\nAmazon: https://amzn.to/4qmYBU1\nAlternative in Brown Denim\nUlta: https://howl.link/cq138eyneav4f\nAmazon: https://amzn.to/49Gb7Hk\n\n7- Hourglass Liquid Blush Drops in Whim\nhttps://howl.link/ovc371yecnh3t\nAlternative in Flex Symbol\nhttps://howl.link/cx56a902jt1gl\n\n8- Makeup By Mario Lipstick in Lucia\nhttps://howl.link/biihesvj0nx0m\nClinique Satin Lipstick in Plum Pop\nhttps://howl.link/7pw6ei9vunk67\nAlternative in Effortless\nhttps://amzn.to/4jK0R5w\n\n9- Charlotte Tilbury Lip Liner in Pillow Talk Fair\nhttps://howl.link/wday54puglnt0\nAlternative in Bubble Bath\nhttps://howl.link/zihgahexyji5x\n\nMy top https://amzn.to/4jK2d06\nEarrings https://amzn.to/4aXB6MH\nNails https://amzn.to/4sIdnGx\nFoundation in Classic Ivory\nhttps://amzn.to/4sH9UIt\nLip Gloss in pearly pink\nhttps://amzn.to/4qNhWO0\n\nContact or PR mmulder1026@gmail.com \nhttps://www.facebook.com/melissa.mulder.528 \nhttps://www.instagram.com/mrsmelissam1 \nhttps://tiktok.com/@UC8gaiQHu6uEfWa87kZ0_FkQ \n\n*Sign up for Rakuten & get $30 back after your first order. When you sign up I get a small commission. \nhttps://www.rakuten.com/r/MMULDE12?eeid=45830 \n\nHere's the website that lists skincare ingredients \nhttps://incidecoder.com/ \n\n*The items listed above are accompanied by affiliate links, meaning I earn a small commission if a purchase is made through my links. This has no impact on the cost to you, the consumer. I link to products this way whenever possible, and it has no bearing on the products I choose to review or recommend. Feel free to use, or not use, the links provided. And if you decide to use them, thank you so much! Also, if you would like to help a little more, when watching one of my videos please watch it all the way through, that helps to show the YT algorithm that people are interested in my video. If you have time, watch one or two of the ads shown with the video, that's the only way YouTubers get paid at all, if people watch the ads. So if you have a favorite Youtuber, now know how you can support them with these little tips. #makeupover50 #drugstoremakeup #beautyover40",
  "all_tags": "['skincare', 'skin care', 'prequel skincare review', 'prequel skincare', 'skincare routine', 'dermatologist', 'dermdoctor', 'skincare expert', 'dr samantha ellis', 'mature skin', 'mature women', 'over 50', 'over 40', 'over 60', 'over 70', 'mrs melissa m', 'pretty over 50', '50 and fabulous', 'fabulous 50s', 'skincare routines', 'eyebrow tutorial', 'eyebrow tutorial for beginners', 'makeup tutorial for beginners', 'makeup tutorial', 'makeup for beginners', 'mature skin makeup tutorial', 'apply eyebrow gel', 'apply brow gel', 'mrs melissa m', 'miss melissa m', 'michelle spieler', 'dna', 'skin care', 'skincare routine', 'skincare', 'photozyme', 'dna repair enzymes skincare', 'dna repair enzymes skin products', 'dna repair enzymes', 'skin care products', 'dna repair', 'skin barrier repair', 'skincare routine', 'glowing skin', 'dry skin', 'dry mature skin', 'mature skincare', 'dry skin care', 'amazon', 'amazon must haves', 'amazon fashion finds', 'best amazon finds', 'amazon deals', 'gadgets', 'amazon finds', 'amazon gadgets', 'amazon haul', 'best amazon products', 'amazon home finds', 'amazon finds for home', 'amazon tech finds', 'amazon products', 'amazon finds you need', 'mrs melissa m', 'makeup over 50', 'makeup over 40', 'makeup over 60', 'makeup over 70', 'shea whitney', 'brittany vasseur', 'drugstore makeup', 'affordable makeup', 'cheap makeup', 'drugstore forgotten gems', 'nyx butter gloss', 'elf wow brow', 'maybelline', 'nyx new york', 'essence makeup', 'falsies lash lift']",
  "channel_text": "drugstore makeup that rivals high end - save serious cash!!! tired of spending a fortune on high end and luxury beauty products? in this video, i'm sharing the best-kept secrets at the drugstore that will make you say goodbye to those pricey high-end products! affordable alternatives to luxury skincare staples & your favorite designer makeup, we're covering it all. get ready to save some serious cash and upgrade your beauty routine without breaking the bank! whether you're a beauty newbie or a seasoned pro, you won't want to miss these game-changing drugstore products. come discover the ultimate drugstore products that will make you look and feel like a million bucks! previous \"buy this not that\" videos https://youtu.be/jmyavxs5h10 https://youtu.be/3miiknguh5s *my amazon storefront https://amzn.to/2ahoi3t when you shop on my amazon page i get a small commission. makeup listed below. *products mentioned: 1- murad exfoliating cleanser https://howl.link/8tw29m1fnksa5 alternative: https://howl.link/209lgiv218ny0 2- patrick ta major dimensions iii palette https://howl.link/etdhmxrnf8zwl alternative ulta: https://howl.link/w57kjupuhs3dz amazon: https://amzn.to/49pfs9p 3- charlotte tilbury contour wand in fair/medium https://howl.link/d1g544tx951w0 alternative in summer nights ulta: https://howl.link/5jm1xbb8iqb7i amazon: https://amzn.to/49aixsd 4- mac extra dimension highlighter in doublegleam https://howl.link/mu3bbcju5ozmr alternative in stardust https://amzn.to/49pgewl 5- charlotte tilbury flawless filter in 2 light https://howl.link/8kxf3zocir88y alternative in light https://amzn.to/4qozygl 6- persona eyeliner in brown ulta: https://howl.link/ch260o6twvo3p amazon: https://amzn.to/4qmybu1 alternative in brown denim ulta: https://howl.link/cq138eyneav4f amazon: https://amzn.to/49gb7hk 7- hourglass liquid blush drops in whim https://howl.link/ovc371yecnh3t alternative in flex symbol https://howl.link/cx56a902jt1gl 8- makeup by mario lipstick in lucia https://howl.link/biihesvj0nx0m clinique satin lipstick in plum pop https://howl.link/7pw6ei9vunk67 alternative in effortless https://amzn.to/4jk0r5w 9- charlotte tilbury lip liner in pillow talk fair https://howl.link/wday54puglnt0 alternative in bubble bath https://howl.link/zihgahexyji5x my top https://amzn.to/4jk2d06 earrings https://amzn.to/4axb6mh nails https://amzn.to/4sidngx foundation in classic ivory https://amzn.to/4sh9uit lip gloss in pearly pink https://amzn.to/4qnhwo0 contact or pr mmulder1026@gmail.com https://www.facebook.com/melissa.mulder.528 https://www.instagram.com/mrsmelissam1 https://tiktok.com/@uc8gaiqhu6uefwa87kz0_fkq *sign up for rakuten & get $30 back after your first order. when you sign up i get a small commission. https://www.rakuten.com/r/mmulde12?eeid=45830 here's the website that lists skincare ingredients https://incidecoder.com/ *the items listed above are accompanied by affiliate links, meaning i earn a small commission if a purchase is made through my links. this has no impact on the cost to you, the consumer. i link to products this way whenever possible, and it has no bearing on the products i choose to review or recommend. feel free to use, or not use, the links provided. and if you decide to use them, thank you so much! also, if you would like to help a little more, when watching one of my videos please watch it all the way through, that helps to show the yt algorithm that people are interested in my video. if you have time, watch one or two of the ads shown with the video, that's the only way youtubers get paid at all, if people watch the ads. so if you have a favorite youtuber, now know how you can support them with these little tips. #makeupover50 #drugstoremakeup #beautyover40 skincare skin care prequel skincare review prequel skincare skincare routine dermatologist dermdoctor skincare expert dr samantha ellis mature skin mature women over 50 over 40 over 60 over 70 mrs melissa m pretty over 50 50 and fabulous fabulous 50s skincare routines eyebrow tutorial eyebrow tutorial for beginners makeup tutorial for beginners makeup tutorial makeup for beginners mature skin makeup tutorial apply eyebrow gel apply brow gel mrs melissa m miss melissa m michelle spieler dna skin care skincare routine skincare photozyme dna repair enzymes skincare dna repair enzymes skin products dna repair enzymes skin care products dna repair skin barrier repair skincare routine glowing skin dry skin dry mature skin mature skincare dry skin care amazon amazon must haves amazon fashion finds best amazon finds amazon deals gadgets amazon finds amazon gadgets amazon haul best amazon products amazon home finds amazon finds for home amazon tech finds amazon products amazon finds you need mrs melissa m makeup over 50 makeup over 40 makeup over 60 makeup over 70 shea whitney brittany vasseur drugstore makeup affordable makeup cheap makeup drugstore forgotten gems nyx butter gloss elf wow brow maybelline nyx new york essence makeup falsies lash lift",
  "days_since_latest": 5,
  "comments_n": 0.0,
  "comments_like_mean": 0.0,
  "comment_len_median": 0.0,
  "channel_title": "MrsMelissaM",
  "degree_centrality": 0.1297071129707113,
  "betweenness_centrality": 0.0076472485230063,
  "eigenvector_centrality": 0.7407407407407407,
  "sna_score_raw": 0.2898478562226013,
  "sna_score": 0.728539536498491,
  "community_id_raw": 1,
  "community_size": 40,
  "community_id": 1,
  "graph_degree": 31,
  "is_isolated": false,
  "ml_potential_score": 0.4468687999323744,
  "tfidf_similarity_raw": 0.0497695578405997,
  "keyword_boost": 0.0,
  "tfidf_similarity": 0.0989239398859944,
  "semantic_score": 0.0400121878812094,
  "tone_match_score": 0.4,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.04, tone match=0.40, must-keyword hits=0, exclusion hits=0.",
  "engagement_score": 0.4428070925404174,
  "scale_score": 0.4978491508902588,
  "activity_score": 1.0,
  "interaction_score": 0.5503719079214517,
  "evidence_score": 0.6563728191778602,
  "credibility_multiplier": 0.7766423324656091,
  "eligible_recommendation": true,
  "final_score_base": 0.3954564209832277,
  "final_score": 0.3071281971809158,
  "channel_profile_text": "Discover the truth about PREQUEL SKINCARE and its effectiveness for mature skin. In this video, we dive into the details of PREQUEL SKINCARE, exploring its ingredients, benefits, and results for older skin types. Whether you're looking to reduce fine lines, wrinkles, or protect your skin's barrier, or simply seeking a skincare routine that caters to your mature skin needs, this video is for you. …",
  "channel_keyword_summary": "mrs melissa m, drugstore makeup, makeup over 40, makeup over 50, best drugstore makeup, over 50, affordable makeup, skincare, skincare routine, pretty over 50",
  "recent_video_titles": "['2026-02-24 | PREQUEL SKINCARE for Mature Skin: Worth It or Waste? (2,561 views)', '2026-02-23 | Fake An EYEBROW LIFT With This Simple Eyebrow Trick (1,665 views)', '2026-02-23 | Photozyme DNA Repair Enzyme and Hyaluronic Acid (931 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=9k-utvAG8Vc', 'https://www.youtube.com/watch?v=qluOhBfEEBY', 'https://www.youtube.com/watch?v=UVu19709EJg']",
  "best_video_title": "Drugstore Makeup That Rivals High End - Save SERIOUS Cash!!!",
  "best_video_views": 22104,
  "best_video_url": "https://www.youtube.com/watch?v=V6k4AT4C4m4",
  "recent_comments": "[]",
  "top_liked_comment": NaN,
  "comment_samples_n": 0.0,
  "est_subscribers": 0.0,
  "est_video_count": 0.0,
  "image_url": "https://i.ytimg.com/vi/V6k4AT4C4m4/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UC8gaiQHu6uEfWa87kZ0_FkQ",
  "video_url": "https://www.youtube.com/watch?v=V6k4AT4C4m4",
  "display_score": 0.3071281971809158
}
```

### #6 Dr Alexis Stephens
```json
{
  "_channel_id": "UC2I480CzINvT-3cBAtsBySQ",
  "n_videos": 15,
  "median_views": 28608.0,
  "median_likes": 1007.0,
  "median_comments": 27.0,
  "mean_engagement": 0.0306693226903407,
  "latest_publish": "2025-11-03 02:44:48+00:00",
  "representative_video_id": "LTBr5gFBSlY",
  "video_title": "Dark Spot Game-Changer? Let’s Talk SkinBetter 👩🏾‍⚕️",
  "tags_text": "hyperpigmentation dark spots dark spots on face removal at home fade hyperpigmentation post inflammatory hyperpigmentation skincare melasma hyperpigmentation treatment hyperpigmentation black skin remedy for dark spots hyperpigmentation treatment for black skin skincare routine",
  "video_description": "Stubborn dark marks and uneven tone? As a dermatologist, I’m always looking for formulas backed by real science—and this one delivers. The NEW Even Intensive Skin Tone Correcting Serum from @skinbetter uses two b.r.y.t.e.r.™ biotechnology to improve the look of stubborn discoloration and reveal more luminous, even-looking skin. Exclusively on skinbetter.com or through an authorized provider. \n\n #skinbetterscience #dermatologisttips #darkspotsolution #skincaretok #evenbetter",
  "all_tags": "['melasma treatment', 'melasma', 'melasma black skin', 'melasma laser treatment', 'hyperpigmentation', 'melasma in skin of color', 'dermatologist', 'dermatology skin care', 'dermatologist skin care advice', 'dermatology', 'skin of color expert', 'skin of color skincare', 'dark spots', 'dark spot removal cream', 'dark spot reduction', 'dark spot cream', 'dark spot treatment', 'dark spot serum', 'dark spot removal', 'black dermatologist', 'black dermatologist skin care advice', 'best face wash', 'cleanser', 'skin care routine', 'skincare', 'skin care review', 'skincare routine', 'olay cleansing melts', 'skin care', 'olay', 'dermatology', 'sensitive skin', 'skin routine', 'dermatologist', 'shorts', 'face wash', 'glass skin', 'dry skin', 'hyperpigmentation', 'dark spots', 'dark spots on face removal at home', 'fade hyperpigmentation', 'post inflammatory hyperpigmentation', 'skincare', 'melasma', 'hyperpigmentation treatment', 'hyperpigmentation black skin', 'remedy for dark spots', 'hyperpigmentation treatment for black skin', 'skincare routine', 'skincare tips', 'neutrogena', 'neutrogena hydro boost water gel', 'glass skin', 'skincare products', 'korean skincare', 'neutrogena hydro boost review', 'neutrogena hydro boost', 'skin care products', 'hydro boost', 'skincare routine', 'hydro boost water gel', 'hyaluronic acid', 'skin care', 'skin care tips', 'razor bumps', \"barber's rash back of head\", 'akn', \"barber's rash\", 'acne keloidalis nuchae', 'akn removal', 'acne keloidalis nuchae surgery', 'keloids', 'pimples back of head', 'shaving bumps back of head', 'keloid', 'acne back of head', 'acne keloidalis nuchae treatment', 'keloids back of head', 'acne prone skin']",
  "channel_text": "dark spot game-changer? let’s talk skinbetter 👩🏾‍⚕️ stubborn dark marks and uneven tone? as a dermatologist, i’m always looking for formulas backed by real science—and this one delivers. the new even intensive skin tone correcting serum from @skinbetter uses two b.r.y.t.e.r.™ biotechnology to improve the look of stubborn discoloration and reveal more luminous, even-looking skin. exclusively on skinbetter.com or through an authorized provider. #skinbetterscience #dermatologisttips #darkspotsolution #skincaretok #evenbetter melasma treatment melasma melasma black skin melasma laser treatment hyperpigmentation melasma in skin of color dermatologist dermatology skin care dermatologist skin care advice dermatology skin of color expert skin of color skincare dark spots dark spot removal cream dark spot reduction dark spot cream dark spot treatment dark spot serum dark spot removal black dermatologist black dermatologist skin care advice best face wash cleanser skin care routine skincare skin care review skincare routine olay cleansing melts skin care olay dermatology sensitive skin skin routine dermatologist shorts face wash glass skin dry skin hyperpigmentation dark spots dark spots on face removal at home fade hyperpigmentation post inflammatory hyperpigmentation skincare melasma hyperpigmentation treatment hyperpigmentation black skin remedy for dark spots hyperpigmentation treatment for black skin skincare routine skincare tips neutrogena neutrogena hydro boost water gel glass skin skincare products korean skincare neutrogena hydro boost review neutrogena hydro boost skin care products hydro boost skincare routine hydro boost water gel hyaluronic acid skin care skin care tips razor bumps barber's rash back of head akn barber's rash acne keloidalis nuchae akn removal acne keloidalis nuchae surgery keloids pimples back of head shaving bumps back of head keloid acne back of head acne keloidalis nuchae treatment keloids back of head acne prone skin",
  "days_since_latest": 119,
  "comments_n": 0.0,
  "comments_like_mean": 0.0,
  "comment_len_median": 0.0,
  "channel_title": "Dr Alexis Stephens",
  "degree_centrality": 0.1129707112970711,
  "betweenness_centrality": 0.0079028659302463,
  "eigenvector_centrality": 0.6888888888888889,
  "sna_score_raw": 0.2673006424776505,
  "sna_score": 0.6718665741203826,
  "community_id_raw": 1,
  "community_size": 40,
  "community_id": 1,
  "graph_degree": 27,
  "is_isolated": false,
  "ml_potential_score": 0.1311753747506837,
  "tfidf_similarity_raw": 0.1599923487427877,
  "keyword_boost": 0.08,
  "tfidf_similarity": 0.4770182760346593,
  "semantic_score": 0.1641544268990056,
  "tone_match_score": 0.4,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.16, tone match=0.40, must-keyword hits=1, exclusion hits=0.",
  "engagement_score": 0.1003532575527501,
  "scale_score": 0.6250946595776744,
  "activity_score": 0.8107144632819592,
  "interaction_score": 0.5700970794437057,
  "evidence_score": 0.6725309636688646,
  "credibility_multiplier": 0.787145126384762,
  "eligible_recommendation": true,
  "final_score_base": 0.3897573175858784,
  "final_score": 0.306795573010522,
  "channel_profile_text": "Melasma can feel frustrating and impossible to treat but real results are possible with the right dermatologist-guided care. In this video, we share a real patient’s journey at Lex Dermatology & Aesthetics, where personalized melasma treatments helped fade dark patches and restore confidence. ✨ Watch the before and after results, learn about treatment options, and discover how we specialize in hy…",
  "channel_keyword_summary": "skincare routine, hyperpigmentation, dark spots, skincare, melasma, dermatology, skin care, melasma treatment, dermatologist, dermatologist skin care advice",
  "recent_video_titles": "['2025-11-03 | Accutane Survival Tips 💊 (Derm Edition) #isotretinoin #accutane #acne (28,608 views)', '2025-10-03 | Melasma Treatment Results | Dermatologist Testimonial & Before/After #hyperpigmentation (13,312 views)', '2025-06-30 | I Tried Olay Cleansing Melts and Here’s What Happened! (21,930 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=IKKi_vBNy5Q', 'https://www.youtube.com/watch?v=75ay0ZkgyUw', 'https://www.youtube.com/watch?v=aPEzll-Kwh8']",
  "best_video_title": "Dark Spot Game-Changer? Let’s Talk SkinBetter 👩🏾‍⚕️",
  "best_video_views": 1798647,
  "best_video_url": "https://www.youtube.com/watch?v=LTBr5gFBSlY",
  "recent_comments": "[]",
  "top_liked_comment": NaN,
  "comment_samples_n": 0.0,
  "est_subscribers": 577000.0,
  "est_video_count": 252.0,
  "image_url": "https://i.ytimg.com/vi/LTBr5gFBSlY/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UC2I480CzINvT-3cBAtsBySQ",
  "video_url": "https://www.youtube.com/watch?v=LTBr5gFBSlY",
  "display_score": 0.306795573010522
}
```

### #7 Mad About Skin
```json
{
  "_channel_id": "UCSqbmBSDm3Xlh7LeTRTUjjQ",
  "n_videos": 25,
  "median_views": 19289.0,
  "median_likes": 1069.0,
  "median_comments": 86.0,
  "mean_engagement": 0.0718623772105344,
  "latest_publish": "2026-02-28 11:47:40+00:00",
  "representative_video_id": "3WUR7DPmjps",
  "video_title": "Bizarre - SHOCKING BLACKHEAD REMOVAL #shorts",
  "tags_text": "skincare skincare routine skin care routine blackheads blackhead blackhead removal blackheads removal blackhead extraction short youtube shorts shorts shelf shorts video skincare shorts skin care shorts mad about skin madaboutskin mad about skin shorts madaboutskin shorts blackheads shorts blackhead shorts satisfying blackhead removal deep blackhead removal deepest blackhead removal endless blackhead removal bizzare blackhead removal huge blackhead",
  "video_description": "crazy bizzare blackhead removal which just kept going. This is a super deep blackhead removal and shows that you need to work to get it all out.\n\nHey guys and welcome to todays YouTube shorts video where we are looking at a bizzare blackhead removal, one of the deepest blackhead removals I have seen but I wish they knew what they were doing with this one.\n\nThis is a crazy deep blackhead removal in ear and I think one we can all find super satisfying so let me know your thoughts down in the comments below.\n\nIf you found this blackheads removal one of the crazy satisfying ones then let me know by giving it a thumbs up and a like.\n\n#skincare #blackheads #blackheadsremoval     \n\nThemes In Video:\n\nskincare, skin care, skincare routine, skin care routine, blackheads, blackhead, blackhead removal, blackheads removal, blackhead extraction, short, youtube shorts, shorts shelf, shorts video, skincare shorts, skin care shorts, mad about skin, madaboutskin, mad about skin shorts, madaboutskin shorts, blackheads shorts, blackhead shorts, satisfying blackhead removal, deep blackhead removal, deepest blackhead removal, endless blackhead removal, bizzare blackhead removal,",
  "all_tags": "['skincare', 'skin care', 'skincare routine', 'skin care routine', 'skin care chat', 'skincare chat', 'skincare live', 'skin care live', 'skincare livestream', 'skin care livestream', 'livestream', 'sunscreen', 'best sunscreen', 'sunscreen 2025', 'best sunscreen 2025', 'affordable sunscreen', 'mad about skin', 'madaboutskin', 'mad about skin sunscreen', 'madaboutskin sunscreen', 'live', 'live 2025', 'happy new year', 'new year', '2026', '2026 livestream', 'livestream 2026', 'skincare', 'skincare routine', 'skincare review', 'skin care review', 'skin care routine', 'how to boost collagen', 'how to boost collagen in skin', 'collagen', 'collagen in skin', 'anti ageing', 'anti-ageing', 'anti-ageing skincare', 'anti aging', 'anti aging skin care', 'collagen for anti ageing', 'collagen for anti aging', 'collagen supplements', 'how to increase collagen', 'mad about skin', 'madaboutskin', 'do collagen supplements work', 'vitamin c', 'retinoids', 'growth factors', 'reduce wrinkles', 'skin collagen', 'skincare', 'skin care', 'skincare routine', 'skin care routine', 'blackheads', 'blackhead', 'blackhead removal', 'blackheads removal', 'blackhead extraction', 'short', 'youtube shorts', 'shorts shelf', 'shorts video', 'skincare shorts', 'skin care shorts', 'mad about skin', 'mad about skin shorts', 'madaboutskin shorts', 'blackheads shorts', 'blackhead shorts', 'satisfying blackhead removal', 'blackhead removal fail', 'endless blackhead removal', 'sloppy blackhead removal', 'cheek blackhead removal', 'blackhead pop', 'pore']",
  "channel_text": "bizarre - shocking blackhead removal #shorts crazy bizzare blackhead removal which just kept going. this is a super deep blackhead removal and shows that you need to work to get it all out. hey guys and welcome to todays youtube shorts video where we are looking at a bizzare blackhead removal, one of the deepest blackhead removals i have seen but i wish they knew what they were doing with this one. this is a crazy deep blackhead removal in ear and i think one we can all find super satisfying so let me know your thoughts down in the comments below. if you found this blackheads removal one of the crazy satisfying ones then let me know by giving it a thumbs up and a like. #skincare #blackheads #blackheadsremoval themes in video: skincare, skin care, skincare routine, skin care routine, blackheads, blackhead, blackhead removal, blackheads removal, blackhead extraction, short, youtube shorts, shorts shelf, shorts video, skincare shorts, skin care shorts, mad about skin, madaboutskin, mad about skin shorts, madaboutskin shorts, blackheads shorts, blackhead shorts, satisfying blackhead removal, deep blackhead removal, deepest blackhead removal, endless blackhead removal, bizzare blackhead removal, skincare skin care skincare routine skin care routine skin care chat skincare chat skincare live skin care live skincare livestream skin care livestream livestream sunscreen best sunscreen sunscreen 2025 best sunscreen 2025 affordable sunscreen mad about skin madaboutskin mad about skin sunscreen madaboutskin sunscreen live live 2025 happy new year new year 2026 2026 livestream livestream 2026 skincare skincare routine skincare review skin care review skin care routine how to boost collagen how to boost collagen in skin collagen collagen in skin anti ageing anti-ageing anti-ageing skincare anti aging anti aging skin care collagen for anti ageing collagen for anti aging collagen supplements how to increase collagen mad about skin madaboutskin do collagen supplements work vitamin c retinoids growth factors reduce wrinkles skin collagen skincare skin care skincare routine skin care routine blackheads blackhead blackhead removal blackheads removal blackhead extraction short youtube shorts shorts shelf shorts video skincare shorts skin care shorts mad about skin mad about skin shorts madaboutskin shorts blackheads shorts blackhead shorts satisfying blackhead removal blackhead removal fail endless blackhead removal sloppy blackhead removal cheek blackhead removal blackhead pop pore",
  "days_since_latest": 2,
  "comments_n": 160.0,
  "comments_like_mean": 301.1375,
  "comment_len_median": 64.0,
  "channel_title": "Mad About Skin",
  "degree_centrality": 0.1129707112970711,
  "betweenness_centrality": 0.0070537007527628,
  "eigenvector_centrality": 0.5407407407407407,
  "sna_score_raw": 0.2181230374284173,
  "sna_score": 0.5482574846636068,
  "community_id_raw": 1,
  "community_size": 40,
  "community_id": 1,
  "graph_degree": 27,
  "is_isolated": false,
  "ml_potential_score": 0.2051458545173931,
  "tfidf_similarity_raw": 0.095101857515625,
  "keyword_boost": 0.08,
  "tfidf_similarity": 0.3480393714221697,
  "semantic_score": 0.105645978982437,
  "tone_match_score": 0.4,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.11, tone match=0.40, must-keyword hits=1, exclusion hits=0.",
  "engagement_score": 0.2463630785012936,
  "scale_score": 0.5966191296158241,
  "activity_score": 1.0,
  "interaction_score": 0.5791767375400062,
  "evidence_score": 0.7150170319197041,
  "credibility_multiplier": 0.8147610707478077,
  "eligible_recommendation": true,
  "final_score_base": 0.3474010637578149,
  "final_score": 0.2830488626862446,
  "channel_profile_text": "Weekend skincare livestream - Grab a drink and bring your skincare questions and lets chat, whether its your own skin care concerns, chatting about new product launches, answering your questions. Hey guys and welcome to a special skincare livestream where we are talking all things skincare - join us for our New Years livestream and help us break our record for the longest livestream to date Grab …",
  "channel_keyword_summary": "skincare, skin care, skincare routine, skin care routine, mad about skin, madaboutskin, skincare review, skin care review, youtube shorts, shorts shelf",
  "recent_video_titles": "['2026-02-28 | WEEKEND SKINCARE LIVESTREAM - Come Chat (1,432 views)', '2026-02-27 | SECRET TO FIRMER & LIFTED SKIN - Study Exposes Collagen Scam (6,347 views)', '2026-02-26 | Sloppy - SHOCKING BLACKHEAD REMOVAL #shorts (49,610 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=46QWFlucWc4', 'https://www.youtube.com/watch?v=hzhFW-IeNl8', 'https://www.youtube.com/watch?v=MbS2nYmoiIs']",
  "best_video_title": "Bizarre - SHOCKING BLACKHEAD REMOVAL #shorts",
  "best_video_views": 171567,
  "best_video_url": "https://www.youtube.com/watch?v=3WUR7DPmjps",
  "recent_comments": "['2025-09-10 | @alisade127: I just wish this was a longer video.', '2024-08-20 | @heathengypsy: Who are these people that such massive pores?', '2024-06-06 | @erindiazmclaughlin: Love it!!! Such a perfect blackhead removal short.']",
  "top_liked_comment": "@ericknguyen4123: Every single squeeze is so satisfying 😂 (likes 10953)",
  "comment_samples_n": 160.0,
  "est_subscribers": 712000.0,
  "est_video_count": 3368.0,
  "image_url": "https://i.ytimg.com/vi/3WUR7DPmjps/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UCSqbmBSDm3Xlh7LeTRTUjjQ",
  "video_url": "https://www.youtube.com/watch?v=3WUR7DPmjps",
  "display_score": 0.2830488626862446
}
```

### #8 Just Beauty by Julie P - makeup, beauty reviews
```json
{
  "_channel_id": "UCOGWHvRzz36S6zGpOBMrwlg",
  "n_videos": 25,
  "median_views": 903.0,
  "median_likes": 0.0,
  "median_comments": 59.0,
  "mean_engagement": 0.0633429122642175,
  "latest_publish": "2026-02-28 21:19:38+00:00",
  "representative_video_id": "MGEQ0sGGa_s",
  "video_title": "I Tried a Full Face of NEW Drugstore Makeup 🛒 Hits or Misses?",
  "tags_text": "affordable makeup covergirl covergirl review drugstore makeup drugstore makeup try on foundation review foundation testing full face drugstore makeup full face of makeup grwm makeup makeup first impressions makeup routine makeup tutorial new drugstore foundation new drugstore makeup new makeup releases nyx drugstore makeup soft glam looks softglam testing new makeup trying new makeup ulta viral drugstore makeup viral makeup woc woc beauty woc makeup",
  "video_description": "In today’s video, I’m trying a full face of newly released affordable and drugstore makeup from NYX, Covergirl, Morphe, Juvias Place and About Face Beauty. I’m testing everything from complexion to eyes and lips to see which new releases are actually worth your money — and which ones you can skip.\nI’ll be sharing first impressions, application, blendability, and how these products perform together in a full face. If you love honest drugstore makeup reviews, new makeup try-ons, and budget-friendly beauty, this video is for you!\n✨ Let me know in the comments which product surprised you the most — and don’t forget to subscribe for weekly makeup reviews and new release testing!\n\n\nHere's the link to subscribe https://youtube.com/c/JustBeautybyJulieP?sub_confirmation=1\n\n 🛍️🛍️Happy shopping!!Ulta & Sephora Link \n\n💄Ulta Beauty | Makeup, Skin Care, Fragrance, Hair Care & Beauty Products  https://go.magik.ly/ml/317j5/\n💄Makeup, Skincare, Fragrance, Hair & Beauty Products | Sephora  https://go.magik.ly/ml/2fcz3/\n\n\nThe products mentioned in this video are listed below : 💄Burgundy Wrap Lash Tubing Mascara - Revolution Beauty | Ulta Beauty  https://go.magik.ly/ml/3foru/\n💄Up All Night Lingerie Lip Liner Stain - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3fors/\n💄Up All Night Lingerie Lip Liner Stain - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3forr/\n💄Left On Melt Buttermelt Glaze Highlighter Stix - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3fork/\n💄Big Melt Energy Buttermelt Glaze Highlighter Stix - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3fori/\n💄Please Please Pink TruBlend Skin Enhancer Baked Luminous Blush - CoverGirl | Ulta Beauty  https://go.magik.ly/ml/3for9/\n💄Ready, Set, Sealed Longwear Continuous Fix And Set Spray - Juvia's Place | Ulta Beauty  https://go.magik.ly/ml/3foqw/\n💄Cacao Craze Wonder Snatch Setting Powder - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3foqm/\n💄Deep Rich Make 'EM Wonder, 24H Soft Matte Foundation - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3foqj/\n💄Orange Ya Jelly? Jelly Job Lip Gloss - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3foqi/\n💄Glow Job Jelly Job Lip Gloss - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3foqh/\n💄Big Melt Energy Buttermelt Glaze Highlighter Stix - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3fq99/\n💄Left On Melt Buttermelt Glaze Highlighter Stix - NYX Professional Makeup | Ulta Beauty  https://go.magik.ly/ml/3fq97/\n💄Radiant Peach Trublend Skin Enhancer Balm Blush Stick - CoverGirl | Ulta Beauty  https://go.magik.ly/ml/3fq9b/\n💄Bubblegum Pop Trublend Skin Enhancer Balm Blush Stick - CoverGirl | Ulta Beauty  https://go.magik.ly/ml/3fq9i/\n💄Calabasas BFF Crème Gel Liner - ColourPop | Ulta Beauty  https://go.magik.ly/ml/3ejla/\n\n\n$ Save 10% on Sigma Beauty With CODE *JULIEP*\n\n\nHere's some links to watch more of my videos \n\n\nhttps://www.youtube.com/playlist?list=PLqRu400FI36dW_jhTYHAdVtjThKMtfF-Q\n\nhttps://www.youtube.com/playlist?list=PLqRu400FI36e2OewfNUm4m4qOs32jWtJw\n\n\n\nhttps://youtu.be/IfGMqa5FbZA\n\nhttps://youtu.be/00igh8Vsq_k\n\nhttps://youtu.be/CUKNi0SEWIE\n\n https://youtube.com/playlist? \n\n\nlist=PLqRu400FI36fTgDTTKTNkFZZdnIKMx5NQ\n\nhttps://youtu.be/q9kaBt6296Q\n\nhttps://youtu.be/f22zx29Zu0U\n\nhttps://youtu.be/IfGMqa5FbZA\n\nhttps://youtu.be/00igh8Vsq_k\n\n#newdrugstoremakeup #newmakeup2025 #softglammakeup #affordableglam #affordablemakeupforblackwomen #newdrugstoremakeup #nyxcosmetics #covergirlcosmetics #nyxmakeup #juviasplace \n\n*For Business inquiries you can reach me @ jpurvis573@gmail.com*\n*You can connect with me on Twitter (no underscore) & IG @ Just_Beauty_by_JulieP  P.o Box 410171\nCharlotte, NC 28241-0171",
  "all_tags": "['foundation for oily skin', 'first impressions', 'foundation', 'foundation review', 'full coverage foundation', 'full face of makeup', 'grwm', 'makeup', 'makeup first impressions', 'makeup review', 'makeup tutorial', 'nars', 'nars cosmetics', 'nars foundation', 'nars foundation review', 'nars makeup', 'nars natural matte foundation', 'new makeup', 'new makeup releases', 'new nars natural matte foundation', 'new releases', 'oily skin makeup', 'sephora', 'softglam', 'trying new makeup', 'ulta', 'patrck ta concealer', 'drugstore makeup', 'estee lauder', 'estee lauder double wear foundation', 'estee lauder double wear foundation dark skin', 'estee lauder double wear foundation oily skin', 'estee lauder double wear foundation reformulated', 'foundation review', 'grwm', 'makeup', 'makeup first impressions', 'makeup routine', 'matte foundation', 'new drop', 'new makeup releases', 'new releases', 'oily skin makeup', 'sephora', 'testing new makeup', 'trying new makeup', 'ulta', 'viral makeup', 'woc beauty', 'woc makeup', 'milk makeup concealer', 'affordable beauty', 'affordable makeup', 'brown skin', 'drugstore makeup', 'full face of makeup', 'get ready with me', 'grwm', 'hard candy powder', 'high end makeup', 'luxury beauty', 'makeup', 'makeup first impressions', 'makeup routine', 'makeup testing', 'makeup tutorial', 'melanin makeup', 'new makeup releases', 'new releases', 'oily skin makeup', 'sephora', 'skincare', 'softglam', 'testing new makeup', 'trying new makeup', 'ulta', 'ulta finds', 'viral makeup', 'woc', 'woc beauty']",
  "channel_text": "i tried a full face of new drugstore makeup 🛒 hits or misses? in today’s video, i’m trying a full face of newly released affordable and drugstore makeup from nyx, covergirl, morphe, juvias place and about face beauty. i’m testing everything from complexion to eyes and lips to see which new releases are actually worth your money — and which ones you can skip. i’ll be sharing first impressions, application, blendability, and how these products perform together in a full face. if you love honest drugstore makeup reviews, new makeup try-ons, and budget-friendly beauty, this video is for you! ✨ let me know in the comments which product surprised you the most — and don’t forget to subscribe for weekly makeup reviews and new release testing! here's the link to subscribe https://youtube.com/c/justbeautybyjuliep?sub_confirmation=1 🛍️🛍️happy shopping!!ulta & sephora link 💄ulta beauty | makeup, skin care, fragrance, hair care & beauty products https://go.magik.ly/ml/317j5/ 💄makeup, skincare, fragrance, hair & beauty products | sephora https://go.magik.ly/ml/2fcz3/ the products mentioned in this video are listed below : 💄burgundy wrap lash tubing mascara - revolution beauty | ulta beauty https://go.magik.ly/ml/3foru/ 💄up all night lingerie lip liner stain - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3fors/ 💄up all night lingerie lip liner stain - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3forr/ 💄left on melt buttermelt glaze highlighter stix - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3fork/ 💄big melt energy buttermelt glaze highlighter stix - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3fori/ 💄please please pink trublend skin enhancer baked luminous blush - covergirl | ulta beauty https://go.magik.ly/ml/3for9/ 💄ready, set, sealed longwear continuous fix and set spray - juvia's place | ulta beauty https://go.magik.ly/ml/3foqw/ 💄cacao craze wonder snatch setting powder - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3foqm/ 💄deep rich make 'em wonder, 24h soft matte foundation - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3foqj/ 💄orange ya jelly? jelly job lip gloss - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3foqi/ 💄glow job jelly job lip gloss - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3foqh/ 💄big melt energy buttermelt glaze highlighter stix - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3fq99/ 💄left on melt buttermelt glaze highlighter stix - nyx professional makeup | ulta beauty https://go.magik.ly/ml/3fq97/ 💄radiant peach trublend skin enhancer balm blush stick - covergirl | ulta beauty https://go.magik.ly/ml/3fq9b/ 💄bubblegum pop trublend skin enhancer balm blush stick - covergirl | ulta beauty https://go.magik.ly/ml/3fq9i/ 💄calabasas bff crème gel liner - colourpop | ulta beauty https://go.magik.ly/ml/3ejla/ $ save 10% on sigma beauty with code *juliep* here's some links to watch more of my videos https://www.youtube.com/playlist?list=plqru400fi36dw_jhtyhadvtjthkmtff-q https://www.youtube.com/playlist?list=plqru400fi36e2oewfnum4m4qos32jwtjw https://youtu.be/ifgmqa5fbza https://youtu.be/00igh8vsq_k https://youtu.be/cukni0sewie https://youtube.com/playlist? list=plqru400fi36ftgdttktnkfzzdnikmx5nq https://youtu.be/q9kabt6296q https://youtu.be/f22zx29zu0u https://youtu.be/ifgmqa5fbza https://youtu.be/00igh8vsq_k #newdrugstoremakeup #newmakeup2025 #softglammakeup #affordableglam #affordablemakeupforblackwomen #newdrugstoremakeup #nyxcosmetics #covergirlcosmetics #nyxmakeup #juviasplace *for business inquiries you can reach me @ jpurvis573@gmail.com* *you can connect with me on twitter (no underscore) & ig @ just_beauty_by_juliep p.o box 410171 charlotte, nc 28241-0171 foundation for oily skin first impressions foundation foundation review full coverage foundation full face of makeup grwm makeup makeup first impressions makeup review makeup tutorial nars nars cosmetics nars foundation nars foundation review nars makeup nars natural matte foundation new makeup new makeup releases new nars natural matte foundation new releases oily skin makeup sephora softglam trying new makeup ulta patrck ta concealer drugstore makeup estee lauder estee lauder double wear foundation estee lauder double wear foundation dark skin estee lauder double wear foundation oily skin estee lauder double wear foundation reformulated foundation review grwm makeup makeup first impressions makeup routine matte foundation new drop new makeup releases new releases oily skin makeup sephora testing new makeup trying new makeup ulta viral makeup woc beauty woc makeup milk makeup concealer affordable beauty affordable makeup brown skin drugstore makeup full face of makeup get ready with me grwm hard candy powder high end makeup luxury beauty makeup makeup first impressions makeup routine makeup testing makeup tutorial melanin makeup new makeup releases new releases oily skin makeup sephora skincare softglam testing new makeup trying new makeup ulta ulta finds viral makeup woc woc beauty",
  "days_since_latest": 1,
  "comments_n": 0.0,
  "comments_like_mean": 0.0,
  "comment_len_median": 0.0,
  "channel_title": "Just Beauty by Julie P - makeup, beauty reviews",
  "degree_centrality": 0.1589958158995816,
  "betweenness_centrality": 0.0105989896756375,
  "eigenvector_centrality": 0.9037037037037036,
  "sna_score_raw": 0.3542944979588009,
  "sna_score": 0.8905277157842344,
  "community_id_raw": 0,
  "community_size": 82,
  "community_id": 0,
  "graph_degree": 38,
  "is_isolated": false,
  "ml_potential_score": 0.1888779939554256,
  "tfidf_similarity_raw": 0.0493719520582719,
  "keyword_boost": 0.0,
  "tfidf_similarity": 0.0981336429210245,
  "semantic_score": 0.0386019074338248,
  "tone_match_score": 0.4,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.04, tone match=0.40, must-keyword hits=0, exclusion hits=0.",
  "engagement_score": 0.2161656200734577,
  "scale_score": 0.3755024385493754,
  "activity_score": 1.0,
  "interaction_score": 0.3362318046267515,
  "evidence_score": 0.5569611118961693,
  "credibility_multiplier": 0.71202472273251,
  "eligible_recommendation": true,
  "final_score_base": 0.3838879718411102,
  "final_score": 0.2733377267105121,
  "channel_profile_text": "Today I’m testing the *NEW* NARS Natural Matte Longwear Pore Blurring Medium-to-Full Coverage Foundation to see if it actually lives up to the claims! In this first impressions + wear test, I’m sharing application, coverage, finish, pore blurring, how the *NEW* NARS Natural Matte Longwear Pore Blurring Medium-to-Full Coverage foundation performs throughout the day, and my honest thoughts on wheth…",
  "channel_keyword_summary": "makeup, woc beauty, ulta, woc makeup, full face of makeup, makeup tutorial, woc, grwm, oily skin makeup, sephora",
  "recent_video_titles": "['2026-02-28 | Is the *NEW* NARS Natural Matte Foundation Worth It? | First Impressions + Wear Test (341 views)', '2026-02-26 | NEW Estée Lauder Double Wear Reformulated 😳 | Wear Test + New Patrick Ta Concealer (901 views)', '2026-02-21 | Testing NEW Makeup Releases | First Impressions & Second Chances (846 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=bFOfDE4GyvU', 'https://www.youtube.com/watch?v=pKxFAfhKvP0', 'https://www.youtube.com/watch?v=NOiMx9bz4fs']",
  "best_video_title": "I Tried a Full Face of NEW Drugstore Makeup 🛒 Hits or Misses?",
  "best_video_views": 1673,
  "best_video_url": "https://www.youtube.com/watch?v=MGEQ0sGGa_s",
  "recent_comments": "[]",
  "top_liked_comment": NaN,
  "comment_samples_n": 0.0,
  "est_subscribers": 0.0,
  "est_video_count": 0.0,
  "image_url": "https://i.ytimg.com/vi/MGEQ0sGGa_s/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UCOGWHvRzz36S6zGpOBMrwlg",
  "video_url": "https://www.youtube.com/watch?v=MGEQ0sGGa_s",
  "display_score": 0.2733377267105121
}
```

### #9 James Welsh
```json
{
  "_channel_id": "UCPP291gN79qI1QZY1znOscg",
  "n_videos": 22,
  "median_views": 63281.0,
  "median_likes": 3335.5,
  "median_comments": 333.0,
  "mean_engagement": 0.0531673293278704,
  "latest_publish": "2026-02-21 19:52:36+00:00",
  "representative_video_id": "pmO5Jg_p1Io",
  "video_title": "The Worst Beauty Scandals of 2025 - WITH UPDATES!",
  "tags_text": "james welsh best skin skincare skin care routine skin care kbeauty korean skin care yesstyle welsh twins the welsh twins viral react when beauty turns ugly instagram vs reality react to best of skincare controversy updates on skincare controversy sonya dakar caveman routine caveman skincare routine matt rife and elf elf and matt rife elf matt rife dr mehss my magic healing fake doctors fake tiktok dr fake tiktok doctor",
  "video_description": "Instagram - james_s_welsh\nUnboxing Channel - @JaymesPlays1\n\n2025 has been one of the messiest years the skincare industry has ever seen.\n\nShocking client horror stories and AI “doctors” spreading misinformation, to disastrous brand collaborations, bizarre TikTok skincare trends, and a sunscreen scandal that shook consumer trust... this year exposed some very uncomfortable truths about the beauty industry.\n\nToday i'm breaking down five of the ugliest skincare news stories of 2025. Some of these went viral, some quietly disappeared, and some are still unfolding right now. I’ll recap what happened, explain why it matters, and update you on where things stand today!\n\nWatch the full story on Victoria Nelson peel gone wrong here:\nhttps://www.youtube.com/watch?v=DdLuexfsjLc\n\nWatch the full story on Dr Mehss and My Magic Healer here:\nhttps://www.youtube.com/watch?v=uqtuGLhYj4A",
  "all_tags": "['skincare', 'beauty fails', 'best skin', 'clear skin', 'influencer react', 'insta reality', 'instagram vs reality', 'james welsh', 'james welsh react', 'kbeauty', 'korean skin care', 'korean skincare', 'react', 'sephora kids', 'skin care', 'skin care routine', 'skincare', 'skincare routine', 'the welsh twins', 'viral', 'welsh twins', 'when beauty turns ugly', 'yesstyle', 'rhode beauty', 'rhode skincare', 'hailey rhode beiber', 'rhode gross lip balms', 'rhode brought by elf', 'will rhode go downhill now elf has brought them?', 'rhode', 'james welsh', 'best skin', 'skincare', 'skin care routine', 'skin care', 'kbeauty', 'korean skin care', 'yesstyle', 'welsh twins', 'the welsh twins', 'viral', 'react', 'when beauty turns ugly', 'instagram vs reality', 'drunk elephant', 'sephora kids', 'drunk elephant kids', 'skincare smoothies', 'drunk elephant rebrand', 'drunk elephant for teens', 'kids skincare', 'teens skincare', 'shiseido', 'drunk elephant decline', 'skincare for kids', 'sephora kids grwm', 'skincare', 'best skin', 'glow up', 'instagram vs reality', 'james welsh', 'kbeauty', 'korean beauty', 'korean skin care', 'react', 'skin care', 'skin care routine', 'skin transformation', 'skin transformations', 'the welsh twins', 'viral', 'welsh twins', 'when beauty turns ugly', 'yesstyle', 'yesstyle haul', 'jiyu', 'jiyu toner pads', 'jiyu skin', 'jiyu korean skincare toner pads', 'is jiyu a scam?']",
  "channel_text": "the worst beauty scandals of 2025 - with updates! instagram - james_s_welsh unboxing channel - @jaymesplays1 2025 has been one of the messiest years the skincare industry has ever seen. shocking client horror stories and ai “doctors” spreading misinformation, to disastrous brand collaborations, bizarre tiktok skincare trends, and a sunscreen scandal that shook consumer trust... this year exposed some very uncomfortable truths about the beauty industry. today i'm breaking down five of the ugliest skincare news stories of 2025. some of these went viral, some quietly disappeared, and some are still unfolding right now. i’ll recap what happened, explain why it matters, and update you on where things stand today! watch the full story on victoria nelson peel gone wrong here: https://www.youtube.com/watch?v=ddluexfsjlc watch the full story on dr mehss and my magic healer here: https://www.youtube.com/watch?v=uqtuglhyj4a skincare beauty fails best skin clear skin influencer react insta reality instagram vs reality james welsh james welsh react kbeauty korean skin care korean skincare react sephora kids skin care skin care routine skincare skincare routine the welsh twins viral welsh twins when beauty turns ugly yesstyle rhode beauty rhode skincare hailey rhode beiber rhode gross lip balms rhode brought by elf will rhode go downhill now elf has brought them? rhode james welsh best skin skincare skin care routine skin care kbeauty korean skin care yesstyle welsh twins the welsh twins viral react when beauty turns ugly instagram vs reality drunk elephant sephora kids drunk elephant kids skincare smoothies drunk elephant rebrand drunk elephant for teens kids skincare teens skincare shiseido drunk elephant decline skincare for kids sephora kids grwm skincare best skin glow up instagram vs reality james welsh kbeauty korean beauty korean skin care react skin care skin care routine skin transformation skin transformations the welsh twins viral welsh twins when beauty turns ugly yesstyle yesstyle haul jiyu jiyu toner pads jiyu skin jiyu korean skincare toner pads is jiyu a scam?",
  "days_since_latest": 8,
  "comments_n": 0.0,
  "comments_like_mean": 0.0,
  "comment_len_median": 0.0,
  "channel_title": "James Welsh",
  "degree_centrality": 0.1087866108786611,
  "betweenness_centrality": 0.0061539562315458,
  "eigenvector_centrality": 0.4814814814814814,
  "sna_score_raw": 0.1968808155975726,
  "sna_score": 0.4948646507522999,
  "community_id_raw": 1,
  "community_size": 40,
  "community_id": 1,
  "graph_degree": 26,
  "is_isolated": false,
  "ml_potential_score": 0.1731425335378687,
  "tfidf_similarity_raw": 0.1333258138250815,
  "keyword_boost": 0.08,
  "tfidf_similarity": 0.4240148174623386,
  "semantic_score": 0.1436470667693913,
  "tone_match_score": 0.2,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.14, tone match=0.20, must-keyword hits=1, exclusion hits=0.",
  "engagement_score": 0.1800980096500852,
  "scale_score": 0.6824510698594141,
  "activity_score": 0.9522008800151638,
  "interaction_score": 0.6740338921312309,
  "evidence_score": 0.7621134362469115,
  "credibility_multiplier": 0.8453737335604925,
  "eligible_recommendation": true,
  "final_score_base": 0.319138373534866,
  "final_score": 0.2697911983575928,
  "channel_profile_text": "Instagram - james_s_welsh Unboxing Channel - @JaymesPlays1 Rhode has grown at a speed that most brands don’t come close to. In under three years it went from a tightly edited launch with three products to a $1 billion acquisition by e.l.f. Beauty. Since then it’s expanded into Sephora, broken sales records, and become one of the fastest-growing brands in Sephora history! That kind of growth chang…",
  "channel_keyword_summary": "skincare, best skin, instagram vs reality, james welsh, kbeauty, korean skin care, react, skin care, skin care routine, the welsh twins",
  "recent_video_titles": "['2026-02-21 | When a product floods your feed it gets boring, but some are worth the hype! #skincaretips (22,010 views)', '2026-02-18 | These videos always make people MAD! But I know you have opinions too 🤭 #skincare #skincaretips (98,847 views)', '2026-02-16 | The Ruthless Rise of Rhode Skincare -Quality Complaints & Corporate Control - Behind The Beauty (108,128 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=l5q5RogCUzg', 'https://www.youtube.com/watch?v=HmxV_ypdUbg', 'https://www.youtube.com/watch?v=QCZ0VpORhn4']",
  "best_video_title": "The Worst Beauty Scandals of 2025 - WITH UPDATES!",
  "best_video_views": 194465,
  "best_video_url": "https://www.youtube.com/watch?v=pmO5Jg_p1Io",
  "recent_comments": "[]",
  "top_liked_comment": NaN,
  "comment_samples_n": 0.0,
  "est_subscribers": 1560000.0,
  "est_video_count": 1029.0,
  "image_url": "https://i.ytimg.com/vi/pmO5Jg_p1Io/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UCPP291gN79qI1QZY1znOscg",
  "video_url": "https://www.youtube.com/watch?v=pmO5Jg_p1Io",
  "display_score": 0.2697911983575928
}
```

### #10 Morgan Turner
```json
{
  "_channel_id": "UCCnngeLwoZCSSuSs9ePuDqA",
  "n_videos": 23,
  "median_views": 24748.0,
  "median_likes": 1768.0,
  "median_comments": 107.0,
  "mean_engagement": 0.0734825166211981,
  "latest_publish": "2026-02-26 21:59:41+00:00",
  "representative_video_id": "0oa8Gp12yc8",
  "video_title": "8 NEW VIRAL DRUGSTORE PRODUCTS BETTER THAN HIGH END?!! ULTA HAUL",
  "tags_text": "new makeup trending makeup tiktok makeup viral makeup ulta beauty best & worst makeup tiktok makeup review new at ulta drugstore makeup new affordable makeup viral drugstore makeup viral affordable makeup drugstore better than high end new drugstore makeup hourglass dupe tiktok viral drugstore makeup milani baked bronzer milani hourglass dupe milani baked blush milani reformulation loreal lumi bronze le stick covergirl morphe maybellline nyx foundation",
  "video_description": "MENTIONED\nNYX Make Em Wonder Soft Matte Foundation (06 Light) https://go.magik.ly/ml/3fyci/\nAboutFace The Illusionist Skin Focused Concealer (L1 Neutral) https://go.magik.ly/ml/3fyck/\nLoreal Lumi Bronze Le Stick (100 Sunkissed Rose) https://go.magik.ly/ml/3fyct/\nMaybelline Cloudtopia Cheek & Mousse (09 Dreamy Dawn) https://go.magik.ly/ml/3fycu/\nMilani Baked Bronzer (Tuscan Tan) https://go.magik.ly/ml/3fycy/\nMilani Baked Blush (Sparkling Rose) https://go.magik.ly/ml/3fyd0/\nMilani Baked Highlighter (Champagne Doro) https://go.magik.ly/ml/3fyd3/\nMorphe Lip Pencil (Wifey) https://go.magik.ly/ml/3fyda/\nCovergirl Outlast Lipstain (Honey Sculpt) https://go.magik.ly/ml/3fydh/\n\nAlso Wearing/Mentioned\nColourpop Matcha & Mochi Supershock Shadow Kit (Wearing Double Matcha) https://go.magik.ly/ml/3epzb/\nCatrice Colour Cushion Juicy Lip Oil (Drenched Drama) https://rstyle.me/+gUo26ZZm-eNMvL82fIlykA\n▶▶ Which were the BEST products of 2024? https://www.youtube.com/watch?v=Ga5GAikoc1I&list=PLDWlCCsOZN8O6G2V5vP1AFpPwpKnBOzwJ&index=76\n\n✔ BUYING LINKS & CODES  🛒\nLaura Mercier 20% OFF code MORGAN20 https://www.lauramercier.com/MORGAN20\nBuxom 20% OFF Code MORGAN https://buxomcosmetics.com/MORGAN\nBare Minerals 20% off code MORGAN https://www.bareminerals.com/MORGAN\nSigma Beauty 10% off code MORGANTURNER10 https://sigmabeauty.com/MORGANTURNER10\nCharlotte Tilbury 15% off https://friends.charlottetilbury.com/a/morganturnermakeup\nESUM Cosmetics https://www.esumcosmetics.com/?aff=46\nRephr Brushes || rephr.com/?vr=dfseea\nSigma Beauty code morganturner10 https://www.sigmabeauty.com/MORGANTURNER10\nVegamour https://glnk.io/3v43p/morgan\nNomad Cosmetics // code MORGANTURNER for 10% off\nCODE \"morganturner\" 10% off Odens Eye! https://www.odenseye.se/discount/morganturner\nCODE \"morgan10\" 10% off at bkbeauty (unaffiliated)\nHaleys Beauty MORGANTURNER for 15% off https://haleysbeauty.com/morganturner\n\n▶ My Gear\n📹 Camera: https://amzn.to/4bfH2ie\n🔭 Lens: https://amzn.to/4biPGMN\n\n👥 S O C I A L S \nInstragram || instagram.com/morganturnermakeup/\nTikTok || tiktok.com/@morganturnermakeup\nBusiness || morganturner@dulcedo.com\n\n*Some of the links above are affiliate links. I do receive a small commission with NO extra cost. All earnings go back into improving the content on my channel. However,  feel no pressure to use them. 🤗\n\nI use MagicLinks for all my ready-to-shop product links. \nCheck it out here || magiclinks.org/rewards/referral/morganturn/\n\n\n#MorganTurner #Makeup #Sephora #Ulta #ViralMakeup #NewMakeup #NatashaDenona #PatMcGrath #MAC #Beauty #Luxury #HighEndMakeup #Celebrities #NewLaunches #MakeupReleases #MakeupTutorial #BestMakeup #UltaBeauty #NewatSephora #WorstMakeup #Viral #Makeup2024 #Makeup2025 #MakeupTrends",
  "all_tags": "['new makeup', 'makeup releases', 'trending makeup', 'beauty', 'tiktok makeup', 'viral makeup', 'value makeup', 'makeup', 'makeup tutorial', 'sephora', 'ulta', 'ulta beauty', 'new at sephora', 'viral sephora', 'best & worst makeup', 'morgan turner', 'natashadenona', 'natasha denona', 'natasha denona reviews', 'new natasha denona', 'morgan turner natasha denona', 'best of natasha denona', 'worst of natasha denona', 'natasha denona hy glam', 'natasha denona eyeshadow', 'eye sculpt', 'eyeshadow', 'best sephora makeup', '2025', 'new makeup', 'makeup releases', 'trending makeup', 'beauty', 'professional artist', 'tiktok makeup', 'viral makeup', 'makeup', 'makeup tutorial', 'sephora', 'ulta', 'ulta beauty', 'new at sephora', 'viral sephora', 'best & worst makeup', 'morgan turner', 'natashadenona', 'natasha denona', 'new natasha denona', 'natasha denona luxe glam quad', 'natasha denona 28 pan palette', 'natasha denona quad', 'morgan turner natasha denona', 'rosy', 'cool', 'nude', 'swatches', 'natasha denona luxe glam quad review', 'natasha denona quad review', 'new makeup', 'makeup releases', 'trending makeup', 'beauty', 'professional artist', 'tiktok makeup', 'viral makeup', 'makeup', 'makeup tutorial', 'sephora', 'ulta', 'ulta beauty', 'new at sephora', 'viral sephora', 'best & worst makeup', 'morgan turner', 'natashadenona', 'natasha denona', 'new natasha denona', 'natasha denona luxe glam quad', 'natasha denona 28 pan palette', 'natasha denona quad']",
  "channel_text": "8 new viral drugstore products better than high end?!! ulta haul mentioned nyx make em wonder soft matte foundation (06 light) https://go.magik.ly/ml/3fyci/ aboutface the illusionist skin focused concealer (l1 neutral) https://go.magik.ly/ml/3fyck/ loreal lumi bronze le stick (100 sunkissed rose) https://go.magik.ly/ml/3fyct/ maybelline cloudtopia cheek & mousse (09 dreamy dawn) https://go.magik.ly/ml/3fycu/ milani baked bronzer (tuscan tan) https://go.magik.ly/ml/3fycy/ milani baked blush (sparkling rose) https://go.magik.ly/ml/3fyd0/ milani baked highlighter (champagne doro) https://go.magik.ly/ml/3fyd3/ morphe lip pencil (wifey) https://go.magik.ly/ml/3fyda/ covergirl outlast lipstain (honey sculpt) https://go.magik.ly/ml/3fydh/ also wearing/mentioned colourpop matcha & mochi supershock shadow kit (wearing double matcha) https://go.magik.ly/ml/3epzb/ catrice colour cushion juicy lip oil (drenched drama) https://rstyle.me/+guo26zzm-enmvl82filyka ▶▶ which were the best products of 2024? https://www.youtube.com/watch?v=ga5gaikoc1i&list=pldwlccsozn8o6g2v5vp1afppwpknbozwj&index=76 ✔ buying links & codes 🛒 laura mercier 20% off code morgan20 https://www.lauramercier.com/morgan20 buxom 20% off code morgan https://buxomcosmetics.com/morgan bare minerals 20% off code morgan https://www.bareminerals.com/morgan sigma beauty 10% off code morganturner10 https://sigmabeauty.com/morganturner10 charlotte tilbury 15% off https://friends.charlottetilbury.com/a/morganturnermakeup esum cosmetics https://www.esumcosmetics.com/?aff=46 rephr brushes || rephr.com/?vr=dfseea sigma beauty code morganturner10 https://www.sigmabeauty.com/morganturner10 vegamour https://glnk.io/3v43p/morgan nomad cosmetics // code morganturner for 10% off code \"morganturner\" 10% off odens eye! https://www.odenseye.se/discount/morganturner code \"morgan10\" 10% off at bkbeauty (unaffiliated) haleys beauty morganturner for 15% off https://haleysbeauty.com/morganturner ▶ my gear 📹 camera: https://amzn.to/4bfh2ie 🔭 lens: https://amzn.to/4bipgmn 👥 s o c i a l s instragram || instagram.com/morganturnermakeup/ tiktok || tiktok.com/@morganturnermakeup business || morganturner@dulcedo.com *some of the links above are affiliate links. i do receive a small commission with no extra cost. all earnings go back into improving the content on my channel. however, feel no pressure to use them. 🤗 i use magiclinks for all my ready-to-shop product links. check it out here || magiclinks.org/rewards/referral/morganturn/ #morganturner #makeup #sephora #ulta #viralmakeup #newmakeup #natashadenona #patmcgrath #mac #beauty #luxury #highendmakeup #celebrities #newlaunches #makeupreleases #makeuptutorial #bestmakeup #ultabeauty #newatsephora #worstmakeup #viral #makeup2024 #makeup2025 #makeuptrends new makeup makeup releases trending makeup beauty tiktok makeup viral makeup value makeup makeup makeup tutorial sephora ulta ulta beauty new at sephora viral sephora best & worst makeup morgan turner natashadenona natasha denona natasha denona reviews new natasha denona morgan turner natasha denona best of natasha denona worst of natasha denona natasha denona hy glam natasha denona eyeshadow eye sculpt eyeshadow best sephora makeup 2025 new makeup makeup releases trending makeup beauty professional artist tiktok makeup viral makeup makeup makeup tutorial sephora ulta ulta beauty new at sephora viral sephora best & worst makeup morgan turner natashadenona natasha denona new natasha denona natasha denona luxe glam quad natasha denona 28 pan palette natasha denona quad morgan turner natasha denona rosy cool nude swatches natasha denona luxe glam quad review natasha denona quad review new makeup makeup releases trending makeup beauty professional artist tiktok makeup viral makeup makeup makeup tutorial sephora ulta ulta beauty new at sephora viral sephora best & worst makeup morgan turner natashadenona natasha denona new natasha denona natasha denona luxe glam quad natasha denona 28 pan palette natasha denona quad",
  "days_since_latest": 3,
  "comments_n": 0.0,
  "comments_like_mean": 0.0,
  "comment_len_median": 0.0,
  "channel_title": "Morgan Turner",
  "degree_centrality": 0.1589958158995816,
  "betweenness_centrality": 0.0086716379858274,
  "eigenvector_centrality": 0.8,
  "sna_score_raw": 0.3194169761620433,
  "sna_score": 0.8028622284655655,
  "community_id_raw": 0,
  "community_size": 82,
  "community_id": 0,
  "graph_degree": 38,
  "is_isolated": false,
  "ml_potential_score": 0.2054892737333527,
  "tfidf_similarity_raw": 0.0193141027820776,
  "keyword_boost": 0.0,
  "tfidf_similarity": 0.0383894739166753,
  "semantic_score": 0.0160915222736599,
  "tone_match_score": 0.2,
  "red_flags": "['Low semantic relevance to brand brief']",
  "alignment_rationale": "Semantic fit=0.02, tone match=0.20, must-keyword hits=0, exclusion hits=0.",
  "engagement_score": 0.2521057035146127,
  "scale_score": 0.6146232676941258,
  "activity_score": 0.9687936498860342,
  "interaction_score": 0.6189377773776996,
  "evidence_score": 0.7215215588042344,
  "credibility_multiplier": 0.8189890132227524,
  "eligible_recommendation": true,
  "final_score_base": 0.3293150745645808,
  "final_score": 0.2697054279570232,
  "channel_profile_text": "Products Mentioned Mini Eye Sculpt https://go.magik.ly/ml/3jmfo/ Mini Gloom Palette https://go.magik.ly/ml/3ds4y/ Eye Sculpt Texture & Tone soft https://go.magik.ly/ml/3jmfq/ dramatic https://go.magik.ly/ml/3jmfr/ Eye Sculpt Cool https://go.magik.ly/ml/3jmft/ HyGlam Foundation https://go.magik.ly/ml/3jmg3/ HyBlush https://go.magik.ly/ml/3jmg4/ Videos Featured Eye Sculpt Palette https://www.youtub…",
  "channel_keyword_summary": "trending makeup, new makeup, tiktok makeup, viral makeup, ulta beauty, best & worst makeup, makeup releases, sephora, new at sephora, viral sephora",
  "recent_video_titles": "['2026-02-26 | 2.5 hours of every NATASHA DENONA product review 2025 (4,552 views)', '2026-02-25 | the price on these is kind of crazy... NEW Natasha Denona Luxe Glam Compacts (39,040 views)', '2026-02-23 | NATASHA DENONA LUXE GLAM QUADS!! $48 is kind of crazy.. (23,000 views)']",
  "recent_video_urls": "['https://www.youtube.com/watch?v=wsIM1bDGuy8', 'https://www.youtube.com/watch?v=v9IAS_j2wmI', 'https://www.youtube.com/watch?v=TkAMXPRGx5w']",
  "best_video_title": "8 NEW VIRAL DRUGSTORE PRODUCTS BETTER THAN HIGH END?!! ULTA HAUL",
  "best_video_views": 116443,
  "best_video_url": "https://www.youtube.com/watch?v=0oa8Gp12yc8",
  "recent_comments": "[]",
  "top_liked_comment": NaN,
  "comment_samples_n": 0.0,
  "est_subscribers": 0.0,
  "est_video_count": 0.0,
  "image_url": "https://i.ytimg.com/vi/0oa8Gp12yc8/hqdefault.jpg",
  "channel_url": "https://www.youtube.com/channel/UCCnngeLwoZCSSuSs9ePuDqA",
  "video_url": "https://www.youtube.com/watch?v=0oa8Gp12yc8",
  "display_score": 0.2697054279570232
}
```
