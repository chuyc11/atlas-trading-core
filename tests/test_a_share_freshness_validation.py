from __future__ import annotations

from pathlib import Path

from a_share_data_refresh_test_utils import make_data_refresh_paths
from trading_core.equity_data_refresh.validation_core import DatasetSnapshot, load_dataset_snapshots, validate_freshness


def test_freshness_validation_fresh_stale_missing(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    snapshots = load_dataset_snapshots(paths)
    trading_dates = ["2026-06-24", "2026-06-25", "2026-06-26"]
    assert validate_freshness(snapshots["daily_price"], "2026-06-26", trading_dates)["freshness_status"] == "fresh"
    stale_frame = snapshots["daily_price"].frame[snapshots["daily_price"].frame["date"] < "2026-06-26"]
    stale = validate_freshness(DatasetSnapshot(snapshots["daily_price"].contract, stale_frame, snapshots["daily_price"].source_path), "2026-06-26", trading_dates)
    assert stale["freshness_status"] == "stale_blocking"
    missing = validate_freshness(DatasetSnapshot(snapshots["financial_indicators"].contract, snapshots["financial_indicators"].frame.iloc[0:0], ""), "2026-06-26", trading_dates)
    assert missing["freshness_status"] == "lagged_allowed"
