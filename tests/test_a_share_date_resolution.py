from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from a_share_data_refresh_test_utils import make_data_refresh_paths
from trading_core.equity_data_refresh.date_resolution import resolve_data_refresh_date


def test_date_resolution_exact_latest_and_non_trading_day(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    exact = resolve_data_refresh_date(paths=paths, as_of_date="2026-06-26")
    assert exact["overall_passed"] is True
    latest = resolve_data_refresh_date(paths=paths, resolve_latest_completed_trading_day=True, now=datetime(2026, 6, 28, tzinfo=ZoneInfo("Asia/Shanghai")))
    assert latest["resolved_as_of_date"] == "2026-06-26"
    bad = resolve_data_refresh_date(paths=paths, as_of_date="2026-06-27")
    assert bad["overall_passed"] is False
    intraday = resolve_data_refresh_date(paths=paths, resolve_latest_completed_trading_day=True, now=datetime(2026, 6, 26, 10, tzinfo=ZoneInfo("Asia/Shanghai")))
    assert intraday["resolved_as_of_date"] == "2026-06-25"
