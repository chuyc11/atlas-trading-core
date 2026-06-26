from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_data.daily_price import ingest_a_share_daily_prices


def test_a_share_daily_price_ingestion_schema_and_sanity(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = ingest_a_share_daily_prices(paths=paths, as_of_date="2026-06-26")
    frame = pd.read_parquet(result["parquet_path"])
    assert result["symbol_count"] == 6
    assert result["duplicate_rows"] == 0
    assert result["non_positive_prices"] == 0
    assert result["high_low_inversion"] == 0
    assert frame["date"].eq("2026-06-26").all()

