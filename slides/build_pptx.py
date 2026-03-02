from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
SLIDES_DIR = ROOT / "slides"
ASSETS_DIR = SLIDES_DIR / "assets"
SUMMARY_JSON = ROOT / "artifacts" / "reports" / "presentation_summary_boj.json"
OUT_PPTX = SLIDES_DIR / "AI_MCN_Final_Presentation_EN.pptx"


def add_title(
    slide,
    title: str,
    subtitle: str | None = None,
    accent: bool = True,
) -> None:
    title_box = slide.shapes.add_textbox(Inches(0.65), Inches(0.35), Inches(12.1), Inches(1.0))
    tf = title_box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(34)
    p.font.bold = True
    p.font.name = "Aptos Display"
    p.font.color.rgb = RGBColor(15, 44, 89)

    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.72), Inches(1.3), Inches(11.8), Inches(0.65))
        stf = sub_box.text_frame
        stf.clear()
        sp = stf.paragraphs[0]
        sp.text = subtitle
        sp.font.size = Pt(16)
        sp.font.name = "Aptos"
        sp.font.color.rgb = RGBColor(74, 95, 128)

    if accent:
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.62), Inches(1.95), Inches(2.6), Inches(0.08))
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
    font_size: int = 22,
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
        p.space_after = Pt(9)


