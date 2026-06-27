"""Suspension and missing-price helpers for A-share tradable universe filtering."""

from __future__ import annotations

from typing import Any

import pandas as pd


def valid_price_observation(row: pd.Series | dict[str, Any]) -> bool:
    close = _number(row.get("close"))
    volume = _number(row.get("volume"))
    return close is not None and close > 0 and (volume is None or volume >= 0)


def _number(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "--") or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None

