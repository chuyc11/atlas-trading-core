"""Build adjusted price history panel."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history
from trading_core.equity_data_quality.common import ADJUSTED_PRICE_HISTORY_COLUMNS, HISTORICAL_BOUNDARY, HISTORICAL_TARGET_VERSION, read_frame, read_json, sha256_file, utc_now, write_frame, write_json
from trading_core.equity_data_quality.history_manifest import history_dirs
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def backfill_a_share_adjusted_price_history(*, start_date: str, end_date: str, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    dirs = history_dirs(paths)
    daily_path = dirs["market_history"] / "daily_price_history_panel.parquet"
    if not daily_path.exists():
        backfill_a_share_daily_price_history(start_date=start_date, end_date=end_date, paths=paths)
    daily = read_frame(daily_path)
    frame = pd.DataFrame(columns=ADJUSTED_PRICE_HISTORY_COLUMNS)
    if not daily.empty:
        frame = pd.DataFrame(
            {
                "date": daily["date"],
                "symbol": daily["symbol"],
                "adj_open": daily["open"],
                "adj_high": daily["high"],
                "adj_low": daily["low"],
                "adj_close": daily["close"],
                "adj_factor": 1.0,
                "adjustment_type": "raw",
                "source": daily["source"],
                "source_timestamp": daily["source_timestamp"],
                "provider": daily["provider"],
                "ingested_at": daily["ingested_at"],
            },
            columns=ADJUSTED_PRICE_HISTORY_COLUMNS,
        ).drop_duplicates(["date", "symbol", "adjustment_type"]).sort_values(["date", "symbol"])
    parquet_path = dirs["market_history"] / "adjusted_price_history_panel.parquet"
    write_frame(frame, parquet_path)
    price_manifest = read_json(dirs["market_history"] / "daily_price_history_manifest.json")
    manifest = {
        "manifest_id": "A-SHARE-ADJUSTED-PRICE-HISTORY-MANIFEST",
        "target_version": HISTORICAL_TARGET_VERSION,
        "source_symbols_total": price_manifest.get("source_symbols_total", int(daily["symbol"].nunique()) if not daily.empty else 0),
        "symbols_attempted": price_manifest.get("symbols_attempted", int(daily["symbol"].nunique()) if not daily.empty else 0),
        "symbols_succeeded": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "symbols_failed": max(0, int(price_manifest.get("symbols_attempted", 0)) - (int(frame["symbol"].nunique()) if not frame.empty else 0)),
        "rows": int(len(frame)),
        "rows_total": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "min_date": str(frame["date"].min()) if not frame.empty else "",
        "max_date": str(frame["date"].max()) if not frame.empty else "",
        "trading_days": int(frame["date"].nunique()) if not frame.empty else 0,
        "provider_breakdown": price_manifest.get("provider_breakdown", {}),
        "providers_attempted": price_manifest.get("providers_attempted", []),
        "providers_succeeded": price_manifest.get("providers_succeeded", []),
        "providers_failed": price_manifest.get("providers_failed", []),
        "adjustment_types": sorted(frame["adjustment_type"].dropna().unique().tolist()) if not frame.empty else [],
        "adjustment_conflict_count": 0,
        "coverage_note": "raw price history is used as adjusted-price history fallback; true forward/backward adjustment deferred to richer providers",
        "hash": sha256_file(parquet_path),
        "created_at": utc_now(),
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    manifest_path = dirs["market_history"] / "adjusted_price_history_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}
