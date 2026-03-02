from __future__ import annotations

"""
Build a single-file submission script that contains all core analysis/modeling code.

Output:
  submission_colab_python/AI_MCN_Submission_AllInOne.py
"""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_DIR = ROOT / "submission_colab_python"
PKG_DIR = SUBMISSION_DIR / "ai_mcn_submission"
OUT_FILE = SUBMISSION_DIR / "AI_MCN_Submission_AllInOne.py"


MODULE_ORDER = [
    "utils.py",
    "config.py",
    "analysis_categories.py",
    "data_bootstrap.py",
    "data_prep.py",
    "network_scoring.py",
    "text_scoring.py",
    "semantic_enrichment.py",
    "ml_modeling.py",
    "ranking.py",
    "roi_simulation.py",
    "channel_details.py",
    "channel_media.py",
    "content_generation.py",
    "orchestrator.py",
]


HEADER = """\
# -*- coding: utf-8 -*-
\"\"\"
AI-MCN Submission (All-in-One Python File)
=========================================

Purpose
-------
This file combines all core project code into a single Python script for course submission.
It includes:
- data preparation and cleaning
- text analysis (including TF-IDF)
- social network analysis (degree, betweenness proxy, eigenvector proxy, communities)
- ML benchmarking (LinearRegression, LASSO, Ridge, CART, RandomForest, LightGBM)
- SHAP explainability
- hybrid ranking and reliability controls
- ROI calculator and simulation
- benchmark, strategy, memo, and export-ready outputs

Main workflow
-------------
1) Load data (combined first, demo fallback; optional Google Drive bootstrap)
2) Clean and aggregate video/comment data into channel-level features
3) Build network graph and compute SNA signals
4) Compute text relevance and semantic/tone enrichment
5) Optionally run ML benchmark and generate ML potential score
6) Produce final recommendation score with reliability and diversity controls
7) Build benchmark/ROI/strategy/memo outputs

Quick run examples
------------------
Fast run:
    python AI_MCN_Submission_AllInOne.py --no-benchmark

Full run with ML:
    python AI_MCN_Submission_AllInOne.py --ml

\"\"\"

from __future__ import annotations
"""


FOOTER = """

# ---------------------------------------------------------------------------
# Submission CLI entry point
# ---------------------------------------------------------------------------
def _submission_parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Run AI-MCN all-in-one submission pipeline.")
    parser.add_argument("--ml", action="store_true", help="Enable ML benchmark block.")
    parser.add_argument(
        "--ml-models",
        type=str,
        default="",
        help="Comma-separated model names (used when --ml is enabled).",
    )
    parser.add_argument("--no-benchmark", action="store_true", help="Skip benchmark run.")
    return parser.parse_args()


def _submission_main() -> None:
    import json
    from pathlib import Path

    args = _submission_parse_args()
    ml_models = [x.strip() for x in args.ml_models.split(",") if x.strip()] if args.ml_models else None

    result = run_pipeline(
        run_ml=args.ml,
        run_benchmark=not args.no_benchmark,
        ml_models=ml_models,
    )

    topn = result.get("top5_df", None)
    top_channels = []
    if topn is not None and hasattr(topn, "columns") and "channel_title" in topn.columns:
        top_channels = topn["channel_title"].tolist()

    data_sources = result.get("data_sources", {})
    summary = {
        "timestamp_utc": result.get("timestamp_utc"),
        "data_sources": {
            "videos_csv": str(Path(str(data_sources.get("videos_csv", ""))).name),
            "comments_csv": str(Path(str(data_sources.get("comments_csv", ""))).name),
            "master_csv": str(Path(str(data_sources.get("master_csv", ""))).name),
        },
        "top_channels": top_channels,
        "best_model": result.get("ml_best_model", "N/A"),
        "benchmark": result.get("benchmark_summary", {}),
        "artifacts": result.get("artifact_paths", {}),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _submission_main()
"""


def _strip_relative_imports(code: str) -> str:
    lines = []
    for line in code.splitlines():
        if line.startswith("from ."):
            continue
        if line.strip() == "from __future__ import annotations":
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def build() -> Path:
    parts: list[str] = [HEADER.rstrip(), ""]

    for name in MODULE_ORDER:
        src = PKG_DIR / name
        if not src.exists():
            raise FileNotFoundError(f"Missing source module: {src}")

        code = src.read_text(encoding="utf-8")
        code = _strip_relative_imports(code)

        # Make submission package self-contained under submission_colab_python/
        if name == "config.py":
            code = code.replace(
                "BASE_DIR = Path(__file__).resolve().parents[1]",
                "BASE_DIR = Path(__file__).resolve().parent",
            )
            # Keep backward compatibility with previous artifacts location if needed.
            code = code.replace(
                "ARTIFACTS_DIR = BASE_DIR / \"artifacts\"",
                "ARTIFACTS_DIR = BASE_DIR / \"artifacts\"",
            )

        section_title = f"# ===== Begin {name} ====="
        parts.append(section_title)
        parts.append(code.rstrip())
        parts.append(f"# ===== End {name} =====")
        parts.append("")

    parts.append(FOOTER.rstrip())
    OUT_FILE.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return OUT_FILE


if __name__ == "__main__":
    out = build()
    print(out)

