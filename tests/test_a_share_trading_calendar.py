from __future__ import annotations
import pytest

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
    assert "2026-06-19" not in set(frame["date"])
    assert set(frame["source"]) == {"official_exchange_holiday_schedule_v1"}


def test_a_share_calendar_fails_closed_without_official_year_coverage(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    with pytest.raises(ValueError, match="missing years: 2027"):
        build_a_share_trading_calendar(paths=paths, end_date="2027-01-15", lookback_days=10)


def test_a_share_calendar_clamps_forward_horizon_and_reports(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = build_a_share_trading_calendar(paths=paths, end_date="2026-12-15", lookback_days=10)
    frame = pd.read_parquet(result["parquet_path"])
    assert result["horizon_clamped"] is True
    assert result["calendar_horizon_end"] == "2026-12-31"
    assert result["forward_horizon_end"] == "2027-04-14"
    assert result["warnings"], "clamp must be surfaced as a warning"
    assert "2027" in result["warnings"][0]
    assert frame["date"].max() <= "2026-12-31"
    assert set(frame["source"]) == {"official_exchange_holiday_schedule_v1"}


def test_a_share_calendar_reports_no_clamp_within_supported_years(tmp_path: Path) -> None:
    paths = make_a_share_paths(tmp_path)
    result = build_a_share_trading_calendar(paths=paths, end_date="2026-06-26", lookback_days=10)
    assert result["horizon_clamped"] is False
    assert result["warnings"] == []
    assert result["calendar_horizon_end"] == "2026-10-24"
