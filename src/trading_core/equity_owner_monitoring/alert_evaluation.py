"""Evaluate owner alert rules locally."""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from trading_core.equity_owner_monitoring.monitoring_config import TARGET_VERSION


def evaluate_alert_rules(
    *,
    as_of_date: str,
    alert_rule_config: dict[str, Any],
    monitoring_input_availability: dict[str, Any],
    warning_trend_snapshot: dict[str, Any],
    blocking_trend_snapshot: dict[str, Any],
    provider_health_trend_snapshot: dict[str, Any],
    workflow_health_trend_snapshot: dict[str, Any],
    dashboard_health_trend_snapshot: dict[str, Any],
    monitoring_boundary_check: dict[str, Any],
    send_external_notifications: bool,
) -> dict[str, Any]:
    events = []
    now = datetime.now(UTC).isoformat()
    for rule in alert_rule_config.get("rules", []):
        status, message, source_stage, source_artifact = _evaluate_rule(
            rule_id=rule["rule_id"],
            input_availability=monitoring_input_availability,
            warning_trend=warning_trend_snapshot,
            blocking_trend=blocking_trend_snapshot,
            provider_health=provider_health_trend_snapshot,
            workflow_health=workflow_health_trend_snapshot,
            dashboard_health=dashboard_health_trend_snapshot,
            boundary=monitoring_boundary_check,
        )
        events.append(
            {
                "alert_id": f"A-SHARE-OWNER-MONITORING-{as_of_date}-{rule['rule_id']}",
                "rule_id": rule["rule_id"],
                "as_of_date": as_of_date,
                "severity": rule["severity"],
                "status": status,
                "source_stage": source_stage,
                "source_artifact": source_artifact,
                "message": message or rule["owner_message_template"],
                "owner_action": "review_monitoring_artifact" if status == "triggered" else "monitor",
                "blocking": bool(rule["blocking"] and status == "triggered"),
                "known_non_blocking": rule["severity"] == "known_non_blocking",
                "created_at": now,
                "external_notification_sent": False,
            }
        )
    triggered = [event for event in events if event["status"] == "triggered"]
    counts = {
        "critical": sum(1 for event in triggered if event["severity"] == "critical"),
        "warning": sum(1 for event in triggered if event["severity"] == "warning"),
        "informational": sum(1 for event in triggered if event["severity"] == "informational"),
        "known_non_blocking": sum(1 for event in triggered if event["severity"] == "known_non_blocking"),
    }
    warnings = ["unsupported_external_notification_request"] if send_external_notifications else []
    return {
        "evaluation_id": "A-SHARE-OWNER-MONITORING-ALERT-EVALUATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "alert_status_enum": ["triggered", "not_triggered", "suppressed", "insufficient_history"],
        "events": events,
        "triggered_alerts": triggered,
        "alert_counts": counts,
        "critical_alert_count": counts["critical"],
        "warning_alert_count": counts["warning"],
        "informational_alert_count": counts["informational"],
        "known_non_blocking_alert_count": counts["known_non_blocking"],
        "external_notifications_requested": send_external_notifications,
        "external_notifications_sent": False,
        "warnings": warnings,
    }


