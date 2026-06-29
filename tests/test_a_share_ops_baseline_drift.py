from trading_core.equity_ops_history.baseline_drift import build_ops_baseline_drift_snapshot


def test_ops_baseline_drift_is_unavailable_with_one_observation():
    drift = build_ops_baseline_drift_snapshot("2026-06-26", 1, 5)
    assert drift["drift_status"] == "insufficient_history"
    assert drift["synthetic_history_used"] is False

