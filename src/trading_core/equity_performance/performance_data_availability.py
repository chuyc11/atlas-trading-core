"""Data availability reporting for performance tracking."""

from __future__ import annotations

from typing import Any

from trading_core.equity_performance.performance_config import BENCHMARK_IDS, PERFORMANCE_FLAGS, PerformanceConfig
from trading_core.equity_performance.performance_inputs import PerformanceInputs


def build_performance_data_availability(
    *,
    config: PerformanceConfig,
    inputs: PerformanceInputs,
    nav_series: dict[str, Any],
    benchmark_nav_snapshot: dict[str, Any],
) -> dict[str, Any]:
    portfolio_counts = dict(nav_series.get("observation_counts", {}))
    benchmark_counts = _benchmark_counts(benchmark_nav_snapshot, config.as_of_date)
    portfolio_dates = {row.get("as_of_date") for row in nav_series.get("records", [])}
    benchmark_dates = {row.get("date") for row in benchmark_nav_snapshot.get("records", []) if row.get("date") <= config.as_of_date}
    common_dates = sorted(day for day in portfolio_dates.intersection(benchmark_dates) if day)
    duplicate_dates = _duplicate_portfolio_dates(nav_series.get("records", []))
    sufficient = bool(portfolio_counts) and min(portfolio_counts.values()) >= config.minimum_required_observations
    return {
        "availability_id": "A-SHARE-MULTI-DAY-PERFORMANCE-DATA-AVAILABILITY",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "mode": config.mode,
        "tracking_snapshots_available": all(key in inputs.tracking_artifacts for key in ["portfolio_nav_snapshot", "portfolio_performance_snapshot"]),
        "benchmark_snapshots_available": all(key in inputs.benchmark_artifacts for key in ["benchmark_return_snapshot", "benchmark_nav_snapshot"]),
        "price_panels_available": inputs.price_panels_available,
        "portfolio_observation_count": min(portfolio_counts.values()) if portfolio_counts else 0,
        "portfolio_observation_counts": portfolio_counts,
        "benchmark_observation_count": min(benchmark_counts.values()) if benchmark_counts else 0,
        "benchmark_observation_counts": benchmark_counts,
        "common_observation_count": len(common_dates),
        "common_observation_dates": common_dates,
        "minimum_required_observations": config.minimum_required_observations,
        "sufficient_history": sufficient,
        "insufficient_history": not sufficient,
        "missing_dates": [],
        "duplicate_dates": duplicate_dates,
        "data_gaps": [],
        "warnings": ["portfolio observation history is below the minimum required window"] if not sufficient else [],
        **PERFORMANCE_FLAGS,
    }


def _benchmark_counts(snapshot: dict[str, Any], as_of_date: str) -> dict[str, int]:
    counts = {benchmark_id: 0 for benchmark_id in BENCHMARK_IDS}
    for row in snapshot.get("records", []):
        benchmark_id = row.get("benchmark_id")
        if benchmark_id in counts and str(row.get("date")) <= as_of_date:
            counts[benchmark_id] += 1
    return counts


def _duplicate_portfolio_dates(records: list[dict[str, Any]]) -> list[str]:
    seen: set[tuple[str, str]] = set()
    duplicates: set[str] = set()
    for row in records:
        key = (str(row.get("portfolio_id")), str(row.get("as_of_date")))
        if key in seen:
            duplicates.add("|".join(key))
        seen.add(key)
    return sorted(duplicates)
