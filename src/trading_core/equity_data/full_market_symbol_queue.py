"""Full-market A-share symbol queue for historical backfill."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import (
    HISTORICAL_BOUNDARY,
    HISTORICAL_TARGET_VERSION,
    data_quality_dir,
    markdown_boundary,
    normalize_symbol,
    read_frame,
    write_report,
)
from trading_core.equity_data_quality.history_manifest import DEFAULT_END_DATE, DEFAULT_TARGET_START_DATE
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


QUEUE_ID = "A-SHARE-HISTORICAL-BACKFILL-SYMBOL-QUEUE"


def build_a_share_historical_backfill_symbol_queue(
    *,
    paths: ProjectPaths | None = None,
    target_start_date: str = DEFAULT_TARGET_START_DATE,
    end_date: str = DEFAULT_END_DATE,
) -> dict[str, Any]:
    paths = default_paths(paths)
    master_path = paths.data_dir / "equity_universe" / "equity_master.parquet"
    master = read_frame(master_path)
    rows = _queue_rows(master, target_start_date=target_start_date, end_date=end_date)
    frame = pd.DataFrame(rows)
    eligible_price = int(frame["eligible_for_price_backfill"].sum()) if not frame.empty else 0
    eligible_adjusted = int(frame["eligible_for_adjusted_price_backfill"].sum()) if not frame.empty else 0
    eligible_basic = int(frame["eligible_for_daily_basic_backfill"].sum()) if not frame.empty else 0
    ineligible = frame[~frame["eligible_for_price_backfill"]] if not frame.empty else frame
    reasons = ineligible["reason_if_ineligible"].value_counts().to_dict() if not frame.empty else {}
    payload: dict[str, Any] = {
        "queue_id": QUEUE_ID,
        "target_version": HISTORICAL_TARGET_VERSION,
        "source": "data/equity_universe/equity_master.parquet",
        "uses_equity_master_as_source": True,
        "uses_etf_universe": False,
        "uses_fixture_universe": False,
        "target_start_date": target_start_date,
        "end_date": end_date,
        "queue_total_symbols": len(rows),
        "eligible_price_backfill_symbols": eligible_price,
        "eligible_adjusted_price_backfill_symbols": eligible_adjusted,
        "eligible_daily_basic_backfill_symbols": eligible_basic,
        "ineligible_symbols": int(len(ineligible)) if ineligible is not None else 0,
        "ineligible_reasons": {str(key): int(value) for key, value in reasons.items()},
        "symbols": rows,
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    json_path = data_quality_dir(paths) / "a_share_historical_backfill_symbol_queue.json"
    report_path = paths.outputs_dir / "equity_data_quality" / "A_SHARE_HISTORICAL_BACKFILL_SYMBOL_QUEUE.md"
    lines = [
        "# A-Share Historical Backfill Symbol Queue",
        "",
        f"- target_version: {HISTORICAL_TARGET_VERSION}",
        "- source: data/equity_universe/equity_master.parquet",
        f"- queue_total_symbols: {payload['queue_total_symbols']}",
        f"- eligible_price_backfill_symbols: {eligible_price}",
        f"- eligible_adjusted_price_backfill_symbols: {eligible_adjusted}",
        f"- eligible_daily_basic_backfill_symbols: {eligible_basic}",
        f"- ineligible_symbols: {payload['ineligible_symbols']}",
        f"- ineligible_reasons: {payload['ineligible_reasons']}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "- Live trading ready: false.",
        "",
    ]
    return write_report(json_path, payload, report_path, "\n".join(lines))


def load_backfill_queue_symbols(
    paths: ProjectPaths,
    *,
    max_symbols: int | None = None,
    sample_size: int | None = None,
) -> list[str]:
    payload = build_a_share_historical_backfill_symbol_queue(paths=paths)
    rows = payload.get("symbols", [])
    symbols = [row["symbol"] for row in rows if row.get("eligible_for_price_backfill")]
    if sample_size is not None and sample_size > 0:
        return symbols[:sample_size]
    if max_symbols is not None and max_symbols > 0:
        return symbols[:max_symbols]
    return symbols


def _queue_rows(master: pd.DataFrame, *, target_start_date: str, end_date: str) -> list[dict[str, Any]]:
    if master.empty:
        return []
    rows: list[dict[str, Any]] = []
    frame = master.copy()
    frame["symbol"] = frame["symbol"].map(normalize_symbol)
    frame["_is_active_sort"] = frame.get("is_active", True)
    frame["_exchange_sort"] = frame.get("exchange", "").map({"SSE": 0, "SZSE": 1, "BSE": 2}).fillna(9)
    frame = frame.sort_values(["_is_active_sort", "_exchange_sort", "symbol"], ascending=[False, True, True])
    for priority, item in enumerate(frame.to_dict("records"), start=1):
        exchange = str(item.get("exchange") or "")
        is_active = bool(item.get("is_active", True))
        delist_date = str(item.get("delist_date") or "")
        symbol = normalize_symbol(item.get("symbol"))
        reason = ""
        eligible = True
        if not is_active or delist_date:
            eligible = False
            reason = "inactive_or_delisted"
        elif exchange not in {"SSE", "SZSE", "BSE"}:
            eligible = False
            reason = "unsupported_exchange"
        elif exchange == "BSE":
            eligible = False
            reason = "provider_support_unknown_for_bse"
        rows.append(
            {
                "symbol": symbol,
                "exchange": exchange,
                "name": item.get("name", ""),
                "list_date": item.get("list_date", ""),
                "delist_date": delist_date,
                "is_active": is_active,
                "is_st": bool(item.get("is_st", False)),
                "board": item.get("board", ""),
                "priority": priority,
                "expected_start_date": target_start_date,
                "expected_end_date": end_date,
                "eligible_for_price_backfill": eligible,
                "eligible_for_adjusted_price_backfill": eligible,
                "eligible_for_daily_basic_backfill": eligible,
                "reason_if_ineligible": reason,
            }
        )
    return rows
