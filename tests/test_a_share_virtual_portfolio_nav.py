from __future__ import annotations

from pathlib import Path

from a_share_virtual_portfolio_tracking_test_utils import build_tracking_package, make_tracking_paths, tracking_json


def test_nav_snapshot_cash_plus_holdings_and_weight_sum(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    snapshot = tracking_json(paths, "portfolio_nav_snapshot")

    for key in ["long", "mid", "short"]:
        record = snapshot["portfolios"][key]
        assert record["portfolio_nav"] == record["cash_balance"] + record["holdings_market_value"]
        assert record["portfolio_nav"] == 1_000_000.0
        assert 0.999 <= record["weight_sum"] <= 1.001
        assert record["gross_exposure"] == record["net_exposure"]
        assert record["holding_count"] == 2
