"""Data availability snapshot for attribution diagnostics."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, PORTFOLIO_IDS, PORTFOLIO_KEYS, TARGET_VERSION


def build_attribution_data_availability(config: Any, inputs: Any) -> dict[str, Any]:
    performance_availability = inputs.performance.get("performance_data_availability", {})
    counts = performance_availability.get("portfolio_observation_counts", {})
    source_availability = {key: path.exists() for key, path in inputs.input_paths.items()}
    return {
        "availability_id": "A-SHARE-PERFORMANCE-ATTRIBUTION-DATA-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "portfolio_observation_counts": {PORTFOLIO_IDS[key]: int(counts.get(PORTFOLIO_IDS[key], 0)) for key in PORTFOLIO_KEYS},
        "portfolio_observation_count": int(performance_availability.get("portfolio_observation_count") or min(counts.values() or [0])),
        "minimum_required_observations": config.minimum_required_observations,
        "sufficient_history": False,
        "insufficient_history": True,
        "limited_history": True,
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        "structural_diagnostics_available": True,
        "realized_performance_attribution_available": False,
        "source_artifacts_available": source_availability,
        "all_required_sources_available": all(source_availability.values()),
        **ATTRIBUTION_FLAGS,
    }
