from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.equity_features.multi_horizon import FEATURE_FILES, build_a_share_multi_horizon_features
from trading_core.storage.file_paths import ProjectPaths


AS_OF_DATE = "2026-06-26"
STRICT_SYMBOLS = ["600001.SH", "600002.SH", "600003.SH"]
EXCLUDED_SYMBOL = "600004.SH"


def make_feature_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_a_share_paths(tmp_path)
    for relative in [
        "data/equity_market/history",
        "data/equity_fundamental/history",
        "data/equity_selection/daily/2026-06-26",
        "data/equity_features/daily",
        "outputs/equity_features/daily",
        "outputs/audit",
    ]:
        (paths.project_root / relative).mkdir(parents=True, exist_ok=True)
    write_feature_fixture(paths)
    return paths


def build_feature_package(paths: ProjectPaths) -> dict:
    return build_a_share_multi_horizon_features(paths=paths, as_of_date=AS_OF_DATE)


def feature_frame(paths: ProjectPaths, group: str) -> pd.DataFrame:
    path = paths.data_dir / "equity_features" / "daily" / AS_OF_DATE / FEATURE_FILES[group]
    return pd.read_parquet(path)


def feature_json(paths: ProjectPaths, name: str) -> dict:
    return json.loads((paths.data_dir / "equity_features" / "daily" / AS_OF_DATE / name).read_text(encoding="utf-8"))


def write_feature_fixture(paths: ProjectPaths) -> None:
    dates = [day.date().isoformat() for day in pd.bdate_range(end=AS_OF_DATE, periods=1150)]
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    _write_selection(paths)
    _write_price_history(paths, dates, now)
    _write_daily_basic(paths, dates, now)
    _write_financials(paths, now)
    _write_industry(paths, now)


def _write_selection(paths: ProjectPaths) -> None:
    data_dir = paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE
    rows = [
        _universe_row("600001.SH", "Alpha Bank", "Finance", "Bank"),
        _universe_row("600002.SH", "Beta Bank", "Finance", "Bank"),
        _universe_row("600003.SH", "Gamma Works", "Industrial", "Machinery"),
    ]
    excluded = [
        {
            "symbol": EXCLUDED_SYMBOL,
            "name": "Excluded",
            "bucket": "excluded_universe",
            "primary_exclusion_reason": "fixture_excluded",
            "all_exclusion_reasons": ["fixture_excluded"],
        }
    ]
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "strict_tradable_universe.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    (data_dir / "excluded_universe.json").write_text(json.dumps(excluded, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(rows).to_parquet(data_dir / "tradable_universe.parquet", index=False)


def _universe_row(symbol: str, name: str, industry_1: str, industry_2: str) -> dict:
    return {
        "symbol": symbol,
        "name": name,
        "exchange": "SSE",
        "board": "SSE_MAIN",
        "industry_level_1": industry_1,
        "industry_level_2": industry_2,
        "bucket": "strict_tradable_universe",
        "listing_trading_days": 1150,
        "has_250d_history": True,
        "close": 10.0,
        "avg_amount_20d": 100_000_000.0,
        "avg_amount_60d": 100_000_000.0,
        "total_mv": 10_000_000_000.0,
        "circ_mv": 8_000_000_000.0,
    }


