from trading_core.equity_owner_monitoring.monitoring_cards import build_monitoring_status_card


def test_monitoring_status_card_passes_with_source_warnings():
    card = build_monitoring_status_card(as_of_date="2026-06-26", run_history_snapshot={"run_history_observation_count": 1, "trend_analysis_available": False}, warning_trend_snapshot={"warning_count_current": 2}, blocking_trend_snapshot={"blocking_count_current": 0}, alert_evaluation_result={"critical_alert_count": 0, "warning_alert_count": 0, "known_non_blocking_alert_count": 0, "informational_alert_count": 0, "external_notifications_sent": False})
    assert card["overall_monitoring_status"] == "passed_with_warnings"
    assert card["not_order_instruction"] is True
