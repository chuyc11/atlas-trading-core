from trading_core.equity_owner_monitoring.alert_evaluation import evaluate_alert_rules
from trading_core.equity_owner_monitoring.alert_rules import build_alert_rule_config


def test_alert_evaluation_triggers_boundary_violation():
    result = evaluate_alert_rules(
        as_of_date="2026-06-26",
        alert_rule_config=build_alert_rule_config(as_of_date="2026-06-26"),
        monitoring_input_availability={"blocking_reasons": [], "input_audit_checks": {"data_refresh_audit_passed": True, "current_day_run_audit_passed": True, "owner_dashboard_audit_passed": True}, "input_artifacts": []},
        warning_trend_snapshot={"trend_analysis_available": False},
        blocking_trend_snapshot={"blocking_count_current": 0},
        provider_health_trend_snapshot={"insufficient_history": True},
        workflow_health_trend_snapshot={},
        dashboard_health_trend_snapshot={},
        monitoring_boundary_check={"overall_passed": False},
        send_external_notifications=False,
    )
    assert result["critical_alert_count"] >= 1
    assert any(event["rule_id"] == "BOUNDARY_VIOLATION" and event["status"] == "triggered" for event in result["events"])
