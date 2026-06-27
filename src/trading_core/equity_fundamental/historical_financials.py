"""Backfill A-share basic financial history panel."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import FINANCIAL_HISTORY_COLUMNS, HISTORICAL_BOUNDARY, HISTORICAL_TARGET_VERSION, write_frame, write_json
from trading_core.equity_data_quality.history_manifest import history_dirs
from trading_core.integrations.public_data.historical_provider_registry import fetch_financial_history
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def backfill_a_share_financial_history(
    *,
    start_date: str,
    end_date: str,
    paths: ProjectPaths | None = None,
    provider_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    result = provider_result or fetch_financial_history(start_date=start_date, end_date=end_date)
    rows = [{column: row.get(column) for column in FINANCIAL_HISTORY_COLUMNS} for row in result.get("rows", [])]
    frame = pd.DataFrame(rows, columns=FINANCIAL_HISTORY_COLUMNS)
    if not frame.empty:
        frame = frame.drop_duplicates(["report_date", "symbol"]).sort_values(["report_date", "symbol"])
    dirs = history_dirs(paths)
    parquet_path = dirs["fundamental_history"] / "basic_financials_history_panel.parquet"
    write_frame(frame, parquet_path)
    numeric_columns = [column for column in FINANCIAL_HISTORY_COLUMNS if column not in {"report_date", "ann_date", "symbol", "source", "source_timestamp", "provider", "ingested_at"}]
    manifest = {
        "manifest_id": "A-SHARE-BASIC-FINANCIALS-HISTORY-MANIFEST",
        "target_version": HISTORICAL_TARGET_VERSION,
        "provider": result.get("provider", ""),
        "providers_attempted": [result.get("provider", "")] if result.get("provider") else [],
        "providers_succeeded": [result.get("provider", "")] if not frame.empty else [],
        "providers_failed": result.get("failed_quarters", []),
        "coverage_note": result.get("coverage_note", ""),
        "external_api_called": bool(result.get("external_api_called")),
        "real_time_market_data_downloaded": False,
        "rows": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "report_date_coverage": int(frame["report_date"].nunique()) if not frame.empty else 0,
        "field_coverage": {column: round(float(frame[column].notna().mean()), 6) if not frame.empty else 0.0 for column in numeric_columns},
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    manifest_path = dirs["fundamental_history"] / "basic_financials_history_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}
