"""Limit-up and limit-down risk helpers for A-share tradable universe filtering."""

from __future__ import annotations

from typing import Any

import pandas as pd


def estimated_limit_pct(board: str, exchange: str, is_st: bool | None) -> float | None:
    if is_st is None:
        return None
    if is_st:
        return 5.0
    board_text = (board or "").upper()
    exchange_text = (exchange or "").upper()
    if board_text in {"STAR", "CHINEXT", "BSE"} or exchange_text == "BSE":
        return 20.0
    if board_text in {"SSE_MAIN", "SZSE_MAIN"} or exchange_text in {"SSE", "SZSE"}:
        return 10.0
    return None


def detect_limit_status(row: dict[str, Any], *, board: str, exchange: str, is_st: bool | None) -> tuple[bool, bool, bool]:
    limit_pct = estimated_limit_pct(board, exchange, is_st)
    if limit_pct is None:
        return False, False, True
    pct_change = _number(row.get("pct_change"))
    low = _number(row.get("low"))
    high = _number(row.get("high"))
    if pct_change is None or low is None or high is None:
        return False, False, True
    one_word = abs(high - low) <= 1e-9
    return pct_change >= limit_pct - 0.2 and one_word, pct_change <= -limit_pct + 0.2 and one_word, False


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

