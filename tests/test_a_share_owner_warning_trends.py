from trading_core.equity_owner_monitoring.warning_trends import build_warning_trend_snapshot


def test_warning_trend_marks_single_observation_insufficient():
    snapshot = build_warning_trend_snapshot(as_of_date="2026-06-26", records=[{"warning_codes": ["w"], "warning_count": 1}], current_warnings=["w"], minimum_history_observations=3)
    assert snapshot["trend_status"] == "insufficient_history"
    assert snapshot["new_warning_codes"] == []
