"""Owner alert rule configuration."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_monitoring.monitoring_config import TARGET_VERSION


RULE_DEFINITIONS = [
    ("BLOCKING_AUDIT_FAILURE", "critical", True, False, "Any input or monitoring audit has blocking reasons."),
    ("DATA_REFRESH_FAILURE", "critical", True, False, "The v0.8.0 data refresh audit failed."),
    ("CURRENT_DAY_RUN_FAILURE", "critical", True, False, "The v0.8.1 current-day run audit failed."),
    ("OWNER_DASHBOARD_FAILURE", "critical", True, False, "The v0.8.2 owner dashboard audit failed."),
    ("BOUNDARY_VIOLATION", "critical", True, False, "Monitoring or source boundary check failed."),
    ("BROKER_OR_ORDER_SURFACE_DETECTED", "critical", True, False, "Broker, order, trade, or account surface detected."),
    ("OLD_RUN_DAILY_DETECTED", "critical", True, False, "Old run-daily invocation detected."),
    ("DAY2_EXECUTED_DETECTED", "critical", True, False, "Official forward dry-run day2 execution detected."),
    ("FORBIDDEN_WORDING_DETECTED", "critical", True, False, "Forbidden positive wording detected in monitoring artifacts."),
    ("WARNING_COUNT_INCREASE", "warning", True, True, "Warning count increased versus the previous observation."),
    ("REPEATED_KNOWN_WARNING", "known_non_blocking", True, True, "Known warning repeated across enough observations."),
    ("PROVIDER_HEALTH_DEGRADED", "warning", True, True, "Provider health degraded versus prior observations."),
    ("DATA_FRESHNESS_DEGRADED", "warning", True, True, "Data freshness degraded versus prior observations."),
    ("MISSING_REQUIRED_ARTIFACT", "critical", True, False, "Required monitoring input or output artifact is missing."),
    ("TREND_ANALYSIS_INSUFFICIENT_HISTORY", "informational", True, True, "Trend analysis is unavailable until enough observations exist."),
]


def build_alert_rule_config(*, as_of_date: str) -> dict[str, Any]:
    rules = []
    for rule_id, severity, enabled, requires_history, description in RULE_DEFINITIONS:
        rules.append(
            {
                "rule_id": rule_id,
                "severity": severity,
                "enabled": enabled,
                "source_artifacts": ["monitoring_input_availability", "run_history_snapshot", "warning_trend_snapshot", "monitoring_boundary_check"],
                "condition_description": description,
                "owner_message_template": f"{rule_id}: {description}",
                "blocking": severity == "critical",
                "requires_minimum_history": requires_history,
            }
        )
    return {
        "rule_config_id": "A-SHARE-OWNER-MONITORING-ALERT-RULE-CONFIG",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "severity_enum": ["critical", "warning", "informational", "known_non_blocking"],
        "rules": rules,
    }
