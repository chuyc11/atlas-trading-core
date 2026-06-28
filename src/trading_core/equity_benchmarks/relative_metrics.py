"""Relative performance metrics."""

from __future__ import annotations

import math


def tracking_error(excess_returns: list[float]) -> float | None:
    if len(excess_returns) < 2:
        return None
    mean = sum(excess_returns) / len(excess_returns)
    variance = sum((value - mean) ** 2 for value in excess_returns) / (len(excess_returns) - 1)
    return math.sqrt(variance)


def information_ratio(excess_returns: list[float]) -> float | None:
    error = tracking_error(excess_returns)
    if error in (None, 0.0):
        return None
    return (sum(excess_returns) / len(excess_returns)) / error


def correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_var = sum((a - left_mean) ** 2 for a in left)
    right_var = sum((b - right_mean) ** 2 for b in right)
    denominator = math.sqrt(left_var * right_var)
    if denominator == 0.0:
        return None
    return numerator / denominator


def relative_drawdown(portfolio_nav: float, benchmark_nav: float) -> float:
    return float(portfolio_nav) / float(benchmark_nav) - 1.0 if benchmark_nav else 0.0
