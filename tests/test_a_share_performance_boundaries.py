from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths


def test_performance_boundaries_are_clean(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    result = build_performance_package(paths)
    boundary = result["performance_boundary_check"]
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["run_daily_called"] is False
    assert boundary["day2_executed"] is False
    assert boundary["historical_performance_fabricated"] is False
    assert boundary["future_data_used"] is False
