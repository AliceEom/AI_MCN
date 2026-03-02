from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
SLIDES_DIR = ROOT / "slides"
ASSETS_DIR = SLIDES_DIR / "assets"
DATA_DIR = ROOT / "data"
SUMMARY_JSON = ROOT / "artifacts" / "reports" / "presentation_summary_boj.json"
OUT_PPTX = SLIDES_DIR / "AI_MCN_Final_Presentation_EN.pptx"


def add_title(slide, title: str, subtitle: str | None = None, accent: bool = True) -> None:
    title_box = slide.shapes.add_textbox(Inches(0.65), Inches(0.35), Inches(12.1), Inches(1.0))
    tf = title_box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.name = "Aptos Display"
    p.font.color.rgb = RGBColor(15, 44, 89)

    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.72), Inches(1.28), Inches(11.8), Inches(0.68))
        stf = sub_box.text_frame
        stf.clear()
        sp = stf.paragraphs[0]
        sp.text = subtitle
        sp.font.size = Pt(16)
        sp.font.name = "Aptos"
        sp.font.color.rgb = RGBColor(74, 95, 128)

    if accent:
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.62), Inches(1.92), Inches(2.9), Inches(0.08))
        line.fill.solid()
        line.fill.fore_color.rgb = RGBColor(26, 125, 188)
        line.line.fill.background()


def add_bullets(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    bullets: list[str],
    font_size: int = 21,
) -> None:
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.clear()
    for i, txt in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = txt
        p.level = 0
        p.font.size = Pt(font_size)
        p.font.name = "Aptos"
        p.font.color.rgb = RGBColor(28, 45, 70)
        p.space_after = Pt(8)


def add_card(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    title: str,
    bullets: list[str],
    title_size: int = 18,
    body_size: int = 15,
) -> None:
    rect = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor(242, 247, 252)
    rect.line.color.rgb = RGBColor(205, 220, 238)
    rect.line.width = Pt(1.25)

    title_box = slide.shapes.add_textbox(Inches(left + 0.20), Inches(top + 0.12), Inches(width - 0.30), Inches(0.38))
    ttf = title_box.text_frame
    ttf.clear()
    tp = ttf.paragraphs[0]
    tp.text = title
    tp.font.bold = True
    tp.font.size = Pt(title_size)
    tp.font.color.rgb = RGBColor(19, 58, 102)
    tp.font.name = "Aptos"

    add_bullets(
        slide,
        left=left + 0.18,
        top=top + 0.48,
        width=width - 0.28,
        height=height - 0.58,
        bullets=bullets,
        font_size=body_size,
    )


def add_footer(slide, text: str) -> None:
    box = slide.shapes.add_textbox(Inches(0.55), Inches(7.03), Inches(12.0), Inches(0.32))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.RIGHT
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(110, 128, 152)
    p.font.name = "Aptos"


def image_path(name: str) -> Path:
    p = ASSETS_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Missing image asset: {p}")
    return p


def compute_keyword_snapshot() -> dict[str, object]:
    candidates = [
        DATA_DIR / "videos_text_ready_combined.csv",
        DATA_DIR / "videos_text_ready_demo.csv",
    ]
    source = next((p for p in candidates if p.exists()), None)
    if source is None:
        return {"source_file": "N/A", "total_videos": 0, "total_channels": 0, "keywords": {}}

    usecols = ["_channel_id", "snippet__title", "snippet__description", "snippet__tags"]
    df = pd.read_csv(source, usecols=usecols, low_memory=False)
    text = (
        df["snippet__title"].fillna("")
        + " "
        + df["snippet__description"].fillna("")
        + " "
        + df["snippet__tags"].fillna("")
    ).str.lower()

    keywords = ["sunscreen", "spf", "k-beauty", "beauty of joseon", "cerave"]
    out: dict[str, dict[str, int]] = {}
    for kw in keywords:
        m = text.str.contains(kw, regex=False)
        out[kw] = {
            "videos": int(m.sum()),
            "channels": int(df.loc[m, "_channel_id"].astype(str).nunique()),
        }

    return {
        "source_file": source.name,
        "total_videos": int(len(df)),
        "total_channels": int(df["_channel_id"].astype(str).nunique()),
        "keywords": out,
    }


def _fmt_kw(kw_snapshot: dict[str, object], keyword: str) -> str:
    row = (kw_snapshot.get("keywords") or {}).get(keyword, {})
    return f"{keyword}: {int(row.get('videos', 0)):,} videos | {int(row.get('channels', 0)):,} channels"


