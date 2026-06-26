"""Build A-share adjusted price panel with raw fallback coverage."""

from __future__ import annotations

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
        "coverage_note": "raw prices used as adjusted-price fallback with adj_factor=1.0; true forward/backward adjustment deferred to richer providers",
    }
    manifest_path = paths.data_dir / "equity_market" / "adjusted_price_panel_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}

