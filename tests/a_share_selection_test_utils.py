from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from a_share_data_test_utils import make_a_share_paths
from trading_core.storage.file_paths import ProjectPaths


AS_OF_DATE = "2026-06-26"


SYMBOLS = {
    "strict": "600001.SH",
    "st": "600002.SH",
    "new": "600003.SH",
    "missing_price": "600004.SH",
    "low_liquidity": "600005.SH",
    "low_market_cap": "600006.SH",
    "low_price": "600007.SH",
    "invalid_price": "600008.SH",
    "limit_up": "600009.SH",
    "unknown_st": "600010.SH",
    "short_history": "600011.SH",
    "delisted": "600012.SH",
    "missing_market_cap": "600013.SH",
    "estimated_amount": "600014.SH",
}


def make_tradable_universe_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_a_share_paths(tmp_path)
    for relative in [
        "data/equity_market/history",
        "data/equity_fundamental/history",
        "data/equity_selection/daily",
        "outputs/equity_selection/daily",
        "outputs/audit",
    ]:
        (paths.project_root / relative).mkdir(parents=True, exist_ok=True)
    write_tradable_universe_fixture(paths)
    return paths


def write_tradable_universe_fixture(paths: ProjectPaths) -> None:
    dates = [day.date().isoformat() for day in pd.bdate_range(end=AS_OF_DATE, periods=300)]
    history_dates = dates[-260:]
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    _write_calendar(paths, dates, now)
    _write_master(paths, now)
    _write_price_history(paths, history_dates, now)
    _write_daily_basic(paths, now)
    _write_industry(paths, now)
    _write_financials(paths, now)
    _write_quality_inputs(paths)


def _write_calendar(paths: ProjectPaths, dates: list[str], now: str) -> None:
    rows = []
    for exchange in ["SSE", "SZSE", "BSE"]:
        for index, day in enumerate(dates):
            rows.append(
                {
                    "date": day,
                    "exchange": exchange,
                    "is_trading_day": True,
                    "previous_trading_day": dates[index - 1] if index else "",
                    "next_trading_day": dates[index + 1] if index + 1 < len(dates) else "",
                    "source": "fixture_calendar",
                    "source_timestamp": now,
                }
            )
    _parquet(paths.data_dir / "equity_universe" / "trading_calendar.parquet", rows)


def _write_master(paths: ProjectPaths, now: str) -> None:
    rows = []
    for index, (key, symbol) in enumerate(SYMBOLS.items(), start=1):
        rows.append(
            {
                "symbol": symbol,
                "exchange": "SSE",
                "market": "A_SHARE",
                "name": "*ST Risk" if key == "st" else f"Fixture {index}",
                "list_date": "2026-06-01" if key == "new" else "2020-01-02",
                "delist_date": "2026-01-01" if key == "delisted" else "",
                "board": "SSE_MAIN",
                "is_active": key != "delisted",
                "is_st": None if key == "unknown_st" else key == "st",
                "is_star_market": False,
                "is_chinext": False,
                "is_bse": False,
                "currency": "CNY",
                "source": "fixture_master",
                "source_timestamp": now,
            }
        )
    _parquet(paths.data_dir / "equity_universe" / "equity_master.parquet", rows)


