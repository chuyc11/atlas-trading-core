"""Escalation workflow artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, FORBIDDEN_ROUTES, TARGET_VERSION


def build_exception_severity_matrix(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "matrix_id": "A-SHARE-EXCEPTION-SEVERITY-MATRIX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "severity_levels": ["info", "warning", "owner_review_required", "developer_follow_up_required", "blocking"],
        "blocking_requires_developer_follow_up": True,
        "trade_related_severity_allowed": False,
    }


def build_exception_routing_matrix(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    routes = {
        "readiness_score_below_threshold": "developer_follow_up",
        "insufficient_history": "wait_for_more_history",
        "warning_issue_threshold_issue": "owner_review",
        "source_trace_quality_issue": "developer_follow_up",
        "boundary_quality_issue": "hold_daily_pack",
        "protected_path_issue": "hold_daily_pack",
        "daily_pack_completeness_issue": "developer_follow_up",
        "markdown_report_quality_issue": "developer_follow_up",
        "safe_action_threshold_issue": "developer_follow_up",
        "owner_next_step_quality_issue": "developer_follow_up",
        "artifact_navigation_issue": "developer_follow_up",
        "unknown_quality_issue": "owner_review",
    }
    return {
        "matrix_id": "A-SHARE-EXCEPTION-ROUTING-MATRIX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "routes": routes,
        "forbidden_routes": sorted(FORBIDDEN_ROUTES),
        "no_forbidden_routes": not any(route in FORBIDDEN_ROUTES for route in routes.values()),
    }


def build_exception_sla_policy(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "policy_id": "A-SHARE-EXCEPTION-SLA-POLICY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "sla_hours": {
            "blocking": 24,
            "developer_follow_up_required": 48,
            "owner_review_required": 72,
            "warning": 120,
            "info": 168,
        },
        "external_notifications_sent": False,
        "auto_escalation_enabled": False,
    }


def build_escalation_workflow(*, as_of_date: str = DEFAULT_AS_OF_DATE, classification: dict[str, Any], routing: dict[str, Any], sla: dict[str, Any]) -> dict[str, Any]:
    steps = []
    for row in classification.get("classifications", []):
        route = routing["routes"].get(row["category"], "owner_review")
        steps.append(
            {
                "exception_id": row["exception_id"],
                "category": row["category"],
                "severity": row["severity"],
                "route": route,
                "sla_hours": sla["sla_hours"].get(row["severity"], 120),
                "owner_visible": True,
                "trade_related": False,
                "broker_related": False,
                "order_related": False,
            }
        )
    return {
        "workflow_id": "A-SHARE-ESCALATION-WORKFLOW",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "steps": steps,
        "step_count": len(steps),
        "no_forbidden_escalation_routes": not any(step["route"] in FORBIDDEN_ROUTES for step in steps),
        "external_notifications_sent": False,
        "execute_remediation_actions": False,
    }
