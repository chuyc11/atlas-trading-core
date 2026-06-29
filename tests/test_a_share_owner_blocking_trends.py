from trading_core.equity_owner_monitoring.blocking_trends import build_blocking_trend_snapshot


def test_blocking_trend_detects_new_blocker_with_enough_history():
    records = [
        {"blocking_codes": [], "blocking_count": 0},
        {"blocking_codes": [], "blocking_count": 0},
        {"blocking_codes": ["x"], "blocking_count": 1},
    ]
    snapshot = build_blocking_trend_snapshot(as_of_date="2026-06-26", records=records, current_blockers=["x"], minimum_history_observations=3)
    assert snapshot["trend_analysis_available"] is True
    assert snapshot["new_blocking_codes"] == ["x"]
