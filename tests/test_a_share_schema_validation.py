from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_refresh_test_utils import make_data_refresh_paths
from trading_core.equity_data_refresh.dataset_contracts import dataset_contracts
from trading_core.equity_data_refresh.validation_core import DatasetSnapshot, load_dataset_snapshots, validate_schema


def test_schema_validation_missing_duplicate_and_ohlc_fail(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    snapshots = load_dataset_snapshots(paths)
    daily = snapshots["daily_price"]
    missing = DatasetSnapshot(daily.contract, daily.frame.drop(columns=["close"]), daily.source_path)
    assert validate_schema(missing, "2026-06-26")["schema_status"] == "failed"
    duplicate = DatasetSnapshot(daily.contract, pd.concat([daily.frame, daily.frame.head(1)], ignore_index=True), daily.source_path)
    assert validate_schema(duplicate, "2026-06-26")["schema_status"] == "failed"
    broken = daily.frame.copy()
    broken.loc[0, "low"] = broken.loc[0, "high"] + 1
    assert validate_schema(DatasetSnapshot(daily.contract, broken, daily.source_path), "2026-06-26")["schema_status"] == "failed"
    assert dataset_contracts()["daily_price"].criticality == "critical"
