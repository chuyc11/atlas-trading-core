"""Liquidity feature helpers for A-share feature engineering."""

from __future__ import annotations

import numpy as np


def avg(values: np.ndarray, window: int) -> float | None:
    data = _tail(values, window)
    return float(data.mean()) if len(data) else None


def stability(values: np.ndarray, window: int) -> float | None:
    data = _tail(values, window)
    if len(data) < 2:
        return None
    mean = float(data.mean())
    if mean == 0:
        return None
    return float(data.std(ddof=1) / mean)


def effective_days(values: np.ndarray, window: int) -> int:
    data = _tail(values, window)
    return int((data > 0).sum())


def zero_days(values: np.ndarray, window: int) -> int:
    data = _tail(values, window)
    return int((data <= 0).sum())


def slippage_proxy(amount_values: np.ndarray, window: int) -> float | None:
    amount = avg(amount_values, window)
    if amount is None or amount <= 0:
        return None
    return float(1.0 / np.sqrt(amount / 1_000_000.0))


def _tail(values: np.ndarray, window: int) -> np.ndarray:
    data = np.asarray(values[-window:], dtype=float)
    return data[np.isfinite(data)]

