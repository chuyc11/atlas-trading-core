from __future__ import annotations

from trading_core.equity_data_refresh.data_refresh_boundary import build_data_refresh_boundary_check


def test_data_refresh_boundary_clean() -> None:
    boundary = build_data_refresh_boundary_check(as_of_date="2026-06-26")
    assert boundary["run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["research_workflow_triggered"] is False
