"""Build A-share basic financials panel with explicit partial coverage."""

from __future__ import annotations

import pandas as pd

from trading_core.equity_data_quality.common import FINANCIAL_COLUMNS, latest_weekday, normalize_symbol, source_timestamp, write_frame, write_json
from trading_core.integrations.public_data.provider_registry import load_or_fetch_snapshot
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def ingest_a_share_basic_financials(*, paths: ProjectPaths | None = None) -> dict:
    paths = default_paths(paths)
    snapshot = load_or_fetch_snapshot(paths)
    report_date = latest_weekday()
    rows = []
    for item in snapshot.get("rows", []):
        rows.append(
            {
                "report_date": report_date,
                "ann_date": "",
                "symbol": normalize_symbol(item.get("f12")),
                "revenue": None,
                "net_profit": None,
                "roe": None,
                "gross_margin": None,
                "net_margin": None,
                "operating_cash_flow": None,
                "debt_to_asset": None,
                "eps": None,
                "bps": None,
                "source": snapshot.get("provider", ""),
                "source_timestamp": source_timestamp(snapshot),
            }
        )
    frame = pd.DataFrame(rows, columns=FINANCIAL_COLUMNS).drop_duplicates(["report_date", "symbol"]).sort_values(["report_date", "symbol"])
    parquet_path = paths.data_dir / "equity_fundamental" / "basic_financials_panel.parquet"
    write_frame(frame, parquet_path)
    numeric_columns = [column for column in FINANCIAL_COLUMNS if column not in {"report_date", "ann_date", "symbol", "source", "source_timestamp"}]
    manifest = {
        "manifest_id": "A-SHARE-BASIC-FINANCIALS-MANIFEST",
        "target_version": "v0.7.1-a-share-full-market-data-ingestion",
        "rows": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "report_date_coverage": int(frame["report_date"].nunique()) if not frame.empty else 0,
        "field_coverage": {column: round(float(frame[column].notna().mean()), 6) for column in numeric_columns},
        "coverage_note": "basic financial fields are present as nullable schema placeholders; richer free-source financial ingestion is deferred",
    }
    manifest_path = paths.data_dir / "equity_fundamental" / "basic_financials_manifest.json"
    write_json(manifest_path, manifest)
    return {**manifest, "parquet_path": str(parquet_path), "manifest_path": str(manifest_path)}