def _evaluate_rule(
    *,
    rule_id: str,
    input_availability: dict[str, Any],
    warning_trend: dict[str, Any],
    blocking_trend: dict[str, Any],
    provider_health: dict[str, Any],
    workflow_health: dict[str, Any],
    dashboard_health: dict[str, Any],
    boundary: dict[str, Any],
) -> tuple[str, str, str, str]:
    if rule_id == "BLOCKING_AUDIT_FAILURE":
        return _trigger(bool(input_availability.get("blocking_reasons") or blocking_trend.get("blocking_count_current")), "blocking audit issue detected", "input_audits", "monitoring_input_availability")
    if rule_id == "DATA_REFRESH_FAILURE":
        passed = input_availability.get("input_audit_checks", {}).get("data_refresh_audit_passed")
        return _trigger(passed is False, "data refresh audit failed", "data_refresh", "a_share_daily_data_refresh_audit")
    if rule_id == "CURRENT_DAY_RUN_FAILURE":
        passed = input_availability.get("input_audit_checks", {}).get("current_day_run_audit_passed")
        return _trigger(passed is False, "current-day run audit failed", "current_day", "a_share_current_day_research_run_audit")
    if rule_id == "OWNER_DASHBOARD_FAILURE":
        passed = input_availability.get("input_audit_checks", {}).get("owner_dashboard_audit_passed")
        return _trigger(passed is False, "owner dashboard audit failed", "owner_dashboard", "a_share_owner_dashboard_audit")
    if rule_id == "BOUNDARY_VIOLATION":
        return _trigger(boundary.get("overall_passed") is False, "monitoring boundary violation detected", "boundary", "monitoring_boundary_check")
    if rule_id == "BROKER_OR_ORDER_SURFACE_DETECTED":
        detected = bool(boundary.get("broker_connected") or boundary.get("real_orders_placed") or boundary.get("order_preview_generated") or boundary.get("forbidden_artifacts_present"))
        return _trigger(detected, "broker or order surface detected", "boundary", "monitoring_boundary_check")
    if rule_id == "OLD_RUN_DAILY_DETECTED":
        return _trigger(bool(boundary.get("old_run_daily_called") or boundary.get("run_daily_called")), "old run-daily detected", "boundary", "monitoring_boundary_check")
    if rule_id == "DAY2_EXECUTED_DETECTED":
        return _trigger(bool(boundary.get("day2_executed")), "day2 execution detected", "boundary", "monitoring_boundary_check")
    if rule_id == "FORBIDDEN_WORDING_DETECTED":
        return _trigger(bool(boundary.get("forbidden_wording_positive_hits")), "forbidden wording detected", "boundary", "monitoring_boundary_check")
    if rule_id == "MISSING_REQUIRED_ARTIFACT":
        missing = any((row.get("required") and not row.get("exists")) for row in input_availability.get("input_artifacts", []))
        return _trigger(missing, "required artifact missing", "inputs", "monitoring_input_availability")
    if rule_id in {"WARNING_COUNT_INCREASE", "REPEATED_KNOWN_WARNING"}:
        if not warning_trend.get("trend_analysis_available"):
            return "insufficient_history", "trend analysis requires more run observations", "warning_trend", "warning_trend_snapshot"
        condition = warning_trend.get("warning_count_change", 0) > 0 if rule_id == "WARNING_COUNT_INCREASE" else bool(warning_trend.get("repeated_warning_codes"))
        return _trigger(condition, f"{rule_id} condition met", "warning_trend", "warning_trend_snapshot")
    if rule_id == "PROVIDER_HEALTH_DEGRADED":
        if provider_health.get("insufficient_history"):
            return "insufficient_history", "provider trend requires more run observations", "provider_health", "provider_health_trend_snapshot"
        return _trigger(bool(provider_health.get("degraded")), "provider health degraded", "provider_health", "provider_health_trend_snapshot")
    if rule_id == "DATA_FRESHNESS_DEGRADED":
        if provider_health.get("insufficient_history"):
            return "insufficient_history", "data freshness trend requires more run observations", "provider_health", "provider_health_trend_snapshot"
        return _trigger(provider_health.get("current_status") == "failed", "data freshness degraded", "provider_health", "provider_health_trend_snapshot")
    if rule_id == "TREND_ANALYSIS_INSUFFICIENT_HISTORY" and not warning_trend.get("trend_analysis_available"):
        return "insufficient_history", "trend analysis intentionally disabled until enough observations exist", "run_history", "run_history_snapshot"
    return "not_triggered", "", "monitoring", "alert_rule_config"


def _trigger(condition: bool, message: str, source_stage: str, source_artifact: str) -> tuple[str, str, str, str]:
    return ("triggered" if condition else "not_triggered", message, source_stage, source_artifact)
