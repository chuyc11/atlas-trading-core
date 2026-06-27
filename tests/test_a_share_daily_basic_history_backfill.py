from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_historical_test_utils import fake_price_provider_result, make_history_paths
from trading_core.equity_data.historical_daily_basic import backfill_a_share_daily_basic_history
from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history


def test_a_share_daily_basic_history_backfill_records_partial_fields(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    backfill_a_share_daily_price_history(start_date="2023-01-01", end_date="2026-06-26", paths=paths, provider_result=fake_price_provider_result())
    result = backfill_a_share_daily_basic_history(start_date="2023-01-01", end_date="2026-06-26", paths=paths)
    frame = pd.read_parquet(result["parquet_path"])
    assert result["symbol_count"] == 3
    assert result["field_coverage_ratio"]["turnover_rate"] == 1.0
    assert frame["pe"].isna().all()
