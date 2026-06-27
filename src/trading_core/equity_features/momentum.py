"""Momentum helpers for A-share feature engineering."""

from __future__ import annotations

import numpy as np

from trading_core.equity_features.returns import pct_return


def momentum(values: np.ndarray, periods: int) -> float | None:
    return pct_return(values, periods)

