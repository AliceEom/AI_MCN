from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class ROISimulation:
    budget_usd: float
    cpm: float
    ctr: float
    cvr: float
    aov: float
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    roas: float
    roas_low: float
    roas_high: float

    def to_dict(self) -> dict:
        return asdict(self)


def simulate_roi(
    budget_usd: float,
    cpm: float = 18.0,
    ctr: float = 0.018,
    cvr: float = 0.03,
    aov: float = 38.0,
) -> ROISimulation:
    budget = max(float(budget_usd), 0.0)
    cpm = max(float(cpm), 0.01)
    ctr = max(float(ctr), 0.0)
    cvr = max(float(cvr), 0.0)
    aov = max(float(aov), 0.0)

    impressions = int((budget / cpm) * 1000)
    clicks = int(impressions * ctr)
    conversions = int(clicks * cvr)
    revenue = conversions * aov
    roas = revenue / budget if budget > 0 else 0.0

    return ROISimulation(
        budget_usd=budget,
        cpm=cpm,
        ctr=ctr,
        cvr=cvr,
        aov=aov,
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        revenue=revenue,
        roas=roas,
        roas_low=roas * 0.7,
        roas_high=roas * 1.3,
    )
