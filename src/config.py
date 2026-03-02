from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
CACHE_DIR = ARTIFACTS_DIR / "cache"
PLOTS_DIR = ARTIFACTS_DIR / "plots"
MODELS_DIR = ARTIFACTS_DIR / "models"
REPORTS_DIR = ARTIFACTS_DIR / "reports"


def _prefer_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


VIDEOS_CSV = _prefer_existing(
    DATA_DIR / "videos_text_ready_combined.csv",
    DATA_DIR / "videos_text_ready_demo.csv",
)
COMMENTS_CSV = _prefer_existing(
    DATA_DIR / "comments_raw_combined.csv",
    DATA_DIR / "comments_raw_demo.csv",
)
MASTER_CSV = _prefer_existing(
    DATA_DIR / "master_prd_slim_combined.csv",
    DATA_DIR / "master_prd_slim_demo.csv",
)


@dataclass(frozen=True)
class PipelineConfig:
    random_state: int = 42
    tfidf_max_features: int = 1200
    svd_components: int = 50
    ml_max_rows: int = 3000
    top_candidates_for_semantic: int = 30
    top_recommendations: int = 10
    min_shared_tags_edge: int = 2
    max_tag_channel_ratio: float = 0.20
    min_community_size: int = 3


DEFAULT_CONFIG = PipelineConfig()
