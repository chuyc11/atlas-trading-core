"""Quality exception classification."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


CATEGORY_BY_REASON = {
    "owner_readiness_score_below_threshold": "readiness_score_below_threshold",
    "insufficient_history_correctly_flagged": "insufficient_history",
    "warning_issue_items_present": "warning_issue_threshold_issue",
    "source_trace_incomplete": "source_trace_quality_issue",
    "boundary_not_clean": "boundary_quality_issue",
    "protected_path_modifications_detected": "protected_path_issue",
    "required_json_artifacts_incomplete": "daily_pack_completeness_issue",
    "markdown_report_incomplete": "markdown_report_quality_issue",
    "forbidden_owner_next_step_detected": "owner_next_step_quality_issue",
    "artifact_navigation_incomplete": "artifact_navigation_issue",
}


def classify_quality_exceptions(
    *, as_of_date: str = DEFAULT_AS_OF_DATE, registry: dict[str, Any], intake: dict[str, Any], score_gate: dict[str, Any]
) -> dict[str, Any]:
    rows = []
    for record in registry.get("records", []):
        description = record["description"]
        category = CATEGORY_BY_REASON.get(description, "unknown_quality_issue")
        severity = _severity(category, record)
        rows.append(
            {
                "exception_id": record["exception_id"],
                "target_version": TARGET_VERSION,
                "as_of_date": as_of_date,
                "category": category,
                "severity": severity,
                "source_gate": record["source_gate"],
                "actual_value": _actual_value(category, intake, score_gate),
                "threshold_value": _threshold_value(category, intake, score_gate),
                "readiness_score_impact": intake.get("readiness_score_gap", 0) if category == "readiness_score_below_threshold" else 0,
                "owner_visibility": True,
                "developer_follow_up_required": severity in {"developer_follow_up_required", "blocking"} or record.get("developer_follow_up_required") is True,
                "owner_follow_up_required": True,
                "waiver_candidate": record.get("waiver_allowed") is True,
                "waiver_allowed": record.get("waiver_allowed") is True and category not in {"boundary_quality_issue", "protected_path_issue"},
                "auto_waiver_allowed": False,
                "trade_related": False,
                "broker_related": False,
                "order_related": False,
                "status": "classified",
            }
        )
    return {
        "classification_id": "A-SHARE-QUALITY-EXCEPTION-CLASSIFICATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "classified_count": len(rows),
        "classifications": rows,
        "quality_exceptions_classified": bool(rows),
        "forbidden_trade_broker_order_categories_present": False,
    }


def _severity(category: str, record: dict[str, Any]) -> str:
    if category == "readiness_score_below_threshold":
        return "blocking"
    if category in {"boundary_quality_issue", "protected_path_issue", "source_trace_quality_issue", "daily_pack_completeness_issue"}:
        return "developer_follow_up_required"
    if record.get("raw_severity") == "warning":
        return "owner_review_required"
    return "warning"


def _actual_value(category: str, intake: dict[str, Any], score_gate: dict[str, Any]) -> Any:
    if category == "readiness_score_below_threshold":
        return intake.get("actual_owner_readiness_score")
    return score_gate.get("actual_value")


def _threshold_value(category: str, intake: dict[str, Any], score_gate: dict[str, Any]) -> Any:
    if category == "readiness_score_below_threshold":
        return intake.get("minimum_owner_readiness_score")
    return score_gate.get("threshold")
