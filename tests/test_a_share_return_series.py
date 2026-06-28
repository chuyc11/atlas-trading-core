from __future__ import annotations

from trading_core.equity_performance.performance_config import PerformanceConfig
from trading_core.equity_performance.return_series import build_portfolio_return_series


def test_return_series_math() -> None:
    nav_records = [
        {"portfolio_id": "long_virtual_portfolio", "portfolio_key": "long", "as_of_date": "2026-06-26", "nav": 100.0},
        {"portfolio_id": "long_virtual_portfolio", "portfolio_key": "long", "as_of_date": "2026-06-29", "nav": 105.0},
    ]
    series = build_portfolio_return_series(PerformanceConfig(as_of_date="2026-06-29"), nav_records)
    assert series["records"][0]["daily_return"] == 0.0
    assert abs(series["records"][1]["daily_return"] - 0.05) < 1e-12
    assert abs(series["records"][1]["cumulative_return"] - 0.05) < 1e-12
