"""Limitations for attribution diagnostics."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION


LIMITATION_TEXT = [
    "Current performance history is limited.",
    "Only one portfolio observation is available unless more dates exist.",
    "Realized multi-day attribution is not yet available.",
    "Current outputs are mainly structural exposure diagnostics.",
    "No real trades were placed.",
    "No broker was connected.",
    "No buy/sell signal was generated.",
    "No live trading readiness is claimed.",
    "Attribution is not investment advice.",
]


def build_attribution_limitations(config: Any, data_availability: dict[str, Any]) -> dict[str, Any]:
    return {
        "limitations_id": "A-SHARE-PERFORMANCE-ATTRIBUTION-LIMITATIONS",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "limited_history": True,
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        "structural_diagnostics_available": True,
        "realized_performance_attribution_available": False,
        "multi_day_performance_attribution_status": "insufficient_history",
        "portfolio_observation_count": data_availability.get("portfolio_observation_count"),
        "minimum_required_observations": data_availability.get("minimum_required_observations"),
        "limitations": list(LIMITATION_TEXT),
        **ATTRIBUTION_FLAGS,
    }
