"""Liquidity filter helpers for A-share tradable universe filtering."""

from __future__ import annotations

from typing import Any

import pandas as pd


def effective_amount(row: pd.Series | dict[str, Any]) -> tuple[float | None, bool]:
    amount = _number(row.get("amount"))
    if amount is not None:
        return amount, False
    volume = _number(row.get("volume"))
    close = _number(row.get("close"))
    if volume is None or close is None:
        return None, False
    return volume * close, True


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

