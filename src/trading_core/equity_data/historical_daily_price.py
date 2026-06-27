"""Backfill A-share daily price history panel."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import DAILY_PRICE_HISTORY_COLUMNS, HISTORICAL_BOUNDARY, HISTORICAL_TARGET_VERSION, normalize_symbol, write_frame, write_json
from trading_core.equity_data_quality.history_manifest import history_dirs
from trading_core.integrations.public_data.historical_provider_registry import fetch_price_history, select_history_symbols
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def backfill_a_share_daily_price_history(
    *,
    start_date: str,
    end_date: str,
    paths: ProjectPaths | None = None,
    provider_result: dict[str, Any] | None = None,
    max_symbols: int | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    symbols = select_history_symbols(paths, max_symbols=max_symbols)
    result = provider_result or fetch_price_history(symbols, start_date=start_date, end_date=end_date, adjustment_type="raw")
    rows = []
    for row in result.get("rows", []):
        rows.append({column: row.get(column) for column in DAILY_PRICE_HISTORY_COLUMNS})
    frame = pd.DataFrame(rows, columns=DAILY_PRICE_HISTORY_COLUMNS)
    if not frame.empty:
        frame["symbol"] = frame["symbol"].map(normalize_symbol)
        frame = frame.drop_duplicates(["date", "symbol"]).sort_values(["date", "symbol"])
    dirs = history_dirs(paths)
    parquet_path = dirs["market_history"] / "daily_price_history_panel.parquet"
    write_frame(frame, parquet_path)
    manifest = _manifest(frame, result, parquet_path, start_date, end_date)
    manifest_path = dirs["market_history"] / "daily_price_history_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}


def _manifest(frame: pd.DataFrame, result: dict[str, Any], parquet_path, start_date: str, end_date: str) -> dict[str, Any]:
    attempted = result.get("attempted_symbols", [])
    failed = result.get("failed_symbols", [])
    return {
        "manifest_id": "A-SHARE-DAILY-PRICE-HISTORY-MANIFEST",
        "target_version": HISTORICAL_TARGET_VERSION,
        "start_date": start_date,
        "end_date": end_date,
        "provider": result.get("provider", ""),
        "providers_attempted": [result.get("provider", "")] if result.get("provider") else [],
        "providers_succeeded": [result.get("provider", "")] if not frame.empty else [],
        "providers_failed": failed,
        "external_api_called": bool(result.get("external_api_called")),
        "real_time_market_data_downloaded": False,
        "attempted_symbols": len(attempted),
        "failed_symbols": len(failed),
        "rows": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "date_count": int(frame["date"].nunique()) if not frame.empty else 0,
        "min_date": str(frame["date"].min()) if not frame.empty else "",
        "max_date": str(frame["date"].max()) if not frame.empty else "",
        "duplicate_rows": int(frame.duplicated(["date", "symbol"]).sum()) if not frame.empty else 0,
        "non_positive_prices": int(((frame[["open", "high", "low", "close"]] <= 0).any(axis=1)).sum()) if not frame.empty else 0,
        "high_low_inversion": int((frame["high"] < frame["low"]).sum()) if not frame.empty else 0,
        "volume_negative": int((frame["volume"].fillna(0) < 0).sum()) if not frame.empty else 0,
        "amount_negative": int((frame["amount"].fillna(0) < 0).sum()) if not frame.empty else 0,
        "path": str(parquet_path),
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
