"""Build A-share daily price panel."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import DAILY_PRICE_COLUMNS, latest_weekday, normalize_symbol, safe_float, safe_int, source_timestamp, write_frame, write_json
from trading_core.integrations.public_data.provider_registry import load_or_fetch_snapshot
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def ingest_a_share_daily_prices(*, paths: ProjectPaths | None = None, as_of_date: str | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    snapshot = load_or_fetch_snapshot(paths)
    day = as_of_date or latest_weekday()
    rows = []
    for item in snapshot.get("rows", []):
        symbol = normalize_symbol(item.get("f12"))
        close = safe_float(item.get("f2"))
        open_ = safe_float(item.get("f17"))
        high = safe_float(item.get("f15"))
        low = safe_float(item.get("f16"))
        if close is None or open_ is None or high is None or low is None:
            continue
        rows.append(
            {
                "date": day,
                "symbol": symbol,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": safe_int(item.get("f5")),
                "amount": safe_float(item.get("f6")),
                "turnover": safe_float(item.get("f8")),
                "pre_close": safe_float(item.get("f18")),
                "change": safe_float(item.get("f4")),
                "pct_change": safe_float(item.get("f3")),
                "source": snapshot.get("provider", ""),
                "source_timestamp": source_timestamp(snapshot),
            }
        )
    frame = pd.DataFrame(rows, columns=DAILY_PRICE_COLUMNS).drop_duplicates(["date", "symbol"]).sort_values(["date", "symbol"])
    parquet_path = paths.data_dir / "equity_market" / "daily_price_panel.parquet"
    write_frame(frame, parquet_path)
    manifest = _manifest(frame, snapshot, parquet_path)
    manifest_path = paths.data_dir / "equity_market" / "daily_price_panel_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}


def _manifest(frame: pd.DataFrame, snapshot: dict[str, Any], parquet_path) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-DAILY-PRICE-PANEL-MANIFEST",
        "target_version": "v0.7.1-a-share-full-market-data-ingestion",
        "source": snapshot.get("provider", ""),
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
    }

