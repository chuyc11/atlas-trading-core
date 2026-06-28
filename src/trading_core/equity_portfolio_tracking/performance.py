"""First-day virtual performance calculations."""

from __future__ import annotations

from typing import Any

from trading_core.equity_portfolio_tracking.tracking_config import PORTFOLIO_HORIZONS, PORTFOLIO_IDS, TARGET_VERSION, TRACKING_BOUNDARY, TRACKING_FLAGS, TrackingConfig


def build_performance_snapshot(config: TrackingConfig, nav_records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    portfolios = {}
    for key, nav in nav_records.items():
        portfolios[key] = {
            "target_version": TARGET_VERSION,
            "as_of_date": config.as_of_date,
            "portfolio_id": PORTFOLIO_IDS[key],
            "portfolio_horizon": PORTFOLIO_HORIZONS[key],
            "portfolio_nav": float(nav.get("portfolio_nav") or 0.0),
            "daily_return": 0.0,
            "cumulative_return": 0.0,
            "portfolio_volatility_if_enough_history": None,
            "first_day_initialization": True,
            "performance_not_yet_observed": True,
            **TRACKING_FLAGS,
        }
    return {
        "snapshot_id": "A-SHARE-VIRTUAL-PORTFOLIO-PERFORMANCE-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "portfolios": portfolios,
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        **TRACKING_FLAGS,
        "boundary": dict(TRACKING_BOUNDARY),
    }