def _write_price_history(paths: ProjectPaths, dates: list[str], now: str) -> None:
    rows = []
    adjusted_rows = []
    symbols = [*STRICT_SYMBOLS, EXCLUDED_SYMBOL]
    for symbol_index, symbol in enumerate(symbols, start=1):
        for index, day in enumerate(dates):
            close = 10.0 * symbol_index + index * (0.025 + symbol_index * 0.005)
            previous = 10.0 * symbol_index + (index - 1) * (0.025 + symbol_index * 0.005) if index else close
            volume = 1_000_000 + index * 100 + symbol_index * 10_000
            row = {
                "date": day,
                "symbol": symbol,
                "open": close * 0.995,
                "high": close * 1.01,
                "low": close * 0.99,
                "close": close,
                "volume": volume,
                "amount": volume * close,
                "turnover": 1.0 + index / 10_000,
                "pre_close": previous,
                "change": close - previous,
                "pct_change": (close / previous - 1.0) * 100.0 if previous else 0.0,
                "source": "fixture_price",
                "source_timestamp": now,
                "provider": "fixture",
                "ingested_at": now,
            }
            rows.append(row)
            adjusted_rows.append(
                {
                    "date": day,
                    "symbol": symbol,
                    "adj_open": row["open"],
                    "adj_high": row["high"],
                    "adj_low": row["low"],
                    "adj_close": row["close"],
                    "adj_factor": 1.0,
                    "adjustment_type": "qfq",
                    "source": "fixture_adjusted",
                    "source_timestamp": now,
                    "provider": "fixture",
                    "ingested_at": now,
                }
            )
    _parquet(paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet", rows)
    _parquet(paths.data_dir / "equity_market" / "history" / "adjusted_price_history_panel.parquet", adjusted_rows)


def _write_daily_basic(paths: ProjectPaths, dates: list[str], now: str) -> None:
    history_rows = []
    snapshot_rows = []
    for symbol_index, symbol in enumerate([*STRICT_SYMBOLS, EXCLUDED_SYMBOL], start=1):
        for index, day in enumerate(dates):
            history_rows.append(
                {
                    "date": day,
                    "symbol": symbol,
                    "total_mv": 10_000_000_000.0 + index * 1_000_000 + symbol_index,
                    "circ_mv": 8_000_000_000.0 + index * 800_000 + symbol_index,
                    "turnover_rate": 1.0 + index / 10_000,
                    "volume_ratio": 1.0,
                    "pe": 10.0 + symbol_index,
                    "pe_ttm": 11.0 + symbol_index,
                    "pb": 1.2 + symbol_index / 10,
                    "ps": 2.0 + symbol_index / 10,
                    "ps_ttm": 2.2 + symbol_index / 10,
                    "dv_ratio": 1.0,
                    "dv_ttm": 1.1,
                    "source": "fixture_basic_history",
                    "source_timestamp": now,
                    "provider": "fixture",
                    "ingested_at": now,
                }
            )
        snapshot_rows.append({**history_rows[-1], "source": "fixture_basic_snapshot"})
    _parquet(paths.data_dir / "equity_market" / "history" / "daily_basic_history_panel.parquet", history_rows)
    _parquet(paths.data_dir / "equity_market" / "daily_basic_panel.parquet", snapshot_rows)


def _write_financials(paths: ProjectPaths, now: str) -> None:
    rows = []
    reports = [day.date().isoformat() for day in pd.date_range("2021-03-31", "2026-03-31", freq="QE")]
    for symbol_index, symbol in enumerate([*STRICT_SYMBOLS, EXCLUDED_SYMBOL], start=1):
        for index, report_date in enumerate(reports, start=1):
            rows.append(
                {
                    "report_date": report_date,
                    "ann_date": report_date,
                    "symbol": symbol,
                    "revenue": 1_000_000.0 * symbol_index + index * 10_000,
                    "net_profit": 100_000.0 * symbol_index + index * 2_000,
                    "roe": 8.0 + index / 10,
                    "gross_margin": 30.0,
                    "net_margin": 10.0,
                    "operating_cash_flow": 50_000.0 + index,
                    "debt_to_asset": 40.0,
                    "eps": 0.2 + index / 100,
                    "bps": 4.0 + index / 10,
                    "source": "fixture_financial",
                    "source_timestamp": now,
                    "provider": "fixture",
                    "ingested_at": now,
                }
            )
    _parquet(paths.data_dir / "equity_fundamental" / "history" / "basic_financials_history_panel.parquet", rows)


def _write_industry(paths: ProjectPaths, now: str) -> None:
    rows = [
        ("600001.SH", "Finance", "Bank"),
        ("600002.SH", "Finance", "Bank"),
        ("600003.SH", "Industrial", "Machinery"),
        (EXCLUDED_SYMBOL, "Industrial", "Machinery"),
    ]
    _parquet(
        paths.data_dir / "equity_industry" / "industry_classification.parquet",
        [
            {
                "symbol": symbol,
                "industry_level_1": industry_1,
                "industry_level_2": industry_2,
                "industry_level_3": "",
                "industry_standard": "fixture",
                "effective_date": AS_OF_DATE,
                "source": "fixture_industry",
                "source_timestamp": now,
            }
            for symbol, industry_1, industry_2 in rows
        ],
    )


def _parquet(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)
