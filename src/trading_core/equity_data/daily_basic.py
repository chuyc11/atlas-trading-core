"""Build A-share daily basic panel."""

from __future__ import annotations

import pandas as pd

from trading_core.equity_data_quality.common import DAILY_BASIC_COLUMNS, latest_weekday, normalize_symbol, safe_float, source_timestamp, write_frame, write_json
from trading_core.integrations.public_data.provider_registry import load_or_fetch_snapshot
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def ingest_a_share_daily_basic(*, paths: ProjectPaths | None = None, as_of_date: str | None = None) -> dict:
    paths = default_paths(paths)
    snapshot = load_or_fetch_snapshot(paths)
    day = as_of_date or latest_weekday()
    rows = []
    for item in snapshot.get("rows", []):
        rows.append(
            {
                "date": day,
                "symbol": normalize_symbol(item.get("f12")),
                "total_mv": safe_float(item.get("f20")),
                "circ_mv": safe_float(item.get("f21")),
                "turnover_rate": safe_float(item.get("f8")),
                "volume_ratio": None,
                "pe": safe_float(item.get("f9")),
                "pe_ttm": None,
                "pb": safe_float(item.get("f23")),
                "ps": None,
                "ps_ttm": None,
                "dv_ratio": None,
                "dv_ttm": None,
                "source": snapshot.get("provider", ""),
                "source_timestamp": source_timestamp(snapshot),
            }
        )
    frame = pd.DataFrame(rows, columns=DAILY_BASIC_COLUMNS).drop_duplicates(["date", "symbol"]).sort_values(["date", "symbol"])
    parquet_path = paths.data_dir / "equity_market" / "daily_basic_panel.parquet"
    write_frame(frame, parquet_path)
    manifest = {
        "manifest_id": "A-SHARE-DAILY-BASIC-PANEL-MANIFEST",
        "target_version": "v0.7.1-a-share-full-market-data-ingestion",
        "rows": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "field_coverage": {column: round(float(frame[column].notna().mean()), 6) for column in DAILY_BASIC_COLUMNS if column not in {"date", "symbol", "source", "source_timestamp"}},
        "partial_fields": ["volume_ratio", "pe_ttm", "ps", "ps_ttm", "dv_ratio", "dv_ttm"],
    }
    manifest_path = paths.data_dir / "equity_market" / "daily_basic_panel_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}

