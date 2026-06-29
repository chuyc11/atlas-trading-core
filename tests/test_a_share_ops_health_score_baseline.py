from trading_core.equity_ops_history.health_score_baseline import build_ops_health_score_baseline


def test_ops_health_score_baseline_waits_for_minimum_history():
    baseline = build_ops_health_score_baseline(as_of_date="2026-06-26", health_history={"records": [{"score": 65, "grade": "C"}]}, minimum_required_observations=5, baseline_window_observations=20)
    assert baseline["baseline_status"] == "insufficient_history"
    assert baseline["average_score"] is None
    assert baseline["latest_score"] == 65

