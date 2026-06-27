"""Market-cap filter helpers for A-share tradable universe filtering."""

from __future__ import annotations

from typing import Any

import pandas as pd


def normalize_market_cap(total_mv: Any, circ_mv: Any, source: str = "") -> tuple[float | None, float | None, bool, bool]:
    total = _number(total_mv)
    circ = _number(circ_mv)
    if total is None and circ is None:
        return None, None, False, False
    source_lower = source.lower()
    unit_normalized = False
    unit_unknown = False
    if "tushare" in source_lower:
        total = total * 10_000 if total is not None else None
        circ = circ * 10_000 if circ is not None else None
        unit_normalized = True
    elif "qstock" not in source_lower and "eastmoney" not in source_lower:
        largest = max([value for value in [total, circ] if value is not None], default=0.0)
        if 0 < largest < 1_000_000:
            total = total * 10_000 if total is not None else None
            circ = circ * 10_000 if circ is not None else None
            unit_normalized = True
        elif largest <= 0:
            unit_unknown = True
    return total, circ, unit_normalized, unit_unknown


def latest_market_cap_rows(history: pd.DataFrame, snapshot: pd.DataFrame, as_of_date: str) -> tuple[dict[str, dict[str, Any]], bool]:
    rows: dict[str, dict[str, Any]] = {}
    history_used = False
    if not history.empty and {"date", "symbol", "total_mv", "circ_mv"}.issubset(history.columns):
        hist = history[history["date"].astype(str) <= as_of_date].copy()
        hist = hist[hist["total_mv"].notna() | hist["circ_mv"].notna()]
        if not hist.empty:
            history_used = True
            hist = hist.sort_values(["symbol", "date"]).drop_duplicates("symbol", keep="last")
            for item in hist.to_dict(orient="records"):
                rows[str(item["symbol"])] = item
    if not snapshot.empty and {"date", "symbol", "total_mv", "circ_mv"}.issubset(snapshot.columns):
        snap = snapshot[snapshot["date"].astype(str) <= as_of_date].copy()
        snap = snap[snap["total_mv"].notna() | snap["circ_mv"].notna()]
        if not snap.empty:
            snap = snap.sort_values(["symbol", "date"]).drop_duplicates("symbol", keep="last")
            for item in snap.to_dict(orient="records"):
                rows.setdefault(str(item["symbol"]), {**item, "used_daily_basic_snapshot_fallback": True})
    return rows, any(row.get("used_daily_basic_snapshot_fallback") for row in rows.values()) and not history_used


def _number(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "--") or pd.isna(value):
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not pd.notna(number):
        return None
    return number

