from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_mcn_submission.orchestrator import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the AI-MCN submission pipeline (Colab-friendly entry point)."
    )
    parser.add_argument(
        "--ml",
        action="store_true",
        help="Enable the ML benchmark block (slower but complete).",
    )
    parser.add_argument(
        "--ml-models",
        type=str,
        default="",
        help="Comma-separated model names for ML run.",
    )
    parser.add_argument(
        "--no-benchmark",
        action="store_true",
        help="Disable anchor-vs-benchmark comparison run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ml_models = [x.strip() for x in args.ml_models.split(",") if x.strip()] if args.ml_models else None

    result = run_pipeline(
        run_ml=args.ml,
        run_benchmark=not args.no_benchmark,
        ml_models=ml_models,
    )

    topn = result["top5_df"].copy()
    data_sources = result.get("data_sources", {})
    summary = {
        "timestamp_utc": result["timestamp_utc"],
        "data_sources": {
            "videos_csv": str(Path(str(data_sources.get("videos_csv", ""))).name),
            "comments_csv": str(Path(str(data_sources.get("comments_csv", ""))).name),
            "master_csv": str(Path(str(data_sources.get("master_csv", ""))).name),
        },
        "top_channels": topn.get("channel_title", []).tolist() if "channel_title" in topn.columns else [],
        "best_model": result.get("ml_best_model", "N/A"),
        "benchmark": result.get("benchmark_summary", {}),
        "artifacts": result.get("artifact_paths", {}),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

