"""Backfill A-share daily price history panel."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import DAILY_PRICE_HISTORY_COLUMNS, HISTORICAL_BOUNDARY, HISTORICAL_TARGET_VERSION, normalize_symbol, read_frame, sha256_file, utc_now, write_frame, write_json
from trading_core.equity_data_quality.history_manifest import history_dirs
from trading_core.integrations.public_data.historical_provider_fallback import fetch_price_history_with_fallback
from trading_core.integrations.public_data.historical_provider_registry import select_history_symbols
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def backfill_a_share_daily_price_history(
    *,
    start_date: str,
    end_date: str,
    paths: ProjectPaths | None = None,
    provider_result: dict[str, Any] | None = None,
    max_symbols: int | None = None,
    provider_priority: str | list[str] | None = None,
    retry: int = 2,
    rate_limit_per_minute: int | None = None,
    merge_existing: bool = False,
) -> dict[str, Any]:
    paths = default_paths(paths)
    symbols = select_history_symbols(paths, max_symbols=max_symbols)
    result = provider_result or fetch_price_history_with_fallback(
        symbols,
        start_date=start_date,
        end_date=end_date,
        adjustment_type="raw",
        provider_priority=provider_priority,
        retry=retry,
        rate_limit_per_minute=rate_limit_per_minute,
        paths=paths,
    )
    rows = []
    for row in result.get("rows", []):
        rows.append({column: row.get(column) for column in DAILY_PRICE_HISTORY_COLUMNS})
    frame = pd.DataFrame(rows, columns=DAILY_PRICE_HISTORY_COLUMNS)
    if merge_existing:
        existing = read_frame(history_dirs(paths)["market_history"] / "daily_price_history_panel.parquet")
        if frame.empty and not existing.empty:
            frame = existing[DAILY_PRICE_HISTORY_COLUMNS]
    if not frame.empty:
        frame["symbol"] = frame["symbol"].map(normalize_symbol)
        frame = frame[(frame["date"] >= start_date) & (frame["date"] <= end_date)]
        if merge_existing:
            if not existing.empty:
                frame = pd.concat([existing[DAILY_PRICE_HISTORY_COLUMNS], frame], ignore_index=True)
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
    provider_breakdown = result.get("provider_breakdown") or {
        str(result.get("provider", "")): {
            "attempted_symbol_count": len(attempted),
            "succeeded_symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
            "failed_symbol_count": len(failed),
        }
    }
    providers_attempted = result.get("providers_attempted") or ([result.get("provider", "")] if result.get("provider") else [])
    providers_succeeded = result.get("providers_succeeded") or ([result.get("provider", "")] if not frame.empty and result.get("provider") else [])
    source_symbols_total = len(attempted)
    symbols_succeeded = int(frame["symbol"].nunique()) if not frame.empty else 0
    return {
        "manifest_id": "A-SHARE-DAILY-PRICE-HISTORY-MANIFEST",
        "target_version": HISTORICAL_TARGET_VERSION,
        "source_universe": "data/equity_universe/equity_master.parquet",
        "source_symbols_total": source_symbols_total,
        "start_date": start_date,
        "end_date": end_date,
        "provider": result.get("provider", ""),
        "providers_attempted": providers_attempted,
        "providers_succeeded": providers_succeeded,
        "providers_failed": failed,
        "provider_breakdown": provider_breakdown,
        "external_api_called": bool(result.get("external_api_called")),
        "real_time_market_data_downloaded": False,
        "attempted_symbols": source_symbols_total,
        "symbols_attempted": source_symbols_total,
        "symbols_succeeded": symbols_succeeded,
        "failed_symbols": len(failed),
        "rows": int(len(frame)),
        "rows_total": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "date_count": int(frame["date"].nunique()) if not frame.empty else 0,
        "trading_days": int(frame["date"].nunique()) if not frame.empty else 0,
        "min_date": str(frame["date"].min()) if not frame.empty else "",
        "max_date": str(frame["date"].max()) if not frame.empty else "",
        "duplicate_rows": int(frame.duplicated(["date", "symbol"]).sum()) if not frame.empty else 0,
        "non_positive_prices": int(((frame[["open", "high", "low", "close"]] <= 0).any(axis=1)).sum()) if not frame.empty else 0,
        "high_low_inversion": int((frame["high"] < frame["low"]).sum()) if not frame.empty else 0,
        "volume_negative": int((frame["volume"].fillna(0) < 0).sum()) if not frame.empty else 0,
        "amount_negative": int((frame["amount"].fillna(0) < 0).sum()) if not frame.empty else 0,
        "path": str(parquet_path),
        "hash": sha256_file(parquet_path),
        "created_at": utc_now(),
        "symbol_limit_detected": bool(source_symbols_total and symbols_succeeded < source_symbols_total),
        "sample_mode": bool(source_symbols_total <= 10),
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
