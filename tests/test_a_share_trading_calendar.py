from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_universe.calendar import build_a_share_trading_calendar


def test_a_share_trading_calendar_covers_exchanges(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = build_a_share_trading_calendar(paths=paths, end_date="2026-06-26", lookback_days=10)
    frame = pd.read_parquet(result["parquet_path"])
    assert {"SSE", "SZSE", "BSE"} == set(frame["exchange"])
    assert frame["is_trading_day"].all()
    assert result["trading_days"] > 0
    assert result["max_date"] >= "2026-06-26"

