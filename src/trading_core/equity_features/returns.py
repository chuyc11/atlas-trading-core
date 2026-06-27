"""Return helpers for A-share feature engineering."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def safe_number(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "--"):
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def pct_return(values: np.ndarray, periods: int) -> float | None:
    if len(values) <= periods:
        return None
    current = safe_number(values[-1])
    previous = safe_number(values[-periods - 1])
    if current is None or previous in (None, 0):
        return None
    return current / previous - 1.0


def daily_returns(values: np.ndarray) -> np.ndarray:
    if len(values) < 2:
        return np.array([], dtype=float)
    series = np.asarray(values, dtype=float)
    previous = series[:-1]
    current = series[1:]
    with np.errstate(divide="ignore", invalid="ignore"):
        returns = current / previous - 1.0
    return returns[np.isfinite(returns)]


def annualized_return(period_return: float | None, periods: int, periods_per_year: int = 252) -> float | None:
    if period_return is None or periods <= 0 or period_return <= -1:
        return None
    return (1.0 + period_return) ** (periods_per_year / periods) - 1.0

