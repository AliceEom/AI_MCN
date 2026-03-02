from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def min_max_scale(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").fillna(0.0)
    vmin = float(s.min())
    vmax = float(s.max())
    if math.isclose(vmin, vmax):
        return pd.Series(np.zeros(len(s), dtype=float), index=s.index)
    return (s - vmin) / (vmax - vmin)


def parse_tags(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    text = str(value).strip()
    if not text:
        return []

    if text.startswith("[") and text.endswith("]"):
        try:
            data = json.loads(text.replace("'", '"'))
            if isinstance(data, list):
                return [str(x).strip().lower() for x in data if str(x).strip()]
        except Exception:
            pass

    # Fallback split for malformed list strings.
    text = re.sub(r"^[\[\(]|[\]\)]$", "", text)
    parts = re.split(r",|\|", text)
    return [p.strip().strip("'\"").lower() for p in parts if p.strip()]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def join_non_empty(parts: Iterable[Any], sep: str = " ") -> str:
    cleaned = [normalize_text(p) for p in parts if p is not None and str(p).strip()]
    return sep.join(cleaned).strip()


def safe_log1p(series: pd.Series) -> pd.Series:
    return np.log1p(pd.to_numeric(series, errors="coerce").clip(lower=0).fillna(0.0))


def build_hash_key(*parts: Any) -> str:
    joined = "||".join([str(p) for p in parts])
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
