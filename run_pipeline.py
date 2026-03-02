from __future__ import annotations

import argparse
import json
import warnings

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AI-MCN pipeline.")
    parser.add_argument("--ml", action="store_true", help="Enable ML benchmarking block (slower).")
    parser.add_argument(
        "--ml-models",
        type=str,
        default="",
        help="Comma-separated models when --ml is enabled (e.g., LinearRegression,LASSO,Ridge,CART,RandomForest,LightGBM).",
    )
    parser.add_argument("--no-benchmark", action="store_true", help="Skip CeraVe benchmark run.")
    return parser.parse_args()


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=Warning, message=".*urllib3 v2 only supports OpenSSL.*")
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    from src.orchestrator import run_pipeline

    args = parse_args()
    ml_models = [x.strip() for x in args.ml_models.split(",") if x.strip()] if args.ml_models else None
    result = run_pipeline(run_ml=args.ml, run_benchmark=not args.no_benchmark, ml_models=ml_models)
    summary = {
        "timestamp_utc": result["timestamp_utc"],
        "top_channels": result["top5_df"]["channel_title"].tolist(),
        "best_model": result["ml_best_model"],
        "benchmark": result.get("benchmark_summary", {}),
        "artifacts": result.get("artifact_paths", {}),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
