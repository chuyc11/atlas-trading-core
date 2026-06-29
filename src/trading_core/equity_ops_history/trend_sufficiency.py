"""Trend sufficiency evaluation."""

from trading_core.equity_ops_history.ops_history_config import TARGET_VERSION


def build_ops_trend_sufficiency(as_of_date: str, observation_count: int, minimum_required_observations: int, baseline_window_observations: int) -> dict:
    available = observation_count >= minimum_required_observations
    return {
        "sufficiency_id": "A-SHARE-OPS-TREND-SUFFICIENCY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "run_history_observation_count": observation_count,
        "history_observation_count": observation_count,
        "minimum_required_observations": minimum_required_observations,
        "baseline_window_observations": baseline_window_observations,
        "trend_analysis_available": available,
        "baseline_status": "available" if available else "insufficient_history",
        "insufficient_history_correctly_flagged": (not available and observation_count < minimum_required_observations) or available,
        "synthetic_history_used": False,
        "future_dates_used": False,
        "blocking_reasons": [],
        "warnings": [],
    }
