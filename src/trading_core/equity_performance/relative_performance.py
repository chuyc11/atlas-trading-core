"""Benchmark-relative performance series."""

from __future__ import annotations

from typing import Any

from trading_core.equity_performance.performance_config import BENCHMARK_IDS, PERFORMANCE_FLAGS, PORTFOLIO_IDS, PORTFOLIO_KEYS, PerformanceConfig


def build_relative_performance_series(
    *,
    config: PerformanceConfig,
    return_series: dict[str, Any],
    drawdown_series: dict[str, Any],
    benchmark_nav_snapshot: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    return_records = return_series.get("records", [])
    drawdown_map = {
        (row["portfolio_id"], row["as_of_date"]): row
        for row in drawdown_series.get("records", [])
    }
    portfolio_dates = sorted({row["as_of_date"] for row in return_records})
    benchmark_common = _benchmark_common_series(benchmark_nav_snapshot, portfolio_dates)
    records: list[dict[str, Any]] = []
    latest_by_pair: dict[str, dict[str, Any]] = {}
    for row in return_records:
        portfolio_id = row["portfolio_id"]
        portfolio_drawdown = float(drawdown_map.get((portfolio_id, row["as_of_date"]), {}).get("drawdown") or 0.0)
        for benchmark_id in BENCHMARK_IDS:
            benchmark = benchmark_common.get((benchmark_id, row["as_of_date"]), {})
            observation_count = int(row["observation_count"])
            status = "available" if observation_count >= config.minimum_required_observations and benchmark else "insufficient_history"
            benchmark_cumulative = float(benchmark.get("benchmark_cumulative_return") or 0.0)
            portfolio_cumulative = float(row["cumulative_return"])
            relative_drawdown = (1.0 + portfolio_cumulative) / (1.0 + benchmark_cumulative) - 1.0 if (1.0 + benchmark_cumulative) else 0.0
            record = {
                "portfolio_key": row.get("portfolio_key"),
                "portfolio_id": portfolio_id,
                "benchmark_id": benchmark_id,
                "as_of_date": row["as_of_date"],
                "portfolio_daily_return": float(row["daily_return"]),
                "benchmark_daily_return": float(benchmark.get("benchmark_daily_return") or 0.0),
                "excess_daily_return": float(row["daily_return"]) - float(benchmark.get("benchmark_daily_return") or 0.0),
                "portfolio_cumulative_return": portfolio_cumulative,
                "benchmark_cumulative_return": benchmark_cumulative,
                "excess_cumulative_return": portfolio_cumulative - benchmark_cumulative,
                "portfolio_drawdown": portfolio_drawdown,
                "benchmark_drawdown": float(benchmark.get("benchmark_drawdown") or 0.0),
                "relative_drawdown": relative_drawdown,
                "observation_count": observation_count,
                "metric_status": status,
                "required_observations": config.minimum_required_observations,
                "available_observations": observation_count,
                "performance_not_yet_observed": observation_count < config.minimum_required_observations,
                "do_not_overinterpret_excess_return": observation_count < config.minimum_required_observations,
                **PERFORMANCE_FLAGS,
            }
            records.append(record)
            latest_by_pair[f"{portfolio_id}:{benchmark_id}"] = record
    status_by_portfolio = {
        PORTFOLIO_IDS[key]: {
            benchmark_id: latest_by_pair.get(f"{PORTFOLIO_IDS[key]}:{benchmark_id}", {}).get("metric_status", "missing")
            for benchmark_id in BENCHMARK_IDS
        }
        for key in PORTFOLIO_KEYS
    }
    sufficient = all(row.get("metric_status") == "available" for row in records) if records else False
    relative = {
        "series_id": "A-SHARE-PORTFOLIO-RELATIVE-PERFORMANCE-SERIES",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "mode": config.mode,
        "records": sorted(records, key=lambda item: (item["portfolio_id"], item["benchmark_id"], item["as_of_date"])),
        "comparison_status": status_by_portfolio,
        "relative_performance_available": sufficient,
        "limited_history_flagged": not sufficient,
        "performance_not_yet_observed": not sufficient,
        "benchmark_metrics_do_not_fabricate_portfolio_history": True,
        **PERFORMANCE_FLAGS,
    }
    benchmark_relative = {
        "series_id": "A-SHARE-PORTFOLIO-BENCHMARK-RELATIVE-SERIES",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "benchmark_ids": list(BENCHMARK_IDS),
        "portfolio_ids": [PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS],
        "latest_records": [latest_by_pair[key] for key in sorted(latest_by_pair)],
        "records": relative["records"],
        "sufficient_history": sufficient,
        "insufficient_history": not sufficient,
        "performance_not_fabricated": True,
        **PERFORMANCE_FLAGS,
    }
    return relative, benchmark_relative


def _benchmark_common_series(benchmark_nav_snapshot: dict[str, Any], dates: list[str]) -> dict[tuple[str, str], dict[str, Any]]:
    by_benchmark_date = {
        (row.get("benchmark_id"), row.get("date")): row
        for row in benchmark_nav_snapshot.get("records", [])
    }
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for benchmark_id in BENCHMARK_IDS:
        first_nav: float | None = None
        previous_nav: float | None = None
        running_peak = 0.0
        max_drawdown = 0.0
        for idx, day in enumerate(dates):
            source = by_benchmark_date.get((benchmark_id, day), {})
            nav = float(source.get("benchmark_nav") or 1.0)
            if first_nav is None:
                first_nav = nav
            daily = 0.0 if idx == 0 or previous_nav in (None, 0.0) else nav / previous_nav - 1.0
            cumulative = 0.0 if not first_nav else nav / first_nav - 1.0
            running_peak = max(running_peak, nav)
            drawdown = 0.0 if running_peak == 0.0 else nav / running_peak - 1.0
            max_drawdown = min(max_drawdown, drawdown)
            result[(benchmark_id, day)] = {
                "benchmark_id": benchmark_id,
                "date": day,
                "benchmark_nav": nav,
                "benchmark_daily_return": daily,
                "benchmark_cumulative_return": cumulative,
                "benchmark_drawdown": drawdown,
                "benchmark_max_drawdown": max_drawdown,
                "source_benchmark_nav_snapshot": bool(source),
            }
            previous_nav = nav
    return result
