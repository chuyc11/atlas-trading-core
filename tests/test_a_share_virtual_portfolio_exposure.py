from __future__ import annotations

from pathlib import Path

from a_share_virtual_portfolio_tracking_test_utils import build_tracking_package, make_tracking_paths, tracking_json


def test_exposure_snapshot_contains_industry_and_weighted_scores(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    snapshot = tracking_json(paths, "portfolio_exposure_snapshot")

    for record in snapshot["portfolios"].values():
        assert record["industry_exposure"]
        assert record["max_industry_weight"] > 0.0
        assert record["risk_score_weighted_avg"] is not None
        assert record["liquidity_score_weighted_avg"] is not None
        assert record["long_score_weighted_avg"] is not None
        assert record["mid_score_weighted_avg"] is not None
        assert record["short_score_weighted_avg"] is not None
        assert record["composite_score_weighted_avg"] is not None
