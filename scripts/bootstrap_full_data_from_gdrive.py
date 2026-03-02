from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import DATA_DIR
from src.data_bootstrap import ensure_full_data_from_gdrive


if __name__ == "__main__":
    report = ensure_full_data_from_gdrive(Path(DATA_DIR))
    print(json.dumps(report, indent=2, ensure_ascii=False))
