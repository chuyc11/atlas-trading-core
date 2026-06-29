from trading_core.equity_ops_history.history_snapshot import build_ops_history_snapshot


def test_ops_history_snapshot_marks_insufficient_history():
    snapshot = build_ops_history_snapshot(as_of_date="2026-06-26", history_index={"records": [{"as_of_date": "2026-06-26"}]}, minimum_required_observations=5)
    assert snapshot["run_history_observation_count"] == 1
    assert snapshot["trend_analysis_available"] is False
    assert snapshot["baseline_status"] == "insufficient_history"

