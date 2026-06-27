from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from a_share_data_test_utils import build_foundation, make_a_share_paths
from trading_core.storage.file_paths import ProjectPaths


def make_history_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_a_share_paths(tmp_path)
    build_foundation(paths)
    (paths.data_dir / "equity_market" / "history").mkdir(parents=True, exist_ok=True)
    (paths.data_dir / "equity_fundamental" / "history").mkdir(parents=True, exist_ok=True)
    return paths


def fake_price_provider_result(symbols: list[str] | None = None, periods: int = 260) -> dict:
    selected = symbols or ["600000.SH", "000001.SZ", "300750.SZ"]
    dates = pd.bdate_range("2023-01-02", periods=periods)
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    rows = []
    for index, symbol in enumerate(selected):
        base = 10.0 + index
        for offset, day in enumerate(dates):
            close = base + offset * 0.01
            rows.append(
                {
                    "date": day.date().isoformat(),
                    "symbol": symbol,
                    "open": close - 0.05,
                    "high": close + 0.10,
                    "low": close - 0.10,
                    "close": close,
                    "volume": 100000 + offset,
                    "amount": 1000000.0 + offset,
                    "turnover": 1.0,
                    "pre_close": close - 0.01,
                    "change": 0.01,
                    "pct_change": 0.1,
                    "source": "fixture_history_provider",
                    "source_timestamp": now,
                    "provider": "fixture_history_provider",
                    "ingested_at": now,
                }
            )
    return {
        "provider": "fixture_history_provider",
        "attempted_symbols": selected,
        "succeeded_symbols": selected,
        "failed_symbols": [],
        "rows": rows,
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "source_timestamp": now,
    }


def fake_financial_provider_result(symbols: list[str] | None = None, quarters: int = 12) -> dict:
    selected = symbols or ["600000.SH", "000001.SZ", "300750.SZ"]
    report_dates = pd.date_range("2021-03-31", periods=quarters, freq="QE")
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    rows = []
    for symbol in selected:
        for day in report_dates:
            rows.append(
                {
                    "report_date": day.date().isoformat(),
                    "ann_date": day.date().isoformat(),
                    "symbol": symbol,
                    "revenue": 1000000.0,
                    "net_profit": 100000.0,
                    "roe": 8.0,
                    "gross_margin": 30.0,
                    "net_margin": None,
                    "operating_cash_flow": 0.5,
                    "debt_to_asset": None,
                    "eps": 0.2,
                    "bps": 4.0,
                    "source": "fixture_financial_provider",
                    "source_timestamp": now,
                    "provider": "fixture_financial_provider",
                    "ingested_at": now,
                }
            )
    return {
        "provider": "fixture_financial_provider",
        "attempted_quarters": [day.date().isoformat() for day in report_dates],
        "succeeded_quarters": [day.date().isoformat() for day in report_dates],
        "failed_quarters": [],
        "rows": rows,
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "source_timestamp": now,
    }
