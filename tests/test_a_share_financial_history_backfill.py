from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_historical_test_utils import fake_financial_provider_result, make_history_paths
from trading_core.equity_fundamental.historical_financials import backfill_a_share_financial_history


def test_a_share_financial_history_backfill_schema_valid(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    result = backfill_a_share_financial_history(start_date="2021-01-01", end_date="2026-06-26", paths=paths, provider_result=fake_financial_provider_result())
    frame = pd.read_parquet(result["parquet_path"])
    assert result["symbol_count"] == 3
    assert result["report_date_coverage"] == 12
    assert frame.duplicated(["report_date", "symbol"]).sum() == 0
    assert frame["revenue"].notna().all()