def add_card(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    title: str,
    bullets: list[str],
) -> None:
    rect = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor(242, 247, 252)
    rect.line.color.rgb = RGBColor(205, 220, 238)
    rect.line.width = Pt(1.25)

    title_box = slide.shapes.add_textbox(Inches(left + 0.22), Inches(top + 0.12), Inches(width - 0.35), Inches(0.4))
    ttf = title_box.text_frame
    ttf.clear()
    tp = ttf.paragraphs[0]
    tp.text = title
    tp.font.bold = True
    tp.font.size = Pt(19)
    tp.font.color.rgb = RGBColor(19, 58, 102)
    tp.font.name = "Aptos"

    add_bullets(
        slide,
        left=left + 0.2,
        top=top + 0.52,
        width=width - 0.35,
        height=height - 0.62,
        bullets=bullets,
        font_size=16,
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


def build() -> Path:
    if not SUMMARY_JSON.exists():
        raise FileNotFoundError(f"Missing summary file: {SUMMARY_JSON}")
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))

    top10 = summary.get("top10", [])
    roi = summary.get("roi", {})
    bench = summary.get("benchmark", {})
    dataset = summary.get("dataset", {})
    bias = summary.get("bias_report", {})
    ml_table = summary.get("ml_table", [])

    best_model = summary.get("ml_best_model", "N/A")
    baseline_rmse = next((x.get("rmse_mean", 0.0) for x in ml_table if x.get("model") == "BaselineMedian"), 0.0)
    best_rmse = next((x.get("rmse_mean", 0.0) for x in ml_table if x.get("model") == best_model), 0.0)
    gain_pct = 0.0
    if baseline_rmse and best_rmse:
        gain_pct = (baseline_rmse - best_rmse) / baseline_rmse * 100.0

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # 1
    slide = prs.slides.add_slide(blank)
    add_title(
        slide,
        "AI-MCN: AI-Augmented Influencer Matching for Beauty Campaigns",
        "MSIS 521 Course Project | Team Presentation (15 minutes)",
    )
    add_bullets(
        slide,
        0.72,
        2.2,
        11.9,
        2.8,
        [
            "Case: Beauty of Joseon (BOJ), U.S. sunscreen campaign scenario",
            "Prototype: Streamlit app + modular Python AI pipeline",
            "Output: Top-N recommendations, model benchmark, explainability, ROI simulator, memo",
        ],
        font_size=24,
    )
    add_footer(slide, "AI-MCN | MSIS 521")

    # 2
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Problem and Scope")
    add_card(
        slide,
        0.65,
        2.0,
        5.95,
        4.7,
        "Business Problem",
        [
            "Influencer discovery is often manual, slow, and popularity-biased.",
            "Teams need transparent, evidence-based creator selection.",
            "Campaign planning needs measurable support, not only intuition.",
        ],
    )
    add_card(
        slide,
        6.72,
        2.0,
        5.95,
        4.7,
        "Scope Discipline",
        [
            "In-scope: end-to-end matching prototype and live demo.",
            "Out-of-scope: full production MLOps and multi-platform live ingestion.",
            "Quarter-feasible scope with meaningful technical depth.",
        ],
    )
    add_footer(slide, "Rubric 1: Topic choice, scope, interest")

    # 3
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Assignment Requirements Check")
    rows = [
        ("Pick a problem and client", "BOJ influencer matching scenario"),
        ("Collect/obtain data", "Team-collected YouTube videos/channels/comments"),
        ("Prototype in Python", "Streamlit + AI pipeline modules"),
        ("Present process + story + demo", "This deck + live app walkthrough"),
    ]
    table = slide.shapes.add_table(len(rows) + 1, 2, Inches(0.8), Inches(2.0), Inches(11.9), Inches(3.9)).table
    table.columns[0].width = Inches(4.4)
    table.columns[1].width = Inches(7.5)
    table.cell(0, 0).text = "Assignment Requirement"
    table.cell(0, 1).text = "Our Implementation"
    for i, (a, b) in enumerate(rows, start=1):
        table.cell(i, 0).text = a
        table.cell(i, 1).text = b
    for r in range(len(rows) + 1):
        for c in range(2):
            cell = table.cell(r, c)
            for p in cell.text_frame.paragraphs:
                p.font.name = "Aptos"
                p.font.size = Pt(14 if r else 15)
                p.font.bold = r == 0
                p.font.color.rgb = RGBColor(17, 34, 63)
    add_footer(slide, "Assignment deliverables: code + slides")

    # 4
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Data Overview (BOJ Run)")
    kpis = [
        ("Videos analyzed", f"{int(dataset.get('videos_analyzed', 0)):,}"),
        ("Channels scored", f"{int(dataset.get('channels_scored', 0)):,}"),
        ("Default recommendations", "Top-10"),
        ("Non-micro communities", "6"),
    ]
    x = 0.75
    for label, val in kpis:
        rect = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.25), Inches(2.95), Inches(1.55))
        rect.fill.solid()
        rect.fill.fore_color.rgb = RGBColor(235, 245, 255)
        rect.line.color.rgb = RGBColor(188, 212, 239)
        vbox = slide.shapes.add_textbox(Inches(x + 0.15), Inches(2.45), Inches(2.65), Inches(0.56))
        vp = vbox.text_frame.paragraphs[0]
        vp.text = val
        vp.font.name = "Aptos Display"
        vp.font.bold = True
        vp.font.size = Pt(26)
        vp.font.color.rgb = RGBColor(21, 96, 162)
        lbox = slide.shapes.add_textbox(Inches(x + 0.15), Inches(3.05), Inches(2.65), Inches(0.4))
        lp = lbox.text_frame.paragraphs[0]
        lp.text = label
        lp.font.name = "Aptos"
        lp.font.size = Pt(12)
        lp.font.color.rgb = RGBColor(59, 87, 126)
        x += 3.15
    add_bullets(
        slide,
        0.8,
        4.2,
        12.0,
        2.1,
        [
            "Input files: videos_text_ready_combined.csv, comments_raw_combined.csv, master_prd_slim_combined.csv",
            "Campaign input: BOJ SPF + Glow Serum, U.S. market, sensitive-skin audience, $50,000 budget",
        ],
        font_size=15,
    )
    add_footer(slide, "Data-driven prototype with fixed reproducible input")

    # 5
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Method Pipeline")
    add_bullets(
        slide,
        0.75,
        2.0,
        12.0,
        4.9,
        [
            "1) Data cleaning + beauty/noise filter",
            "2) Channel aggregation and text profile generation",
            "3) Network scoring (centrality + community detection)",
            "4) TF-IDF relevance + semantic/tone enrichment",
            "5) Evidence guardrail + diversity-aware ranking",
            "6) ML benchmark (Linear/LASSO/Ridge/CART/RF/LightGBM, GroupKFold 5-fold)",
            "7) ROI simulation + strategy generation + executive memo",
        ],
        font_size=19,
    )
    add_footer(slide, "Rubric 3: Technical aspects and method choice")

    # 6
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Model Evaluation Results")
    slide.shapes.add_picture(str(image_path("model_benchmark_rmse.png")), Inches(0.8), Inches(2.0), height=Inches(4.7))
    add_card(
        slide,
        8.0,
        2.0,
        4.5,
        4.7,
        f"Best model: {best_model}",
        [
            f"Best RMSE: {best_rmse:.5f}",
            f"Baseline RMSE: {baseline_rmse:.5f}",
            f"RMSE reduction vs baseline: {gain_pct:.1f}%",
            "Group-based CV used to reduce channel leakage risk",
        ],
    )
    add_footer(slide, "6 models compared under the same CV protocol")

    # 7
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Explainability (SHAP)")
    slide.shapes.add_picture(str(image_path("shap_summary_LightGBM.png")), Inches(0.75), Inches(2.0), height=Inches(4.8))
    add_card(
        slide,
        7.95,
        2.0,
        4.6,
        4.8,
        "Why SHAP matters",
        [
            "Shows which features drive engagement predictions.",
            "Improves trust for non-technical stakeholders.",
            "Helps diagnose unstable or misleading signals.",
        ],
    )
    add_footer(slide, "Rubric 3: Evaluation and sanity checking")

    # 8
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Top-10 BOJ Recommendations")
    slide.shapes.add_picture(str(image_path("top10_final_scores.png")), Inches(0.72), Inches(2.0), height=Inches(4.95))
    top3 = [r["channel_title"] for r in top10[:3]] if top10 else []
    t = ", ".join(top3) if top3 else "N/A"
    add_footer(slide, f"Top 3 channels: {t}")

    # 9
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Guardrails Against Bad Recommendations")
    slide.shapes.add_picture(str(image_path("evidence_vs_finalscore_top10.png")), Inches(0.75), Inches(2.0), height=Inches(4.85))
    overlap = int(bias.get("degree_top_overlap", 0))
    topn = int(bias.get("top_n", 10))
    add_card(
        slide,
        8.03,
        2.0,
        4.45,
        4.85,
        "Bias and quality controls",
        [
            "Low-evidence channels are automatically down-weighted.",
            "Diversity guardrail prevents single-cluster over-concentration.",
            f"Degree-only vs hybrid overlap: {overlap}/{topn}",
        ],
    )
    add_footer(slide, "Reduced popularity bias with evidence-based filtering")

    # 10
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Network Diversity Diagnostics")
    slide.shapes.add_picture(str(image_path("community_distribution_clean.png")), Inches(0.75), Inches(2.0), height=Inches(4.8))
    add_card(
        slide,
        8.0,
        2.0,
        4.5,
        4.8,
        "Community results",
        [
            "Non-micro communities discovered: 6",
            "Largest non-micro community share: 43.8%",
            "Micro/isolated channels separated to improve readability",
        ],
    )
    add_footer(slide, "Community-aware matching for healthier shortlist diversity")

    # 11
    slide = prs.slides.add_slide(blank)
    add_title(slide, "ROI Scenario (Business Lens)")
    slide.shapes.add_picture(str(image_path("roi_funnel_base.png")), Inches(0.75), Inches(2.0), height=Inches(4.9))
    add_card(
        slide,
        7.85,
        2.0,
        4.65,
        4.9,
        "Base scenario outputs",
        [
            f"Budget: ${int(roi.get('budget_usd', 0)):,}",
            f"Impressions: {int(roi.get('impressions', 0)):,}",
            f"Clicks: {int(roi.get('clicks', 0)):,}",
            f"Conversions: {int(roi.get('conversions', 0)):,}",
            f"Expected ROAS: {float(roi.get('roas', 0)):.2f}x",
        ],
    )
    add_footer(slide, "Scenario estimate only, not causal guarantee")

    # 12
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Live Demo Flow")
    add_bullets(
        slide,
        0.8,
        2.1,
        12.0,
        4.7,
        [
            "1) Enter campaign input (brand/product/audience/keywords/budget)",
            "2) Run analysis and show analyzing workflow",
            "3) Inspect Top-N cards with rationale and evidence",
            "4) Change ranking strategy and diversity controls",
            "5) Explore Text Intelligence and Network Studio",
            "6) Review ML Studio (model comparison + SHAP)",
            "7) Adjust ROI assumptions and export memo",
        ],
        font_size=19,
    )
    add_footer(slide, "Rubric 4: Demo clarity and storytelling flow")

    # 13
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Limitations and Future Work")
    add_card(
        slide,
        0.7,
        2.0,
        5.95,
        4.8,
        "Current limitations",
        [
            "Prototype uses pre-collected YouTube data.",
            "ROI module is scenario simulation, not causal inference.",
            "Cluster concentration still exists in skincare-heavy niches.",
        ],
    )
    add_card(
        slide,
        6.75,
        2.0,
        5.95,
        4.8,
        "Next steps",
        [
            "Add live market and competitor enrichment.",
            "Expand to TikTok/Instagram connectors.",
            "Introduce experiment loop for closed-loop learning.",
        ],
    )
    add_footer(slide, "Honest caveats + practical roadmap")

    # 14
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Rubric Alignment (Target: 9-10)")
    rows = [
        ("Topic choice, scope, interest", "Clear marketing problem, creative hybrid AI scope, feasible for course timeline"),
        ("Potential impact and relevance", "Directly supports influencer and budget decisions for brand teams"),
        ("Technical aspects of prototype", "Working end-to-end app, 6-model benchmark, SHAP, bias diagnostics"),
        ("Presentation quality/storytelling", "Context -> method -> evidence -> demo -> impact narrative with visuals"),
    ]
    table = slide.shapes.add_table(len(rows) + 1, 2, Inches(0.78), Inches(2.0), Inches(11.95), Inches(4.95)).table
    table.columns[0].width = Inches(4.0)
    table.columns[1].width = Inches(7.95)
    table.cell(0, 0).text = "Rubric Criterion"
    table.cell(0, 1).text = "Project Evidence"
    for i, (a, b) in enumerate(rows, start=1):
        table.cell(i, 0).text = a
        table.cell(i, 1).text = b
    for r in range(len(rows) + 1):
        for c in range(2):
            cell = table.cell(r, c)
            for p in cell.text_frame.paragraphs:
                p.font.name = "Aptos"
                p.font.size = Pt(13 if r else 14)
                p.font.bold = r == 0
                p.font.color.rgb = RGBColor(20, 38, 66)
    add_footer(slide, "Directly mapped to MSIS 521 project rubric")

    # 15
    slide = prs.slides.add_slide(blank)
    add_title(slide, "15-Minute Delivery Plan")
    add_bullets(
        slide,
        0.9,
        2.1,
        11.8,
        3.6,
        [
            "0:00-2:00 Problem and scope",
            "2:00-5:30 Data and method pipeline",
            "5:30-8:30 Evaluation and explainability",
            "8:30-12:30 Live demo",
            "12:30-14:00 Impact, caveats, roadmap",
            "14:00-15:00 Q&A",
        ],
        font_size=21,
    )
    add_card(
        slide,
        0.9,
        5.8,
        11.8,
        1.0,
        "Speaking split suggestion",
        ["Speaker A: business context | Speaker B: technical pipeline | Speaker C: demo + impact + Q&A"],
    )
    add_footer(slide, "Time and role clarity improves delivery score")

    # 16
    slide = prs.slides.add_slide(blank)
    add_title(slide, "References and Q&A")
    add_bullets(
        slide,
        0.9,
        2.1,
        11.8,
        3.7,
        [
            "MSIS 521 assignment brief and evaluation rubric (Canvas)",
            "YouTube Data API documentation",
            "scikit-learn documentation (regression, tree models, GroupKFold)",
            "LightGBM documentation",
            "SHAP documentation",
            "Streamlit documentation",
        ],
        font_size=19,
    )
    q = slide.shapes.add_textbox(Inches(0.9), Inches(6.0), Inches(11.5), Inches(0.8))
    qp = q.text_frame.paragraphs[0]
    qp.text = "Thank you. Questions?"
    qp.font.size = Pt(30)
    qp.font.bold = True
    qp.font.name = "Aptos Display"
    qp.font.color.rgb = RGBColor(16, 86, 150)
    qp.alignment = PP_ALIGN.CENTER
    add_footer(slide, "AI-MCN team")

    prs.save(str(OUT_PPTX))
    return OUT_PPTX


if __name__ == "__main__":
    out = build()
    print(out)

