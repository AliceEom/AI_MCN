from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .utils import min_max_scale, normalize_text


@dataclass
class BrandBrief:
    brand_name: str
    product_name: str
    category: str
    target_audience: str
    campaign_goal: str
    budget_usd: float
    usp: str
    must_keywords: list[str]
    exclude_keywords: list[str]
    market: str

    @property
    def brief_md(self) -> str:
        return (
            f"Brand: {self.brand_name}\n"
            f"Product: {self.product_name}\n"
            f"Category: {self.category}\n"
            f"Target audience: {self.target_audience}\n"
            f"Campaign goal: {self.campaign_goal}\n"
            f"Market: {self.market}\n"
            f"Core message: {self.usp}\n"
            f"Must keywords: {', '.join(self.must_keywords)}\n"
            f"Excluded keywords: {', '.join(self.exclude_keywords)}"
        )


DEFAULT_BRAND = BrandBrief(
    brand_name="Beauty of Joseon",
    product_name="Relief Sun SPF + Glow Serum",
    category="Skincare",
    target_audience="US Gen Z and Millennial skincare users with sensitivity and acne concerns",
    campaign_goal="Awareness + trial conversion",
    budget_usd=50000,
    usp="Gentle, effective Korean skincare with lightweight textures and strong UV care.",
    must_keywords=["sunscreen", "spf", "sensitive skin", "k-beauty"],
    exclude_keywords=["music", "gaming", "movie"],
    market="United States",
)


def build_brand_brief(params: dict | None = None) -> BrandBrief:
    p = params or {}
    return BrandBrief(
        brand_name=str(p.get("brand_name", DEFAULT_BRAND.brand_name)),
        product_name=str(p.get("product_name", DEFAULT_BRAND.product_name)),
        category=str(p.get("category", DEFAULT_BRAND.category)),
        target_audience=str(p.get("target_audience", DEFAULT_BRAND.target_audience)),
        campaign_goal=str(p.get("campaign_goal", DEFAULT_BRAND.campaign_goal)),
        budget_usd=float(p.get("budget_usd", DEFAULT_BRAND.budget_usd)),
        usp=str(p.get("usp", DEFAULT_BRAND.usp)),
        must_keywords=list(p.get("must_keywords", DEFAULT_BRAND.must_keywords)),
        exclude_keywords=list(p.get("exclude_keywords", DEFAULT_BRAND.exclude_keywords)),
        market=str(p.get("market", DEFAULT_BRAND.market)),
    )


def compute_text_scores(channel_df: pd.DataFrame, brief: BrandBrief) -> pd.DataFrame:
    out = channel_df.copy()

    corpus = out["channel_text"].fillna("").astype(str).tolist()
    query = normalize_text(brief.brief_md + " " + " ".join(brief.must_keywords))

    vectorizer = TfidfVectorizer(
        max_features=2500,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
    )
    x = vectorizer.fit_transform(corpus + [query])
    sim = cosine_similarity(x[:-1], x[-1])[:, 0]

    out["tfidf_similarity_raw"] = sim

    # Encourage explicit must-keyword overlap.
    must_terms = [normalize_text(k) for k in brief.must_keywords if str(k).strip()]
    ex_terms = [normalize_text(k) for k in brief.exclude_keywords if str(k).strip()]

    def keyword_boost(text: str) -> float:
        t = normalize_text(text)
        if not t:
            return 0.0
        hit = sum(1 for w in must_terms if w and w in t)
        miss = sum(1 for w in ex_terms if w and w in t)
        return (0.08 * hit) - (0.12 * miss)

    out["keyword_boost"] = out["channel_text"].fillna("").apply(keyword_boost)
    out["tfidf_similarity"] = min_max_scale(out["tfidf_similarity_raw"] + out["keyword_boost"])
    return out
