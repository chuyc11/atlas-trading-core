"""Benchmark comparison placeholders for first-day virtual tracking."""

from __future__ import annotations

from typing import Any

from trading_core.equity_portfolio_tracking.tracking_config import DEFAULT_BENCHMARKS, PORTFOLIO_HORIZONS, PORTFOLIO_IDS, TARGET_VERSION, TRACKING_BOUNDARY, TRACKING_FLAGS, TrackingConfig


def build_benchmark_comparison_snapshot(
    *,
    config: TrackingConfig,
    performance_snapshot: dict[str, Any],
    benchmarks: list[str] | None = None,
) -> dict[str, Any]:
    benchmarks = benchmarks or DEFAULT_BENCHMARKS
    records = []
    for key, performance in performance_snapshot.get("portfolios", {}).items():
        portfolio_return = float(performance.get("cumulative_return") or 0.0)
        for benchmark in benchmarks:
            available = benchmark in {"CASH", "EQUAL_WEIGHT_PORTFOLIO"}
            benchmark_return = 0.0 if available else None
            records.append(
                {
                    "target_version": TARGET_VERSION,
                    "as_of_date": config.as_of_date,
                    "portfolio_id": PORTFOLIO_IDS[key],
                    "portfolio_horizon": PORTFOLIO_HORIZONS[key],
                    "benchmark": benchmark,
                    "portfolio_return": portfolio_return,
                    "benchmark_return": benchmark_return,
                    "excess_return": portfolio_return - benchmark_return if benchmark_return is not None else None,
                    "tracking_start_date": config.ledger_start_date,
                    "tracking_end_date": config.as_of_date,
                    "benchmark_data_available": available,
                    "benchmark_gap_reason": "" if available else "benchmark price series not available in local v0.7.8 tracking inputs; placeholder retained without fabricated returns",
                    "first_day_initialization": True,
                    "performance_not_yet_observed": True,
                    **TRACKING_FLAGS,
                }
            )
    return {
        "snapshot_id": "A-SHARE-VIRTUAL-PORTFOLIO-BENCHMARK-COMPARISON-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "benchmarks": benchmarks,
        "records": records,
        "benchmark_data_available": all(record["benchmark_data_available"] for record in records),
        "benchmark_gap_reason": "index benchmark data unavailable for CSI300/CSI500/CSI1000 placeholders" if records else "no benchmark records generated",
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        **TRACKING_FLAGS,
        "boundary": dict(TRACKING_BOUNDARY),
    }
