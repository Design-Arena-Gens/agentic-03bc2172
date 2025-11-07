"""Rule-based insights to prime LLM reasoning."""

from __future__ import annotations

from typing import List

from .models import Insight, MetricSnapshot, Recommendation


def roas_low_insight(metric: MetricSnapshot) -> Insight | None:
    if metric.roas is None:
        return None
    if 1.0 <= metric.roas <= 2.0:
        return Insight(
            label="ROAS 1–2",
            signal="Efficiency is muted with ROAS between 1 and 2",
            recommendation=Recommendation(
                summary="Test new hooks and cap frequency to push ROAS above target",
                actions=[
                    "Launch 2–3 new creatives focusing on fresh angles",
                    "Rotate new thumbnail variants to fight fatigue",
                    "Apply frequency cap or refresh audience",
                ],
                priority="high",
            ),
            confidence=0.7,
        )
    if metric.roas is not None and metric.roas < 1.0:
        return Insight(
            label="ROAS < 1",
            signal="Campaign is losing money",
            recommendation=Recommendation(
                summary="Pause and rebuild offer targeting to reach profitability",
                actions=[
                    "Pause worst performing ad sets",
                    "Reassess targeting and bidding",
                    "Rebuild funnel messaging",
                ],
                priority="high",
            ),
            confidence=0.8,
        )
    return None


def ctr_health_conversion_gap(metric: MetricSnapshot) -> Insight | None:
    if metric.ctr_percent is None or metric.atc_to_purchase_percent is None:
        return None
    if metric.ctr_percent >= 1.5 and metric.atc_to_purchase_percent < 20:
        return Insight(
            label="CTR healthy but conversion lagging",
            signal="Traffic quality is solid but conversion funnel underperforms",
            recommendation=Recommendation(
                summary="Audit landing page and checkout to fix conversion leakage",
                actions=[
                    "A/B test landing page copy and load speed",
                    "Analyze checkout drop-off recordings",
                    "Validate tracking for adds to cart vs purchases",
                ],
                priority="medium",
            ),
            confidence=0.75,
        )
    return None


def generate_rule_based_insights(metrics: List[MetricSnapshot]) -> List[Insight]:
    insights: List[Insight] = []
    for metric in metrics:
        for fn in (roas_low_insight, ctr_health_conversion_gap):
            insight = fn(metric)
            if insight:
                insights.append(insight)
    return insights