def build() -> Path:
    if not SUMMARY_JSON.exists():
        raise FileNotFoundError(f"Missing summary file: {SUMMARY_JSON}")
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))

    dataset = summary.get("dataset", {})
    roi = summary.get("roi", {})
    ml_table = summary.get("ml_table", [])
    top10 = summary.get("top10", [])
    kw_snapshot = compute_keyword_snapshot()

    best_model = summary.get("ml_best_model", "N/A")
    baseline_rmse = next((x.get("rmse_mean", 0.0) for x in ml_table if x.get("model") == "BaselineMedian"), 0.0)
    best_rmse = next((x.get("rmse_mean", 0.0) for x in ml_table if x.get("model") == best_model), 0.0)
    gain_pct = ((baseline_rmse - best_rmse) / baseline_rmse * 100.0) if baseline_rmse else 0.0

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # 1. Title and team
    slide = prs.slides.add_slide(blank)
    add_title(
        slide,
        "AI-MCN: Replacing Traditional MCN Matching with an AI Decision System",
        "MSIS 521 Course Project | 15-minute Presentation",
    )
    add_bullets(
        slide,
        0.72,
        2.2,
        11.9,
        2.5,
        [
            "Client case: Beauty of Joseon (BOJ), U.S. sunscreen campaign",
            "Goal: help brands find best-fit influencers directly with transparent AI logic",
            "Team: [Add names]",
        ],
        font_size=23,
    )
    add_footer(slide, "Section 1 | Title and Team")

    # 2. Agenda and timing
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Agenda and Timing (Professor Guide)")
    add_bullets(
        slide,
        0.82,
        2.1,
        12.0,
        4.8,
        [
            "1) Title and team (1 min)",
            "2) Business context and problem (2-3 min)",
            "3) Data and features (1-3 min)",
            "4) AI/ML approach (3-4 min)",
            "5) Prototype demo (3-4 min)",
            "6) Impact, limitations, next steps (2-3 min)",
            "7) How we used AI tools (1-2 min)",
        ],
        font_size=21,
    )
    add_footer(slide, "Section 2 | Roadmap")

    # 3. Business context
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Business Context and Problem")
    add_card(
        slide,
        0.65,
        2.0,
        5.95,
        4.8,
        "Current MCN-Style Workflow",
        [
            "MCNs aggregate influencer data and broker brand-creator matching.",
            "Brands pay agency/management fees plus campaign budget.",
            "Matching logic is often hard to audit for brand teams.",
        ],
    )
    add_card(
        slide,
        6.72,
        2.0,
        5.95,
        4.8,
        "Decision We Improve",
        [
            "From manual or popularity-led creator selection",
            "To evidence-based, product-specific creator ranking",
            "Goal: reduce expensive mismatch risk before launch",
        ],
    )
    add_footer(slide, "Section 3 | Context and Decision")

    # 4. Why now / market evidence
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Why Now: Market Evidence")
    add_bullets(
        slide,
        0.8,
        2.0,
        12.0,
        4.7,
        [
            "US influencer marketing spend is projected at $10.52B in 2025 (EMARKETER, Mar 13, 2025).",
            "YouTube influencer use among US marketers is projected to exceed 50% in 2025 (EMARKETER).",
            "Global beauty grew 7.3% YoY in 2025; US beauty sales are 41% e-commerce (NIQ, Feb 25, 2025).",
            "McKinsey projects core beauty segments to reach about $590B by 2030, with skincare as the largest segment (Aug 28, 2025).",
        ],
        font_size=18,
    )
    add_footer(slide, "Section 3 | External Industry Context")

    # 5. Why beauty and BOJ
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Why Beauty and Why BOJ")
    add_card(
        slide,
        0.65,
        2.0,
        5.95,
        4.75,
        "Case Fit",
        [
            "Beauty creator marketing is large and highly content-driven.",
            "BOJ has visible social momentum and a product-specific campaign story.",
            "BOJ U.S. expansion + sunscreen focus make a practical demo scenario.",
            "(Fashionista coverage, Nov 13, 2024)",
        ],
    )
    add_card(
        slide,
        6.72,
        2.0,
        5.95,
        4.75,
        "Dataset Feasibility Signals",
        [
            f"Source file: {kw_snapshot.get('source_file', 'N/A')} (n={int(kw_snapshot.get('total_videos', 0)):,} videos)",
            _fmt_kw(kw_snapshot, "sunscreen"),
            _fmt_kw(kw_snapshot, "spf"),
            _fmt_kw(kw_snapshot, "beauty of joseon"),
            _fmt_kw(kw_snapshot, "cerave"),
        ],
    )
    add_footer(slide, "Section 3 | Client and Case Selection")

    # 6. Data and features
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Data and Features")
    add_card(
        slide,
        0.7,
        2.0,
        6.0,
        4.7,
        "Data Used",
        [
            "Team-collected YouTube API exports (videos/comments/channel fields)",
            f"Videos analyzed (full run): {int(dataset.get('videos_analyzed', 0)):,}",
            f"Channels scored: {int(dataset.get('channels_scored', 0)):,}",
            "Main files: videos_text_ready, comments_raw, master_prd_slim",
        ],
    )
    add_card(
        slide,
        6.75,
        2.0,
        5.9,
        4.7,
        "Feature Groups",
        [
            "Network features: centrality + community",
            "Text features: TF-IDF + semantic/tone alignment",
            "Behavioral features: views/likes/comments/engagement",
            "Reliability features: evidence score + credibility multiplier",
        ],
    )
    add_footer(slide, "Section 4 | Data and Feature Engineering")

    # 7. Preprocessing and EDA
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Preprocessing and EDA")
    slide.shapes.add_picture(str(image_path("community_distribution_clean.png")), Inches(0.78), Inches(2.0), height=Inches(4.8))
    add_card(
        slide,
        8.0,
        2.0,
        4.5,
        4.8,
        "What we did",
        [
            "Deduplication + type normalization",
            "Beauty include filter + non-beauty noise exclusion",
            "Channel-level aggregation and recency features",
            "EDA confirmed cluster concentration -> diversity guardrail needed",
        ],
        body_size=14,
    )
    add_footer(slide, "Section 4 | Data Understanding")

    # 8. AI/ML approach
    slide = prs.slides.add_slide(blank)
    add_title(slide, "AI/ML Approach (Class-Learned Methods Focus)")
    add_bullets(
        slide,
        0.75,
        2.0,
        12.0,
        4.9,
        [
            "1) Social Network Analysis: creator graph, centrality, communities",
            "2) Text Analytics: TF-IDF relevance + semantic/tone enrichment",
            "3) Supervised Regression: Linear, LASSO, Ridge, CART, RandomForest, LightGBM",
            "4) Validation: GroupKFold(5) by channel to reduce leakage",
            "5) Explainability: SHAP for feature contribution",
            "Extensions shown in demo: ROI simulator, strategy and memo generation",
        ],
        font_size=18,
    )
    add_footer(slide, "Section 5 | Methods")

    # 9. Why this method mix
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Why This Method Mix")
    add_card(
        slide,
        0.65,
        2.0,
        5.95,
        4.8,
        "Why not follower-count only",
        [
            "Misses campaign-language fit",
            "Misses network position and community overlap",
            "Misses quality/reliability signals",
            "High chance of expensive creator mismatch",
        ],
    )
    add_card(
        slide,
        6.72,
        2.0,
        5.95,
        4.8,
        "Hybrid ranking logic",
        [
            "Network influence + text fit + engagement potential",
            "Reliability multiplier to penalize low-signal channels",
            "Diversity constraint for healthier final shortlist",
            "More robust than single-signal ranking",
        ],
    )
    add_footer(slide, "Section 5 | Method Choice Rationale")

    # 10. Model results
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Model Results and Validation")
    slide.shapes.add_picture(str(image_path("model_benchmark_rmse.png")), Inches(0.78), Inches(2.0), height=Inches(4.85))
    add_card(
        slide,
        8.0,
        2.0,
        4.45,
        4.85,
        f"Best model: {best_model}",
        [
            f"Best RMSE: {best_rmse:.5f}",
            f"Baseline RMSE: {baseline_rmse:.5f}",
            f"Relative RMSE reduction: {gain_pct:.1f}%",
            "Interpretation: meaningful uplift over naive baseline",
        ],
    )
    add_footer(slide, "Section 5 | Validation Output")

    # 11. Demo and use cases
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Prototype Demo: Input to Output")
    slide.shapes.add_picture(str(image_path("top10_final_scores.png")), Inches(7.0), Inches(2.1), width=Inches(5.5))
    add_bullets(
        slide,
        0.8,
        2.0,
        6.0,
        4.9,
        [
            "Live flow: campaign input -> Top-N shortlist -> rationale/risk",
            "Interactive tabs: Network, Text Intelligence, ML, ROI",
            "Use case A: BOJ sunscreen launch planning",
            "Use case B: CeraVe benchmark for shortlist calibration",
            "Decision output: ranked creators + risk notes + memo export",
        ],
        font_size=17,
    )
    add_footer(slide, "Section 6 | Live Demo")

    # 12. Impact
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Business Impact")
    add_card(
        slide,
        0.68,
        2.0,
        6.0,
        4.8,
        "How this helps the client",
        [
            "Faster influencer shortlisting and campaign planning",
            "Transparent recommendation logic for stakeholder trust",
            "Reduced mismatch risk before spending budget",
            "Scenario-based ROI planning and expectation setting",
        ],
    )
    add_card(
        slide,
        6.75,
        2.0,
        5.9,
        4.8,
        "Decisions improved",
        [
            "Who to prioritize in outreach",
            "How many creators to activate by objective",
            "How much budget risk is acceptable",
            f"Base ROI scenario in run: {float(roi.get('roas', 0)):.2f}x expected ROAS",
        ],
    )
    add_footer(slide, "Section 7 | Business Value")

    # 13. Limitations and next steps
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Limitations, Ethics, and Next Steps")
    add_card(
        slide,
        0.7,
        2.0,
        5.95,
        4.8,
        "Current limitations",
        [
            "Pre-collected YouTube dataset (not live cross-platform feed)",
            "ROI is scenario estimate, not causal proof",
            "Remaining cluster concentration in skincare niches",
            "Need larger-scale operational monitoring",
        ],
    )
    add_card(
        slide,
        6.75,
        2.0,
        5.95,
        4.8,
        "Ethics and roadmap",
        [
            "Bias checks: degree-overlap diagnostics + evidence penalty",
            "Privacy: no sensitive personal profiling in prototype",
            "Next: live connectors + fairness constraints + pilot calibration",
            "Target: weekly decision-support workflow for brand teams",
        ],
    )
    add_footer(slide, "Section 7 | Caveats and Roadmap")

    # 14. AI tools usage
    slide = prs.slides.add_slide(blank)
    add_title(slide, "How We Used AI Tools")
    add_card(
        slide,
        0.7,
        2.0,
        5.95,
        4.75,
        "Where AI tools helped",
        [
            "Ideation and scope refinement",
            "Implementation acceleration and debugging",
            "Documentation and memo drafting",
            "Slide polishing and presentation prep",
        ],
    )
    add_card(
        slide,
        6.75,
        2.0,
        5.95,
        4.75,
        "Human responsibility",
        [
            "Problem framing and business assumptions",
            "Model choice, validation, and guardrail design",
            "Result interpretation and recommendation decisions",
            "Final accountability stayed with the team",
        ],
    )
    add_footer(slide, "Section 8 | AI Tooling Disclosure")

    # 15. References and Q&A
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Conclusion, References, and Q&A")
    add_bullets(
        slide,
        0.82,
        2.0,
        12.0,
        3.9,
        [
            "Conclusion: AI-MCN can reduce manual MCN dependence and improve influencer decision quality.",
            "EMARKETER (Mar 13, 2025): US influencer spend and YouTube marketer adoption",
            "NIQ (Feb 25, 2025): beauty growth and e-commerce/social commerce indicators",
            "McKinsey (Aug 28, 2025): beauty market outlook to 2030",
            "Fashionista (Nov 13, 2024): BOJ virality and U.S. market context",
            "Technical refs: YouTube API, scikit-learn, LightGBM, SHAP, Streamlit",
        ],
        font_size=16,
    )
    q = slide.shapes.add_textbox(Inches(0.82), Inches(6.1), Inches(11.8), Inches(0.8))
    qp = q.text_frame.paragraphs[0]
    qp.text = "Thank you. Q&A"
    qp.font.size = Pt(30)
    qp.font.bold = True
    qp.font.name = "Aptos Display"
    qp.font.color.rgb = RGBColor(16, 86, 150)
    qp.alignment = PP_ALIGN.CENTER
    add_footer(slide, "AI-MCN | MSIS 521")

    prs.save(str(OUT_PPTX))
    return OUT_PPTX


if __name__ == "__main__":
    out = build()
    print(out)
