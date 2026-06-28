from __future__ import annotations

from pathlib import Path

from a_share_virtual_portfolio_tracking_test_utils import build_tracking_package, make_tracking_paths, tracking_json


def test_performance_first_day_initialization_behavior(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    snapshot = tracking_json(paths, "portfolio_performance_snapshot")

    assert snapshot["first_day_initialization"] is True
    assert snapshot["performance_not_yet_observed"] is True
    for record in snapshot["portfolios"].values():
        assert record["daily_return"] == 0.0
        assert record["cumulative_return"] == 0.0
        assert record["portfolio_volatility_if_enough_history"] is None
