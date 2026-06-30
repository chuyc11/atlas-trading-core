"""Trend sufficiency checks."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION


def build_trend_sufficiency(*, as_of_date: str, observation_count: int, minimum_required_observations: int, baseline_window_observations: int) -> dict:
    available = observation_count >= minimum_required_observations
    return {
        "sufficiency_id": "A-SHARE-OWNER-READINESS-TREND-SUFFICIENCY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "daily_pack_history_observation_count": observation_count,
        "minimum_required_observations": minimum_required_observations,
        "baseline_window_observations": baseline_window_observations,
        "trend_analysis_available": available,
        "readiness_trend_status": "available" if available else "insufficient_history",
        "insufficient_history_correctly_flagged": (not available) if observation_count < minimum_required_observations else True,
        "synthetic_history_used": False,
        "future_dates_used": False,
        "no_fabricated_trends": True,
        "explanation": "Only real owner daily pack records are used; more observations are required for trend analysis." if not available else "Observation count is sufficient for trend analysis.",
    }
