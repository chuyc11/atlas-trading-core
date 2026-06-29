"""Monitoring status cards."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_monitoring.monitoring_config import MONITORING_FLAGS, TARGET_VERSION


def build_monitoring_status_card(
    *,
    as_of_date: str,
    run_history_snapshot: dict[str, Any],
    warning_trend_snapshot: dict[str, Any],
    blocking_trend_snapshot: dict[str, Any],
    alert_evaluation_result: dict[str, Any],
) -> dict[str, Any]:
    critical = int(alert_evaluation_result.get("critical_alert_count", 0))
    warning_alerts = int(alert_evaluation_result.get("warning_alert_count", 0))
    blockers = int(blocking_trend_snapshot.get("blocking_count_current", 0))
    warnings = int(warning_trend_snapshot.get("warning_count_current", 0))
    if critical or blockers:
        status = "failed"
    elif warning_alerts or warnings:
        status = "passed_with_warnings"
    else:
        status = "passed"
    return {
        "card_id": "MONITORING_STATUS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_monitoring_status": status,
        "run_history_observation_count": run_history_snapshot.get("run_history_observation_count", 0),
        "trend_analysis_available": run_history_snapshot.get("trend_analysis_available") is True,
        "critical_alert_count": critical,
        "warning_alert_count": warning_alerts,
        "known_non_blocking_alert_count": int(alert_evaluation_result.get("known_non_blocking_alert_count", 0)),
        "informational_alert_count": int(alert_evaluation_result.get("informational_alert_count", 0)),
        "blocking_count": blockers,
        "warning_count": warnings,
        "external_notifications_sent": alert_evaluation_result.get("external_notifications_sent") is True,
        **MONITORING_FLAGS,
    }


def build_owner_alert_summary_card(*, as_of_date: str, alert_evaluation_result: dict[str, Any]) -> dict[str, Any]:
    events = list(alert_evaluation_result.get("events", []))
    return {
        "card_id": "OWNER_ALERT_SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "critical_alerts": [event for event in events if event.get("severity") == "critical" and event.get("status") == "triggered"],
        "warning_alerts": [event for event in events if event.get("severity") == "warning" and event.get("status") == "triggered"],
        "known_non_blocking_alerts": [event for event in events if event.get("severity") == "known_non_blocking" and event.get("status") == "triggered"],
        "informational_alerts": [event for event in events if event.get("severity") == "informational" and event.get("status") == "triggered"],
        "insufficient_history_events": [event for event in events if event.get("status") == "insufficient_history"],
        "owner_action_notes": ["review critical alerts immediately"] if alert_evaluation_result.get("critical_alert_count") else ["monitor local alert artifacts"],
        "external_notifications_sent": False,
    }


def build_run_history_summary_card(*, as_of_date: str, run_history_snapshot: dict[str, Any]) -> dict[str, Any]:
    records = list(run_history_snapshot.get("records", []))
    return {
        "card_id": "RUN_HISTORY_SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "run_history_observation_count": run_history_snapshot.get("run_history_observation_count", 0),
        "trend_analysis_available": run_history_snapshot.get("trend_analysis_available") is True,
        "insufficient_history_for_trends": run_history_snapshot.get("insufficient_history_for_trends") is True,
        "latest_record": run_history_snapshot.get("latest_record"),
        "history_table": [
            {
                "as_of_date": row.get("as_of_date"),
                "overall_status": row.get("overall_status"),
                "warning_count": row.get("warning_count"),
                "blocking_count": row.get("blocking_count"),
                "dashboard_status": row.get("dashboard_status"),
            }
            for row in records
        ],
    }
