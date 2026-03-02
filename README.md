# AI-MCN Prototype

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py
# Optional full ML benchmark run:
python run_pipeline.py --ml
streamlit run app.py
```

## Demo Data for GitHub / Streamlit Cloud

This repo supports two data modes:
- Full local data: `data/*_combined.csv` (large, not pushed to GitHub).
- Cloud/demo data: `data/*_demo.csv` (lightweight, tracked in GitHub).

The app and pipeline automatically prefer full files when available, and fall back to demo files otherwise.

To regenerate demo snapshots from local full data:

```bash
python scripts/generate_demo_data.py
```

## Notes
- Demo UI is English-only.
- `run_pipeline.py` defaults to a fast run (ML block off). Use `--ml` to enable full model benchmarking.
- You can choose ML model subsets using `--ml-models`.
  - Example: `python run_pipeline.py --ml --ml-models LinearRegression,LASSO,Ridge,CART,RandomForest,LightGBM`
- If `YOUTUBE_API_KEY` is set, channel images use channel thumbnails.
- If `OPENAI_API_KEY` is set, content strategy generation can use LLM; otherwise template fallback is used.
- LightGBM and SHAP are used automatically when their packages are available in the runtime.
- All core artifacts are saved under `artifacts/`.
