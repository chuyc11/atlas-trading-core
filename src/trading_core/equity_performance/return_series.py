"""Portfolio return series construction."""

from __future__ import annotations

from typing import Any

from trading_core.equity_performance.performance_config import PERFORMANCE_FLAGS, PerformanceConfig


def build_portfolio_return_series(config: PerformanceConfig, nav_records: list[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for portfolio_id, rows in _by_portfolio(nav_records).items():
        sorted_rows = sorted(rows, key=lambda row: row["as_of_date"])
        start_nav = float(sorted_rows[0]["nav"]) if sorted_rows else 0.0
        previous_nav: float | None = None
        for idx, row in enumerate(sorted_rows):
            nav = float(row["nav"])
            first = idx == 0
            daily_return = 0.0 if first or previous_nav in (None, 0.0) else nav / previous_nav - 1.0
            cumulative_return = 0.0 if not start_nav else nav / start_nav - 1.0
            observation_count = idx + 1
            records.append(
                {
                    "portfolio_key": row.get("portfolio_key"),
                    "portfolio_id": portfolio_id,
                    "as_of_date": row["as_of_date"],
                    "nav": nav,
                    "daily_return": daily_return,
                    "cumulative_return": cumulative_return,
                    "observation_count": observation_count,
                    "metric_status": "available" if observation_count >= config.minimum_required_observations else "insufficient_history",
                    "required_observations": config.minimum_required_observations,
                    "available_observations": observation_count,
                    "first_day_initialization": first,
                    "performance_not_yet_observed": observation_count < config.minimum_required_observations,
                    "source_nav_record": row.get("source_tracking_snapshot"),
                    **PERFORMANCE_FLAGS,
                }
            )
            previous_nav = nav
    counts = {portfolio_id: len(rows) for portfolio_id, rows in _by_portfolio(nav_records).items()}
    sufficient = all(count >= config.minimum_required_observations for count in counts.values()) if counts else False
    return {
        "series_id": "A-SHARE-PORTFOLIO-RETURN-SERIES",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "mode": config.mode,
        "records": sorted(records, key=lambda row: (row["portfolio_id"], row["as_of_date"])),
        "observation_counts": counts,
        "multi_day_performance_available": sufficient,
        "sufficient_history": sufficient,
        "insufficient_history": not sufficient,
        **PERFORMANCE_FLAGS,
    }


def _by_portfolio(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        grouped.setdefault(str(row["portfolio_id"]), []).append(row)
    return grouped
