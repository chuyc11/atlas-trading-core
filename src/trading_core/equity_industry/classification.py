"""Build A-share industry classification with board fallback."""

from __future__ import annotations

import pandas as pd

from trading_core.equity_data_quality.common import INDUSTRY_COLUMNS, board_for_symbol, latest_weekday, normalize_symbol, source_timestamp, write_frame, write_json
from trading_core.integrations.public_data.provider_registry import load_or_fetch_snapshot
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def ingest_a_share_industry_classification(*, paths: ProjectPaths | None = None) -> dict:
    paths = default_paths(paths)
    snapshot = load_or_fetch_snapshot(paths)
    rows = []
    for item in snapshot.get("rows", []):
        symbol = normalize_symbol(item.get("f12"))
        board = board_for_symbol(symbol)
        rows.append(
            {
                "symbol": symbol,
                "industry_level_1": "Unclassified",
                "industry_level_2": board,
                "industry_level_3": "",
                "industry_standard": "board_fallback",
                "effective_date": latest_weekday(),
                "source": snapshot.get("provider", ""),
                "source_timestamp": source_timestamp(snapshot),
            }
        )
    frame = pd.DataFrame(rows, columns=INDUSTRY_COLUMNS).drop_duplicates("symbol").sort_values("symbol")
    parquet_path = paths.data_dir / "equity_industry" / "industry_classification.parquet"
    write_frame(frame, parquet_path)
    manifest = {
        "manifest_id": "A-SHARE-INDUSTRY-CLASSIFICATION-MANIFEST",
        "target_version": "v0.7.1-a-share-full-market-data-ingestion",
        "rows": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "industry_standard": "board_fallback",
        "conflict_report": [],
        "coverage_note": "public industry taxonomy not available in v0.7.1 provider snapshot; board-level fallback recorded",
    }
    manifest_path = paths.data_dir / "equity_industry" / "industry_classification_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}

