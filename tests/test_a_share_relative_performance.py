from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths


def test_relative_performance_current_snapshot_does_not_fabricate_history(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    result = build_performance_package(paths)
    relative = result["portfolio_relative_performance_series"]
    assert len(relative["records"]) == 18
    assert relative["limited_history_flagged"] is True
    assert relative["benchmark_metrics_do_not_fabricate_portfolio_history"] is True
    assert {row["metric_status"] for row in relative["records"]} == {"insufficient_history"}
