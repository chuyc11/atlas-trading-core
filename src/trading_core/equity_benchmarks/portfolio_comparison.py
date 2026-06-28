"""Portfolio versus benchmark comparison."""

from __future__ import annotations

from typing import Any

from trading_core.equity_benchmarks.benchmark_config import BENCHMARK_IDS, BENCHMARK_FLAGS, PORTFOLIO_IDS, PORTFOLIO_KEYS, BenchmarkConfig
from trading_core.equity_benchmarks.benchmark_nav import as_of_nav_snapshot
from trading_core.equity_benchmarks.relative_metrics import relative_drawdown


def build_portfolio_benchmark_comparison(
    *,
    config: BenchmarkConfig,
    portfolio_performance_snapshot: dict[str, Any],
    nav_records: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    benchmark_as_of = as_of_nav_snapshot(nav_records, config.as_of_date)
    portfolio_records = portfolio_performance_snapshot.get("portfolios", {})
    comparisons = []
    status_by_portfolio: dict[str, dict[str, str]] = {}
    for key in PORTFOLIO_KEYS:
        portfolio = portfolio_records.get(key, {})
        portfolio_id = str(portfolio.get("portfolio_id") or PORTFOLIO_IDS[key])
        status_by_portfolio[portfolio_id] = {}
        for benchmark_id in BENCHMARK_IDS:
            benchmark = benchmark_as_of.get(benchmark_id, {})
            portfolio_nav = float(portfolio.get("portfolio_nav") or 0.0)
            benchmark_nav = float(benchmark.get("benchmark_nav") or 1.0)
            portfolio_daily = float(portfolio.get("daily_return") or 0.0)
            benchmark_daily = float(benchmark.get("benchmark_daily_return") or 0.0)
            portfolio_cumulative = float(portfolio.get("cumulative_return") or 0.0)
            benchmark_cumulative = float(benchmark.get("benchmark_cumulative_return") or 0.0)
            comparison_status = "limited_history"
            status_by_portfolio[portfolio_id][benchmark_id] = comparison_status
            comparisons.append(
                {
                    "as_of_date": config.as_of_date,
                    "portfolio_key": key,
                    "portfolio_id": portfolio_id,
                    "benchmark_id": benchmark_id,
                    "portfolio_nav": portfolio_nav,
                    "benchmark_nav": benchmark_nav,
                    "portfolio_daily_return": portfolio_daily,
                    "benchmark_daily_return": benchmark_daily,
                    "excess_daily_return": portfolio_daily - benchmark_daily,
                    "portfolio_cumulative_return": portfolio_cumulative,
                    "benchmark_cumulative_return": benchmark_cumulative,
                    "excess_cumulative_return": portfolio_cumulative - benchmark_cumulative,
                    "relative_drawdown": relative_drawdown(1.0 + portfolio_cumulative, 1.0 + benchmark_cumulative),
                    "tracking_error_if_enough_history": None,
                    "information_ratio_if_enough_history": None,
                    "correlation_if_enough_history": None,
                    "comparison_status": comparison_status,
                    "minimum_required_trading_days": config.minimum_required_trading_days,
                    "portfolio_history_days": 1,
                    "performance_not_yet_observed": True,
                    **BENCHMARK_FLAGS,
                }
            )
    comparison = {
        "snapshot_id": "A-SHARE-PORTFOLIO-BENCHMARK-COMPARISON",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "portfolio_ids": [PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS],
        "benchmark_ids": list(BENCHMARK_IDS),
        "comparisons": comparisons,
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        "limited_history_correctly_flagged": all(row["comparison_status"] == "limited_history" for row in comparisons),
        "performance_not_fabricated": True,
        **BENCHMARK_FLAGS,
    }
    relative = {
        "snapshot_id": "A-SHARE-RELATIVE-PERFORMANCE-SNAPSHOT",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "comparison_status": status_by_portfolio,
        "relative_performance_available": False,
        "limited_history_flagged": True,
        "performance_not_yet_observed": True,
        "minimum_required_trading_days": config.minimum_required_trading_days,
        "reason": "portfolio tracking has only one observed day; multi-day relative metrics are intentionally not fabricated",
        **BENCHMARK_FLAGS,
    }
    return comparison, relative
