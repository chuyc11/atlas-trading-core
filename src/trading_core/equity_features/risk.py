"""Risk feature helpers for A-share feature engineering."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from trading_core.equity_features.returns import annualized_return, daily_returns, pct_return


def volatility(values: np.ndarray, window: int, *, annualize: bool = False) -> float | None:
    returns = _window_returns(values, window)
    if len(returns) < 2:
        return None
    vol = float(np.std(returns, ddof=1))
    return vol * math.sqrt(252) if annualize else vol


def downside_volatility(values: np.ndarray, window: int) -> float | None:
    returns = _window_returns(values, window)
    if len(returns) == 0:
        return None
    downside = returns[returns < 0]
    if len(downside) < 2:
        return 0.0
    return float(np.std(downside, ddof=1))


def max_drawdown(values: np.ndarray, window: int) -> float | None:
    if len(values) < 2:
        return None
    data = np.asarray(values[-window:], dtype=float) if len(values) >= window else np.asarray(values, dtype=float)
    data = data[np.isfinite(data)]
    if len(data) < 2:
        return None
    running_max = np.maximum.accumulate(data)
    with np.errstate(divide="ignore", invalid="ignore"):
        drawdowns = data / running_max - 1.0
    drawdowns = drawdowns[np.isfinite(drawdowns)]
    return float(drawdowns.min()) if len(drawdowns) else None


def value_at_risk(values: np.ndarray, window: int, quantile: float = 0.05) -> float | None:
    returns = _window_returns(values, window)
    if len(returns) == 0:
        return None
    return float(np.quantile(returns, quantile))


def expected_shortfall(values: np.ndarray, window: int, quantile: float = 0.05) -> float | None:
    returns = _window_returns(values, window)
    if len(returns) == 0:
        return None
    threshold = np.quantile(returns, quantile)
    tail = returns[returns <= threshold]
    return float(tail.mean()) if len(tail) else None


def skewness(values: np.ndarray, window: int) -> float | None:
    returns = pd.Series(_window_returns(values, window))
    if len(returns) < 3:
        return None
    result = returns.skew()
    return float(result) if pd.notna(result) else None


def kurtosis(values: np.ndarray, window: int) -> float | None:
    returns = pd.Series(_window_returns(values, window))
    if len(returns) < 4:
        return None
    result = returns.kurt()
    return float(result) if pd.notna(result) else None


def calmar_250d(values: np.ndarray) -> float | None:
    ret = annualized_return(pct_return(values, 250), 250)
    dd = max_drawdown(values, 250)
    if ret is None or dd in (None, 0):
        return None
    return ret / abs(dd)


def _window_returns(values: np.ndarray, window: int) -> np.ndarray:
    if len(values) < 2:
        return np.array([], dtype=float)
    tail = np.asarray(values[-window - 1 :], dtype=float) if len(values) > window else np.asarray(values, dtype=float)
    return daily_returns(tail)
