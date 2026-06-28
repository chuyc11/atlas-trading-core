"""Exposure calculations for virtual portfolio tracking."""

from __future__ import annotations

from typing import Any

from trading_core.equity_portfolio_tracking.tracking_config import PORTFOLIO_HORIZONS, PORTFOLIO_IDS, TARGET_VERSION, TRACKING_BOUNDARY, TRACKING_FLAGS, TrackingConfig


SCORE_FIELDS = [
    "RiskScore",
    "LiquidityScore",
    "LongScore",
    "MidScore",
    "ShortScore",
    "CompositeOpportunityScore",
]


def build_exposure_snapshot(config: TrackingConfig, holdings_snapshots: dict[str, dict[str, Any]]) -> dict[str, Any]:
    portfolios = {}
    for key, snapshot in holdings_snapshots.items():
        holdings = snapshot.get("holdings", [])
        industry_exposure = _industry_exposure(holdings)
        weighted_scores = _weighted_scores(holdings)
        portfolios[key] = {
            "target_version": TARGET_VERSION,
            "as_of_date": config.as_of_date,
            "portfolio_id": PORTFOLIO_IDS[key],
            "portfolio_horizon": PORTFOLIO_HORIZONS[key],
            "holding_count": len(holdings),
            "industry_exposure": industry_exposure,
            "max_industry_weight": max(industry_exposure.values() or [0.0]),
            "risk_score_weighted_avg": weighted_scores["RiskScore"],
            "liquidity_score_weighted_avg": weighted_scores["LiquidityScore"],
            "long_score_weighted_avg": weighted_scores["LongScore"],
            "mid_score_weighted_avg": weighted_scores["MidScore"],
            "short_score_weighted_avg": weighted_scores["ShortScore"],
            "composite_score_weighted_avg": weighted_scores["CompositeOpportunityScore"],
            **TRACKING_FLAGS,
        }
    return {
        "snapshot_id": "A-SHARE-VIRTUAL-PORTFOLIO-EXPOSURE-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "portfolios": portfolios,
        **TRACKING_FLAGS,
        "boundary": dict(TRACKING_BOUNDARY),
    }


def _industry_exposure(holdings: list[dict[str, Any]]) -> dict[str, float]:
    exposure: dict[str, float] = {}
    for row in holdings:
        industry = str(row.get("industry") or row.get("industry_level_1") or "Unclassified")
        exposure[industry] = exposure.get(industry, 0.0) + float(row.get("actual_weight") or 0.0)
    return dict(sorted(exposure.items(), key=lambda item: (-item[1], item[0])))


def _weighted_scores(holdings: list[dict[str, Any]]) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for field in SCORE_FIELDS:
        numerator = 0.0
        denominator = 0.0
        for row in holdings:
            score = row.get("score_snapshot", {}).get(field)
            if score is None:
                continue
            weight = float(row.get("actual_weight") or 0.0)
            numerator += float(score) * weight
            denominator += weight
        result[field] = numerator / denominator if denominator else None
    return result
