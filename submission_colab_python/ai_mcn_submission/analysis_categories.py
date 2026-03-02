from __future__ import annotations

"""
Canonical analysis/modeling taxonomy used in the submission package.

This module groups all implemented methods into large categories so
reviewers can understand the project structure at a glance.
"""

from typing import Any

import pandas as pd


ANALYSIS_CATEGORIES: list[dict[str, Any]] = [
    {
        "category": "Analysis: Class Concepts",
        "method": "Text analysis",
        "implemented": True,
        "class_concept": True,
        "description": "Campaign-language relevance and semantic interpretation from creator text.",
        "primary_files": ["text_scoring.py", "semantic_enrichment.py", "app.py"],
    },
    {
        "category": "Analysis: Class Concepts",
        "method": "TF-IDF",
        "implemented": True,
        "class_concept": True,
        "description": "TF-IDF vectorization + cosine similarity between campaign brief and channel text.",
        "primary_files": ["text_scoring.py"],
    },
    {
        "category": "Analysis: Class Concepts",
        "method": "Sentiment Analysis & Tone enrichment",
        "implemented": True,
        "class_concept": True,
        "description": "Tone enrichment is implemented directly. Explicit standalone sentiment classifier is not used; comment and tone signals provide sentiment-like context.",
        "primary_files": ["semantic_enrichment.py", "channel_details.py", "app.py"],
    },
    {
        "category": "Analysis: Class Concepts",
        "method": "SNA - Social Network Analysis (degree, betweenness proxy, eigenvector proxy)",
        "implemented": True,
        "class_concept": True,
        "description": "Tag-based creator graph, centrality signals, and community detection for influence structure.",
        "primary_files": ["network_scoring.py", "app.py"],
    },
    {
        "category": "Analysis: Class Concepts",
        "method": "ROI Calculator & Simulation",
        "implemented": True,
        "class_concept": False,
        "description": "Scenario-based ROI calculations from budget, CPM, CTR, CVR, and AOV assumptions.",
        "primary_files": ["roi_simulation.py", "app.py"],
    },
    {
        "category": "Additional Category: Data Engineering",
        "method": "Data preparation and cleaning",
        "implemented": True,
        "class_concept": False,
        "description": "Deduplication, type normalization, include/exclude filtering, feature preparation.",
        "primary_files": ["data_prep.py"],
    },
    {
        "category": "Additional Category: Predictive Modeling",
        "method": "Regression benchmark suite",
        "implemented": True,
        "class_concept": False,
        "description": "LinearRegression, LASSO, Ridge, CART, RandomForest, LightGBM with 5-fold GroupKFold CV.",
        "primary_files": ["ml_modeling.py"],
    },
    {
        "category": "Additional Category: Explainability",
        "method": "SHAP model interpretation",
        "implemented": True,
        "class_concept": False,
        "description": "SHAP summary and dependence outputs for tree-based best model.",
        "primary_files": ["ml_modeling.py", "app.py"],
    },
    {
        "category": "Additional Category: Decision Optimization",
        "method": "Hybrid ranking + reliability controls + diversity guardrail",
        "implemented": True,
        "class_concept": False,
        "description": "Weighted final score, credibility multiplier, eligibility constraints, and community-aware Top-N.",
        "primary_files": ["ranking.py", "orchestrator.py", "app.py"],
    },
    {
        "category": "Additional Category: Reporting and Decision Support",
        "method": "Benchmarking, memo generation, strategy generation, export workflow",
        "implemented": True,
        "class_concept": False,
        "description": "Anchor vs benchmark comparison, executive memo, strategy text, and downloadable artifacts.",
        "primary_files": ["orchestrator.py", "content_generation.py", "app.py"],
    },
]


def get_analysis_category_table() -> pd.DataFrame:
    """Return a clean DataFrame for reporting or notebook display."""
    df = pd.DataFrame(ANALYSIS_CATEGORIES).copy()
    df["class_concept"] = df["class_concept"].map(lambda x: "Yes" if bool(x) else "No")
    return df

