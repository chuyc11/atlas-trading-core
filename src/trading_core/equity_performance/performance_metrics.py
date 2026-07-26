"""Portfolio performance metric snapshots."""

from __future__ import annotations

import math
from statistics import mean, stdev
from typing import Any

from trading_core.equity_performance.performance_config import BENCHMARK_IDS, PERFORMANCE_FLAGS, PerformanceConfig


def build_performance_metric_snapshot(
    *,
    config: PerformanceConfig,
    return_series: dict[str, Any],
    drawdown_series: dict[str, Any],
    relative_series: dict[str, Any],
) -> dict[str, Any]:
    returns_by_portfolio = _by(return_series.get("records", []), "portfolio_id")
    drawdown_by_portfolio = _by(drawdown_series.get("records", []), "portfolio_id")
    relative_by_pair = _relative_by_pair(relative_series.get("records", []))
    portfolios: dict[str, Any] = {}
    for portfolio_id, rows in returns_by_portfolio.items():
        sorted_rows = sorted(rows, key=lambda row: row["as_of_date"])
        observation_count = len(sorted_rows)
        daily_returns = [float(row["daily_return"]) for row in sorted_rows]
        drawdowns = [float(row["drawdown"]) for row in drawdown_by_portfolio.get(portfolio_id, [])]
        portfolios[portfolio_id] = {
            "observation_count": observation_count,
            "minimum_required_observations": config.minimum_required_observations,
            "sufficient_history": observation_count >= config.minimum_required_observations,
            "metric_status": _status(config, observation_count),
            "daily_return_latest": daily_returns[-1] if daily_returns else None,
            "cumulative_return_latest": float(sorted_rows[-1]["cumulative_return"]) if sorted_rows else None,
            "max_drawdown_latest": min(drawdowns) if drawdowns else None,
            "rolling_volatility": _metric_or_insufficient(_rolling_volatility(daily_returns[-config.rolling_window_days :]), config, observation_count),
            "rolling_drawdown_statistics": _metric_or_insufficient(_drawdown_stats(drawdowns[-config.rolling_window_days :]), config, observation_count),
            "benchmark_metrics": {
                benchmark_id: _benchmark_metrics(
                    config=config,
                    observation_count=observation_count,
                    rows=relative_by_pair.get((portfolio_id, benchmark_id), []),
                )
                for benchmark_id in BENCHMARK_IDS
            },
            "first_day_initialization": observation_count == 1,
            "performance_not_yet_observed": observation_count < config.minimum_required_observations,
            **PERFORMANCE_FLAGS,
        }
    return {
        "snapshot_id": "A-SHARE-PERFORMANCE-METRIC-SNAPSHOT",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "mode": config.mode,
        "portfolios": portfolios,
        "minimum_required_observations": config.minimum_required_observations,
        "rolling_window_days": config.rolling_window_days,
        "sufficient_history": all(row["sufficient_history"] for row in portfolios.values()) if portfolios else False,
        "insufficient_history": any(not row["sufficient_history"] for row in portfolios.values()) if portfolios else True,
        **PERFORMANCE_FLAGS,
    }


def _benchmark_metrics(*, config: PerformanceConfig, observation_count: int, rows: list[dict[str, Any]]) -> dict[str, Any]:
    excess = [float(row["excess_daily_return"]) for row in sorted(rows, key=lambda item: item["as_of_date"])]
    benchmark = [float(row["benchmark_daily_return"]) for row in sorted(rows, key=lambda item: item["as_of_date"])]
    portfolio = [float(row["portfolio_daily_return"]) for row in sorted(rows, key=lambda item: item["as_of_date"])]
    sufficient = observation_count >= config.minimum_required_observations
    return {
        "observation_count": observation_count,
        "metric_status": "available" if sufficient else "insufficient_history",
        "tracking_error": _metric_or_insufficient(_tracking_error(excess), config, observation_count),
        "information_ratio": _metric_or_insufficient(_information_ratio(excess), config, observation_count),
        "correlation": _metric_or_insufficient(_correlation(portfolio, benchmark), config, observation_count),
        "beta": _metric_or_insufficient(_beta(portfolio, benchmark), config, observation_count),
    }


def _metric_or_insufficient(value: Any, config: PerformanceConfig, observation_count: int) -> dict[str, Any]:
    if observation_count < config.minimum_required_observations:
        return {
            "metric_status": "insufficient_history",
            "value": None,
            "required_observations": config.minimum_required_observations,
            "available_observations": observation_count,
        }
    return {
        "metric_status": "available",
        "value": value,
        "required_observations": config.minimum_required_observations,
        "available_observations": observation_count,
    }


def _status(config: PerformanceConfig, observation_count: int) -> str:
    return "available" if observation_count >= config.minimum_required_observations else "insufficient_history"


def _rolling_volatility(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    return stdev(values) * math.sqrt(252)


def _drawdown_stats(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    return {"min_drawdown": min(values), "mean_drawdown": mean(values)}


def _tracking_error(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    return stdev(values) * math.sqrt(252)


def _information_ratio(values: list[float]) -> float | None:
    error = _tracking_error(values)
    if error in (None, 0.0):
        return None
    return mean(values) * 252 / error


def _correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right, strict=False))
    denominator = math.sqrt(sum((a - left_mean) ** 2 for a in left) * sum((b - right_mean) ** 2 for b in right))
    return None if denominator == 0.0 else numerator / denominator


def _beta(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    right_mean = mean(right)
    variance = sum((value - right_mean) ** 2 for value in right)
    if variance == 0.0:
        return None
    left_mean = mean(left)
    covariance = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right, strict=False))
    return covariance / variance


def _by(records: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        grouped.setdefault(str(row.get(key)), []).append(row)
    return grouped


def _relative_by_pair(records: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in records:
        grouped.setdefault((str(row.get("portfolio_id")), str(row.get("benchmark_id"))), []).append(row)
    return grouped
