"""Moving-average helpers for A-share feature engineering."""

from __future__ import annotations

import numpy as np

from trading_core.equity_features.returns import safe_number


def moving_average(values: np.ndarray, window: int) -> float | None:
    if len(values) < window:
        return None
    data = np.asarray(values[-window:], dtype=float)
    data = data[np.isfinite(data)]
    return float(data.mean()) if len(data) else None


def close_to_average(close: float | None, average: float | None) -> float | None:
    if close is None or average in (None, 0):
        return None
    return close / average - 1.0


def moving_average_slope(values: np.ndarray, window: int) -> float | None:
    if len(values) < window * 2:
        return None
    current = moving_average(values, window)
    previous = moving_average(values[:-window], window)
    if current is None or previous in (None, 0):
        return None
    return current / previous - 1.0


def trend_consistency(values: np.ndarray, window: int) -> float | None:
    if len(values) <= window:
        return None
    tail = np.asarray(values[-window - 1 :], dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        returns = tail[1:] / tail[:-1] - 1.0
    returns = returns[np.isfinite(returns)]
    return float((returns > 0).mean()) if len(returns) else None


def last_value(values: np.ndarray) -> float | None:
    return safe_number(values[-1]) if len(values) else None