def _write_price_history(paths: ProjectPaths, dates: list[str], now: str) -> None:
    rows = []
    for key, symbol in SYMBOLS.items():
        selected_dates = dates[-100:] if key == "short_history" else list(dates)
        if key == "missing_price":
            selected_dates = selected_dates[:-1]
        for day in selected_dates:
            close = 10.0
            amount = 100_000_000.0
            volume = 10_000_000
            high = 10.2
            low = 9.8
            pct_change = 1.0
            if key == "low_liquidity":
                amount = 1_000_000.0
            if key == "low_price":
                close = 1.5
                high = 1.6
                low = 1.4
            if key == "invalid_price" and day == AS_OF_DATE:
                high = 9.0
                low = 11.0
            if key == "limit_up" and day == AS_OF_DATE:
                close = high = low = 10.0
                pct_change = 9.9
            if key == "estimated_amount":
                amount = None
            rows.append(
                {
                    "date": day,
                    "symbol": symbol,
                    "open": close,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": volume,
                    "amount": amount,
                    "turnover": 1.0,
                    "pre_close": close - 0.1,
                    "change": 0.1,
                    "pct_change": pct_change,
                    "source": "fixture_history",
                    "source_timestamp": now,
                    "provider": "fixture_history",
                    "ingested_at": now,
                }
            )
    price = pd.DataFrame(rows)
    _parquet(paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet", price)
    adjusted = price[["date", "symbol", "open", "high", "low", "close", "source", "source_timestamp", "provider", "ingested_at"]].rename(
        columns={"open": "adj_open", "high": "adj_high", "low": "adj_low", "close": "adj_close"}
    )
    adjusted["adj_factor"] = 1.0
    adjusted["adjustment_type"] = "raw"
    _parquet(paths.data_dir / "equity_market" / "history" / "adjusted_price_history_panel.parquet", adjusted)


def _write_daily_basic(paths: ProjectPaths, now: str) -> None:
    history_rows = []
    snapshot_rows = []
    for key, symbol in SYMBOLS.items():
        total_mv = 10_000_000_000.0
        circ_mv = 8_000_000_000.0
        if key == "low_market_cap":
            total_mv = 1_000_000_000.0
            circ_mv = 900_000_000.0
        if key == "missing_market_cap":
            total_mv = None
            circ_mv = None
        history_rows.append(
            {
                "date": AS_OF_DATE,
                "symbol": symbol,
                "total_mv": None,
                "circ_mv": None,
                "turnover_rate": 1.0,
                "volume_ratio": None,
                "pe": None,
                "pe_ttm": None,
                "pb": None,
                "ps": None,
                "ps_ttm": None,
                "dv_ratio": None,
                "dv_ttm": None,
                "source": "fixture_history_basic",
                "source_timestamp": now,
                "provider": "fixture_history_basic",
                "ingested_at": now,
            }
        )
        snapshot_rows.append(
            {
                "date": AS_OF_DATE,
                "symbol": symbol,
                "total_mv": total_mv,
                "circ_mv": circ_mv,
                "turnover_rate": 1.0,
                "volume_ratio": None,
                "pe": None,
                "pe_ttm": None,
                "pb": None,
                "ps": None,
                "ps_ttm": None,
                "dv_ratio": None,
                "dv_ttm": None,
                "source": "qstock_reference_public_http",
                "source_timestamp": now,
            }
        )
    _parquet(paths.data_dir / "equity_market" / "history" / "daily_basic_history_panel.parquet", history_rows)
    _parquet(paths.data_dir / "equity_market" / "daily_basic_panel.parquet", snapshot_rows)


def _write_industry(paths: ProjectPaths, now: str) -> None:
    rows = [
        {
            "symbol": symbol,
            "industry_level_1": "Fixture",
            "industry_level_2": "Fixture Sub",
            "industry_level_3": "",
            "industry_standard": "fixture",
            "effective_date": AS_OF_DATE,
            "source": "fixture_industry",
            "source_timestamp": now,
        }
        for symbol in SYMBOLS.values()
    ]
    _parquet(paths.data_dir / "equity_industry" / "industry_classification.parquet", rows)


def _write_financials(paths: ProjectPaths, now: str) -> None:
    rows = []
    for symbol in SYMBOLS.values():
        for report_date in pd.date_range("2023-03-31", periods=12, freq="QE"):
            rows.append(
                {
                    "report_date": report_date.date().isoformat(),
                    "ann_date": report_date.date().isoformat(),
                    "symbol": symbol,
                    "revenue": 1_000_000.0,
                    "net_profit": 100_000.0,
                    "roe": 8.0,
                    "gross_margin": 30.0,
                    "net_margin": 10.0,
                    "operating_cash_flow": 0.5,
                    "debt_to_asset": 40.0,
                    "eps": 0.2,
                    "bps": 4.0,
                    "source": "fixture_financial",
                    "source_timestamp": now,
                    "provider": "fixture_financial",
                    "ingested_at": now,
                }
            )
    _parquet(paths.data_dir / "equity_fundamental" / "history" / "basic_financials_history_panel.parquet", rows)


def _write_quality_inputs(paths: ProjectPaths) -> None:
    quality = paths.data_dir / "equity_data_quality"
    quality.mkdir(parents=True, exist_ok=True)
    (quality / "a_share_historical_backfill_symbol_manifest.json").write_text(
        json.dumps({"manifest_id": "fixture", "summary": {"symbols_total": len(SYMBOLS), "symbols_succeeded": len(SYMBOLS)}}),
        encoding="utf-8",
    )
    version = "v0.7.1.2-a-share-historical-data-provider-expansion"
    (quality / "a_share_historical_panel_coverage_audit.json").write_text(
        json.dumps({"audit_id": "coverage", "target_version": version, "overall_passed": True}),
        encoding="utf-8",
    )
    (quality / "a_share_feature_readiness_audit.json").write_text(
        json.dumps({"audit_id": "readiness", "target_version": version, "overall_passed": True}),
        encoding="utf-8",
    )


def _parquet(path: Path, rows_or_frame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = rows_or_frame if isinstance(rows_or_frame, pd.DataFrame) else pd.DataFrame(rows_or_frame)
    frame.to_parquet(path, index=False)

