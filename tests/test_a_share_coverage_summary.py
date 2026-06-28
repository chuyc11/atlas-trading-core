from __future__ import annotations

from pathlib import Path

from a_share_data_refresh_test_utils import make_data_refresh_paths
from trading_core.equity_data_refresh.coverage_summary import build_dataset_coverage_summary
from trading_core.equity_data_refresh.validation_core import DatasetSnapshot, load_dataset_snapshots


def test_coverage_summary_pass_and_fail(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    snapshots = load_dataset_snapshots(paths)
    passed = build_dataset_coverage_summary(as_of_date="2026-06-26", snapshots=snapshots)
    assert passed["coverage_validation_status"] == "passed"
    daily = snapshots["daily_price"]
    snapshots["daily_price"] = DatasetSnapshot(daily.contract, daily.frame[daily.frame["symbol"] == "600001.SH"], daily.source_path)
    failed = build_dataset_coverage_summary(as_of_date="2026-06-26", snapshots=snapshots)
    assert failed["datasets"]["daily_price"]["threshold_passed"] is False
