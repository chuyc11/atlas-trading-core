from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_tracking_test_utils import build_tracking_package, make_tracking_paths, tracking_json


def test_drawdown_first_day_is_zero(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    snapshot = tracking_json(paths, "portfolio_drawdown_snapshot")

    assert snapshot["first_day_initialization"] is True
    for record in snapshot["portfolios"].values():
        assert record["max_drawdown"] == 0.0
        assert record["drawdown_start_date"] == AS_OF_DATE
        assert record["drawdown_end_date"] == AS_OF_DATE
