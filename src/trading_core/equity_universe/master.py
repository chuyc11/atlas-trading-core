"""Build A-share equity master."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import EQUITY_MASTER_COLUMNS, board_for_symbol, exchange_for_symbol, markdown_boundary, normalize_date, normalize_symbol, safe_float, source_timestamp, write_frame
from trading_core.integrations.public_data.provider_registry import load_or_fetch_snapshot
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_a_share_equity_master(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    snapshot = load_or_fetch_snapshot(paths)
    rows = []
    for item in snapshot.get("rows", []):
        symbol = normalize_symbol(item.get("f12"))
        name = str(item.get("f14") or "")
        board = board_for_symbol(symbol)
        rows.append(
            {
                "symbol": symbol,
                "exchange": exchange_for_symbol(symbol),
                "market": "A_SHARE",
                "name": name,
                "list_date": normalize_date(item.get("f26")),
                "delist_date": "",
                "board": board,
                "is_active": safe_float(item.get("f2")) is not None,
                "is_st": "ST" in name.upper(),
                "is_star_market": board == "STAR",
                "is_chinext": board == "CHINEXT",
                "is_bse": board == "BSE",
                "currency": "CNY",
                "source": snapshot.get("provider", ""),
                "source_timestamp": source_timestamp(snapshot),
            }
        )
    frame = pd.DataFrame(rows, columns=EQUITY_MASTER_COLUMNS).drop_duplicates("symbol").sort_values("symbol")
    parquet_path = paths.data_dir / "equity_universe" / "equity_master.parquet"
    json_path = paths.data_dir / "equity_universe" / "equity_master.json"
    write_frame(frame, parquet_path, json_path)
    report_path = paths.outputs_dir / "equity_universe" / "A_SHARE_EQUITY_MASTER.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown(frame, snapshot), encoding="utf-8")
    return {
        "artifact_id": "A-SHARE-EQUITY-MASTER",
        "target_version": "v0.7.1-a-share-full-market-data-ingestion",
        "symbols": int(len(frame)),
        "exchanges": sorted(frame["exchange"].dropna().unique().tolist()) if not frame.empty else [],
        "parquet_path": str(parquet_path),
        "json_path": str(json_path),
        "report_path": str(report_path),
        "source": snapshot.get("provider", ""),
    }


def _markdown(frame: pd.DataFrame, snapshot: dict[str, Any]) -> str:
    lines = [
        "# A-Share Equity Master",
        "",
        f"- source: {snapshot.get('provider', '')}",
        f"- symbols: {len(frame)}",
        f"- exchanges: {', '.join(sorted(frame['exchange'].dropna().unique().tolist())) if not frame.empty else ''}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return "\n".join(lines)

