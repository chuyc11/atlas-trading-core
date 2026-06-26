from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_data.daily_basic import ingest_a_share_daily_basic


def test_a_share_daily_basic_ingestion_records_partial_fields(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = ingest_a_share_daily_basic(paths=paths, as_of_date="2026-06-26")
    frame = pd.read_parquet(result["parquet_path"])
    assert result["symbol_count"] == 6
    assert result["field_coverage"]["total_mv"] == 1.0
    assert result["field_coverage"]["volume_ratio"] == 0.0
    assert (frame["total_mv"] >= 0).all()

