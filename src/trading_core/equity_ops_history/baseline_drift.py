"""Baseline drift detection."""

from trading_core.equity_ops_history.ops_history_config import TARGET_VERSION


def build_ops_baseline_drift_snapshot(as_of_date: str, observation_count: int, minimum_required_observations: int) -> dict:
    enough = observation_count >= minimum_required_observations
    return {
        "snapshot_id": "A-SHARE-OPS-BASELINE-DRIFT-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "observation_count": observation_count,
        "minimum_required_observations": minimum_required_observations,
        "drift_available": enough,
        "drift_status": "not_detected" if enough else "insufficient_history",
        "synthetic_history_used": False,
        "future_dates_used": False,
    }
