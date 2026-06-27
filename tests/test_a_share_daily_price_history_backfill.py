from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_historical_test_utils import fake_price_provider_result, make_history_paths
from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history


def test_a_share_daily_price_history_backfill_schema_valid(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    result = backfill_a_share_daily_price_history(start_date="2023-01-01", end_date="2026-06-26", paths=paths, provider_result=fake_price_provider_result())
    frame = pd.read_parquet(result["parquet_path"])
    assert result["symbol_count"] == 3
    assert result["duplicate_rows"] == 0
    assert result["non_positive_prices"] == 0
    assert {"provider", "ingested_at"}.issubset(frame.columns)
    assert frame["volume"].ge(0).all()
