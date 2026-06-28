"""Portfolio drawdown series construction."""

from __future__ import annotations

from typing import Any

from trading_core.equity_performance.performance_config import PERFORMANCE_FLAGS, PerformanceConfig


def build_portfolio_drawdown_series(config: PerformanceConfig, nav_records: list[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for portfolio_id, rows in _by_portfolio(nav_records).items():
        running_peak = 0.0
        max_drawdown = 0.0
        for idx, row in enumerate(sorted(rows, key=lambda item: item["as_of_date"])):
            nav = float(row["nav"])
            running_peak = max(running_peak, nav)
            drawdown = 0.0 if running_peak == 0.0 else nav / running_peak - 1.0
            max_drawdown = min(max_drawdown, drawdown)
            observation_count = idx + 1
            records.append(
                {
                    "portfolio_key": row.get("portfolio_key"),
                    "portfolio_id": portfolio_id,
                    "as_of_date": row["as_of_date"],
                    "nav": nav,
                    "running_peak_nav": running_peak,
                    "drawdown": drawdown,
                    "max_drawdown": max_drawdown,
                    "observation_count": observation_count,
                    "metric_status": "available" if observation_count >= config.minimum_required_observations else "insufficient_history",
                    "required_observations": config.minimum_required_observations,
                    "available_observations": observation_count,
                    "first_day_initialization": idx == 0,
                    "performance_not_yet_observed": observation_count < config.minimum_required_observations,
                    **PERFORMANCE_FLAGS,
                }
            )
    counts = {portfolio_id: len(rows) for portfolio_id, rows in _by_portfolio(nav_records).items()}
    sufficient = all(count >= config.minimum_required_observations for count in counts.values()) if counts else False
    return {
        "series_id": "A-SHARE-PORTFOLIO-DRAWDOWN-SERIES",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "mode": config.mode,
        "records": sorted(records, key=lambda row: (row["portfolio_id"], row["as_of_date"])),
        "observation_counts": counts,
        "sufficient_history": sufficient,
        "insufficient_history": not sufficient,
        **PERFORMANCE_FLAGS,
    }


def _by_portfolio(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        grouped.setdefault(str(row["portfolio_id"]), []).append(row)
    return grouped
