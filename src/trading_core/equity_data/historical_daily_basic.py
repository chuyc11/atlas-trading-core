"""Backfill A-share daily basic history panel."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history
from trading_core.equity_data_quality.common import DAILY_BASIC_HISTORY_COLUMNS, HISTORICAL_BOUNDARY, HISTORICAL_TARGET_VERSION, read_frame, read_json, sha256_file, utc_now, write_frame, write_json
from trading_core.equity_data_quality.history_manifest import history_dirs
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def backfill_a_share_daily_basic_history(*, start_date: str, end_date: str, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    dirs = history_dirs(paths)
    daily_path = dirs["market_history"] / "daily_price_history_panel.parquet"
    if not daily_path.exists():
        backfill_a_share_daily_price_history(start_date=start_date, end_date=end_date, paths=paths)
    daily = read_frame(daily_path)
    frame = pd.DataFrame(columns=DAILY_BASIC_HISTORY_COLUMNS)
    if not daily.empty:
        frame = pd.DataFrame(
            {
                "date": daily["date"],
                "symbol": daily["symbol"],
                "total_mv": None,
                "circ_mv": None,
                "turnover_rate": daily["turnover"],
                "volume_ratio": None,
                "pe": None,
                "pe_ttm": None,
                "pb": None,
                "ps": None,
                "ps_ttm": None,
                "dv_ratio": None,
                "dv_ttm": None,
                "source": daily["source"],
                "source_timestamp": daily["source_timestamp"],
                "provider": daily["provider"],
                "ingested_at": daily["ingested_at"],
            },
            columns=DAILY_BASIC_HISTORY_COLUMNS,
        ).drop_duplicates(["date", "symbol"]).sort_values(["date", "symbol"])
    parquet_path = dirs["market_history"] / "daily_basic_history_panel.parquet"
    write_frame(frame, parquet_path)
    price_manifest = read_json(dirs["market_history"] / "daily_price_history_manifest.json")
    field_columns = [column for column in DAILY_BASIC_HISTORY_COLUMNS if column not in {"date", "symbol", "source", "source_timestamp", "provider", "ingested_at"}]
    manifest = {
        "manifest_id": "A-SHARE-DAILY-BASIC-HISTORY-MANIFEST",
        "target_version": HISTORICAL_TARGET_VERSION,
        "source_symbols_total": price_manifest.get("source_symbols_total", int(daily["symbol"].nunique()) if not daily.empty else 0),
        "symbols_attempted": price_manifest.get("symbols_attempted", int(daily["symbol"].nunique()) if not daily.empty else 0),
        "symbols_succeeded": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "symbols_failed": max(0, int(price_manifest.get("symbols_attempted", 0)) - (int(frame["symbol"].nunique()) if not frame.empty else 0)),
        "rows": int(len(frame)),
        "rows_total": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "date_count": int(frame["date"].nunique()) if not frame.empty else 0,
        "min_date": str(frame["date"].min()) if not frame.empty else "",
        "max_date": str(frame["date"].max()) if not frame.empty else "",
        "trading_days": int(frame["date"].nunique()) if not frame.empty else 0,
        "provider_breakdown": price_manifest.get("provider_breakdown", {}),
        "providers_attempted": price_manifest.get("providers_attempted", []),
        "providers_succeeded": price_manifest.get("providers_succeeded", []),
        "providers_failed": price_manifest.get("providers_failed", []),
        "field_coverage_ratio": {column: round(float(frame[column].notna().mean()), 6) if not frame.empty else 0.0 for column in field_columns},
        "coverage_note": "turnover_rate is derived from public kline turnover; valuation and market-cap history are nullable until richer providers are configured",
        "hash": sha256_file(parquet_path),
        "created_at": utc_now(),
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    manifest_path = dirs["market_history"] / "daily_basic_history_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}
