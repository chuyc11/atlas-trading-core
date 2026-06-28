from __future__ import annotations

from pathlib import Path

from a_share_benchmark_test_utils import benchmark_json, build_benchmark_package, make_benchmark_paths


def test_benchmark_boundaries_clean_and_no_order_artifacts(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    build_benchmark_package(paths)
    boundary = benchmark_json(paths, "benchmark_boundary_check")
    assert boundary["benchmark_comparison_only"] is True
    assert boundary["research_only"] is True
    assert boundary["virtual_only"] is True
    assert boundary["run_daily_called"] is False
    assert boundary["day2_executed"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["model_profit_guaranteed"] is False
    assert boundary["live_trading_ready"] is False
    assert boundary["forbidden_artifacts_present"] == []
