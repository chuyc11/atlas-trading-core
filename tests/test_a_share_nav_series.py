from __future__ import annotations

from trading_core.equity_performance.nav_series import build_portfolio_nav_series
from trading_core.equity_performance.performance_config import PerformanceConfig


def test_nav_series_counts_observations() -> None:
    config = PerformanceConfig()
    records = [
        {"portfolio_id": "long_virtual_portfolio", "portfolio_key": "long", "as_of_date": "2026-06-26", "nav": 1_000_000.0, "first_day_initialization": True},
        {"portfolio_id": "mid_virtual_portfolio", "portfolio_key": "mid", "as_of_date": "2026-06-26", "nav": 1_000_000.0, "first_day_initialization": True},
        {"portfolio_id": "short_virtual_portfolio", "portfolio_key": "short", "as_of_date": "2026-06-26", "nav": 1_000_000.0, "first_day_initialization": True},
    ]
    series = build_portfolio_nav_series(config, records)
    assert series["multi_day_observations"] == 1
    assert series["multi_day_performance_available"] is False
