# AI-MCN Submission Package (Colab-Friendly)

This folder is a submission-ready Python package for the course project.
It contains the full code used for:
- data preparation and cleaning
- network analysis
- text analysis
- ML benchmarking and explainability
- ranking and recommendation
- visualization and reporting

All comments and notes are written in English for clear grading and review.

---

## 1) Folder structure

```text
submission_colab_python/
  ai_mcn_submission/
    config.py
    data_bootstrap.py
    data_prep.py
    network_scoring.py
    text_scoring.py
    semantic_enrichment.py
    ml_modeling.py
    ranking.py
    visualization.py
    roi_simulation.py
    channel_details.py
    channel_media.py
    content_generation.py
    orchestrator.py
    utils.py
  run_submission_pipeline.py
  colab_walkthrough.py
  requirements_colab.txt
  data/.gitkeep
```

---

## 2) What each major file does

- `data_prep.py`
  - Loads raw CSV files
  - Removes duplicates
  - Cleans numeric/date fields
  - Applies include/exclude filters
  - Aggregates channel-level features

- `network_scoring.py`
  - Builds creator graph from shared tags
  - Computes centrality features
  - Detects communities
  - Produces network influence score

- `text_scoring.py`
  - Builds campaign brief object
  - Computes TF-IDF text similarity
  - Applies keyword boost/penalty

- `semantic_enrichment.py`
  - Enriches top candidates with semantic/tone alignment
  - Generates red flags and rationale strings

- `ml_modeling.py`
  - Runs supervised regression benchmark:
    - LinearRegression, LASSO, Ridge, CART, RandomForest, LightGBM
  - Uses 5-fold GroupKFold CV
  - Adds baseline comparison
  - Produces SHAP outputs (if available)

- `ranking.py`
  - Computes final hybrid score
  - Applies reliability multiplier
  - Applies diversity-aware Top-N selection

- `visualization.py`
  - Builds project figures (model benchmark, score breakdown, network, community, ROI funnel)

- `orchestrator.py`
  - Runs the full end-to-end pipeline and returns one structured result object

- `colab_walkthrough.py`
  - Step-by-step helper functions for notebook demos and grading

- `run_submission_pipeline.py`
  - CLI entry point to execute the full pipeline in one command

---

## 3) Colab setup instructions

## 3.1 Upload files

Upload the entire `submission_colab_python` folder to Colab (or Google Drive mounted in Colab).

## 3.2 Install dependencies

```python
!pip install -r requirements_colab.txt
```

## 3.3 Place data files

Put these three files in `submission_colab_python/data/`:
- `videos_text_ready_combined.csv`
- `comments_raw_combined.csv`
- `master_prd_slim_combined.csv`

Optional:
- If combined files are not available, demo files can be used:
  - `videos_text_ready_demo.csv`
  - `comments_raw_demo.csv`
  - `master_prd_slim_demo.csv`

## 3.4 Run full pipeline

```python
!python run_submission_pipeline.py --ml
```

For faster run:

```python
!python run_submission_pipeline.py
```

---

## 4) Step-by-step notebook workflow (recommended for presentation)

In Colab:

```python
from colab_walkthrough import (
    run_data_preparation_step,
    run_network_step,
    run_text_step,
    run_ml_step,
    run_full_pipeline_step,
    render_core_figures,
)
```

Suggested sequence:
1. `run_data_preparation_step()`
2. `run_network_step(...)`
3. `run_text_step(...)`
4. `run_ml_step(...)`
5. `run_full_pipeline_step(...)`
6. `render_core_figures(...)`

This gives a clear, audit-friendly progression from raw data to final recommendation.

---

## 5) Notes for evaluation

- The code prioritizes transparent logic over black-box behavior.
- Ranking is multi-signal and includes reliability controls.
- ML contribution is gated by CV performance against baseline.
- Outputs include both quantitative metrics and qualitative rationale.

