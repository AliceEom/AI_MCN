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

## Using full data from Google Drive (Cloud-friendly)

If your full `*_combined.csv` files are already on Google Drive, set these secrets/env vars.

Option A (single folder link):

- `GDRIVE_FOLDER_URL` (or `GDRIVE_FOLDER_ID`)

Option B (individual file links):

- `GDRIVE_VIDEOS_FILE_ID` (or `GDRIVE_VIDEOS_URL`)
- `GDRIVE_COMMENTS_FILE_ID` (or `GDRIVE_COMMENTS_URL`)
- `GDRIVE_MASTER_FILE_ID` (or `GDRIVE_MASTER_URL`)

Template:
- `.streamlit/secrets.example.toml`

The pipeline will automatically try to download:

- `data/videos_text_ready_combined.csv`
- `data/comments_raw_combined.csv`
- `data/master_prd_slim_combined.csv`

on startup. If download is successful, full data is used automatically.

You can also test bootstrap manually:

```bash
python scripts/bootstrap_full_data_from_gdrive.py
```

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
- If `GDRIVE_*` ids/urls are set, full combined CSVs are auto-downloaded when missing.
- LightGBM and SHAP are used automatically when their packages are available in the runtime.
- All core artifacts are saved under `artifacts/`.
