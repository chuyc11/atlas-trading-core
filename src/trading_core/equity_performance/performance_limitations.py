"""Performance limitation payloads."""

from __future__ import annotations

from typing import Any

from trading_core.equity_performance.performance_config import PERFORMANCE_FLAGS, PerformanceConfig


def build_performance_limitations(config: PerformanceConfig, data_availability: dict[str, Any]) -> dict[str, Any]:
    sufficient = bool(data_availability.get("sufficient_history"))
    observations = int(data_availability.get("portfolio_observation_count") or 0)
    return {
        "limitations_id": "A-SHARE-MULTI-DAY-PERFORMANCE-LIMITATIONS",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "mode": config.mode,
        "portfolio_observation_count": observations,
        "minimum_required_observations": config.minimum_required_observations,
        "sufficient_history": sufficient,
        "insufficient_history": not sufficient,
        "multi_day_performance_available": sufficient,
        "first_day_initialization": observations == 1,
        "performance_not_yet_observed": not sufficient,
        "limitations": [
            "Current portfolio tracking has limited observations.",
            "First-day initialization is not evidence of strategy performance.",
            "Benchmark history may be available, but portfolio realized virtual history is limited.",
            "No real trades were placed.",
            "No broker was connected.",
            "No buy/sell signal was generated.",
            "No live trading readiness is claimed.",
        ],
        **PERFORMANCE_FLAGS,
    }
