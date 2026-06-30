"""Developer and owner follow-up evidence tracking."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_developer_follow_up_evidence_tracker(*, as_of_date: str = DEFAULT_AS_OF_DATE, developer_plan: dict[str, Any], evidence_registry: dict[str, Any]) -> dict[str, Any]:
    evidence_by_task = {row["source_task_id"]: row for row in evidence_registry.get("records", [])}
    items = []
    for item in developer_plan.get("items", []):
        source_task_id = _task_for_exception(item.get("source_exception_id"))
        evidence = evidence_by_task.get(source_task_id, {})
        items.append(
            {
                "follow_up_id": item.get("follow_up_id"),
                "source_exception_id": item.get("source_exception_id"),
                "source_task_id": source_task_id,
                "evidence_available": evidence.get("evidence_available", False),
                "evidence_confidence": evidence.get("evidence_confidence", "none"),
                "evidence_artifact_path": evidence.get("evidence_artifact_path", ""),
                "status": "evidence_available" if evidence.get("evidence_available") else "planned",
                "completion_verified": False,
            }
        )
    return {
        "tracker_id": "A-SHARE-DEVELOPER-FOLLOW-UP-EVIDENCE-TRACKER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "follow_up_count": len(items),
        "evidence_available_count": sum(1 for row in items if row["evidence_available"]),
        "completed_count": sum(1 for row in items if row["completion_verified"]),
        "items": items,
    }


def build_owner_follow_up_evidence_tracker(*, as_of_date: str = DEFAULT_AS_OF_DATE, owner_plan: dict[str, Any]) -> dict[str, Any]:
    items = [
        {
            "action": item.get("action"),
            "source_status": item.get("status"),
            "evidence_available": False,
            "evidence_confidence": "none",
            "evidence_artifact_path": "",
            "owner_follow_up_completed": False,
            "trade_related": item.get("trade_related", False),
            "broker_related": item.get("broker_related", False),
            "order_related": item.get("order_related", False),
        }
        for item in owner_plan.get("items", [])
    ]
    return {
        "tracker_id": "A-SHARE-OWNER-FOLLOW-UP-EVIDENCE-TRACKER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_follow_up_count": len(items),
        "evidence_available_count": sum(1 for row in items if row["evidence_available"]),
        "completed_count": sum(1 for row in items if row["owner_follow_up_completed"]),
        "items": items,
    }


def _task_for_exception(exception_id: str | None) -> str:
    if exception_id and "owner_readiness_score_gate" in exception_id:
        return "RECOVERY-TASK-001"
    if exception_id and "warning_issue_quality_gate" in exception_id:
        return "RECOVERY-TASK-002"
    if exception_id and "trend_sufficiency_quality_gate" in exception_id:
        return "RECOVERY-TASK-003"
    return ""
