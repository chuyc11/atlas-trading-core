from __future__ import annotations

from trading_core.equity_performance.drawdown_series import build_portfolio_drawdown_series
from trading_core.equity_performance.performance_config import PerformanceConfig


def test_drawdown_series_math() -> None:
    nav_records = [
        {"portfolio_id": "long_virtual_portfolio", "portfolio_key": "long", "as_of_date": "2026-06-26", "nav": 100.0},
        {"portfolio_id": "long_virtual_portfolio", "portfolio_key": "long", "as_of_date": "2026-06-29", "nav": 90.0},
        {"portfolio_id": "long_virtual_portfolio", "portfolio_key": "long", "as_of_date": "2026-06-30", "nav": 95.0},
    ]
    series = build_portfolio_drawdown_series(PerformanceConfig(as_of_date="2026-06-30"), nav_records)
    assert abs(series["records"][1]["drawdown"] + 0.1) < 1e-12
    assert abs(series["records"][2]["max_drawdown"] + 0.1) < 1e-12
