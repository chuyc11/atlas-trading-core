"""Build adjusted price history panel."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history
from trading_core.equity_data_quality.common import ADJUSTED_PRICE_HISTORY_COLUMNS, HISTORICAL_BOUNDARY, HISTORICAL_TARGET_VERSION, read_frame, write_frame, write_json
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
    manifest = {
        "manifest_id": "A-SHARE-ADJUSTED-PRICE-HISTORY-MANIFEST",
        "target_version": HISTORICAL_TARGET_VERSION,
        "rows": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "adjustment_types": sorted(frame["adjustment_type"].dropna().unique().tolist()) if not frame.empty else [],
        "adjustment_conflict_count": 0,
        "coverage_note": "raw price history is used as adjusted-price history fallback; true forward/backward adjustment deferred to richer providers",
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    manifest_path = dirs["market_history"] / "adjusted_price_history_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}
