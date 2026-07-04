"""Build A-share adjusted price panel with raw fallback coverage."""

from __future__ import annotations

import json

import pandas as pd

from trading_core.equity_data.daily_price import ingest_a_share_daily_prices
from trading_core.equity_data_quality.common import ADJUSTED_PRICE_COLUMNS, read_frame, source_timestamp, write_frame, write_json
from trading_core.integrations.public_data.provider_registry import load_or_fetch_snapshot
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def ingest_a_share_adjusted_prices(*, paths: ProjectPaths | None = None) -> dict:
    paths = default_paths(paths)
    daily_path = paths.data_dir / "equity_market" / "daily_price_panel.parquet"
    if not daily_path.exists():
        ingest_a_share_daily_prices(paths=paths)
    daily = read_frame(daily_path)
    snapshot = load_or_fetch_snapshot(paths)
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
            "source": snapshot.get("provider", ""),
            "source_timestamp": source_timestamp(snapshot),
        },
        columns=ADJUSTED_PRICE_COLUMNS,
    )
    parquet_path = paths.data_dir / "equity_market" / "adjusted_price_panel.parquet"
    write_frame(frame, parquet_path)
    manifest = {
        "manifest_id": "A-SHARE-ADJUSTED-PRICE-PANEL-MANIFEST",
        "target_version": "v0.7.1-a-share-full-market-data-ingestion",
        "rows": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "adjustment_types": sorted(frame["adjustment_type"].unique().tolist()) if not frame.empty else [],
        "adjusted_price_status": "raw_fallback" if not frame.empty else "unavailable",
        "true_adjustment_factor_available": False,
        "raw_price_used_as_adjusted_price_fallback": not frame.empty,
        "coverage_note": "raw prices used as explicit adjusted-price fallback with adj_factor=1.0; true forward/backward adjustment is unavailable from current source",
    }
    manifest_path = paths.data_dir / "equity_market" / "adjusted_price_panel_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}


def validate_adjusted_price_status(*, paths: ProjectPaths | None = None, allow_raw_price: bool = False) -> dict:
    paths = default_paths(paths)
    manifest_path = paths.data_dir / "equity_market" / "adjusted_price_panel_manifest.json"
    if not manifest_path.exists():
        return {
            "passed": False,
            "status": "unavailable",
            "adjusted_price_status": "unavailable",
            "degraded": False,
            "allow_raw_price": allow_raw_price,
            "warning": "formal backtest requires adjusted-price status metadata; manifest is missing",
        }
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    status = str(manifest.get("adjusted_price_status", "unavailable"))
    true_factor = bool(manifest.get("true_adjustment_factor_available"))
    raw_fallback = bool(manifest.get("raw_price_used_as_adjusted_price_fallback")) or status == "raw_fallback"
    if true_factor and status not in {"raw_fallback", "unavailable"}:
        return {
            "passed": True,
            "status": "available",
            "adjusted_price_status": status,
            "degraded": False,
            "allow_raw_price": allow_raw_price,
            "warning": None,
        }
    if raw_fallback and allow_raw_price:
        return {
            "passed": True,
            "status": "raw_fallback",
            "adjusted_price_status": status,
            "degraded": True,
            "allow_raw_price": allow_raw_price,
            "warning": "raw prices used as adjusted-price fallback; result is degraded",
        }
    return {
        "passed": False,
        "status": status,
        "adjusted_price_status": status,
        "degraded": raw_fallback,
        "allow_raw_price": allow_raw_price,
        "warning": "formal backtest requires true adjusted prices unless allow_raw_price=true",
    }
