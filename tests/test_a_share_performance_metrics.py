from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths


def test_performance_metrics_are_insufficient_with_one_observation(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    result = build_performance_package(paths)
    metrics = result["performance_metric_snapshot"]["portfolios"]
    assert metrics["long_virtual_portfolio"]["metric_status"] == "insufficient_history"
    assert metrics["long_virtual_portfolio"]["rolling_volatility"]["value"] is None
    assert metrics["long_virtual_portfolio"]["benchmark_metrics"]["CSI300"]["tracking_error"]["metric_status"] == "insufficient_history"
