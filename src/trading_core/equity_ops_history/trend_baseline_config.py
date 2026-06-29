"""Trend baseline config artifact."""

from trading_core.equity_ops_history.ops_history_config import TARGET_VERSION


def build_ops_trend_baseline_config(as_of_date: str, history_window_days: int, minimum_required_observations: int, baseline_window_observations: int) -> dict:
    return {
        "config_id": "A-SHARE-OPS-TREND-BASELINE-CONFIG",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "history_window_days": history_window_days,
        "minimum_required_observations": minimum_required_observations,
        "baseline_window_observations": baseline_window_observations,
        "allow_synthetic_history": False,
        "allow_future_dates": False,
    }
