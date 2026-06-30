"""Recovery task status tracker."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import ALLOWED_TASK_STATUSES, DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_recovery_task_status_tracker(*, as_of_date: str = DEFAULT_AS_OF_DATE, backlog: dict[str, Any], evidence_registry: dict[str, Any], source_gate_decision: str = "blocked") -> dict[str, Any]:
    evidence_by_task = {row["source_task_id"]: row for row in evidence_registry.get("records", [])}
    rows = []
    for task in backlog.get("tasks", []):
        evidence = evidence_by_task.get(task["task_id"], {})
        if task.get("requires_more_history"):
            status = "waiting_for_more_history"
        elif evidence.get("evidence_available") is True:
            status = "evidence_available"
        else:
            status = "planned"
        rows.append(
            {
                "task_id": task["task_id"],
                "source_exception_id": task.get("source_exception_id"),
                "category": task.get("category"),
                "source_status": task.get("status"),
                "status": status,
                "evidence_available": evidence.get("evidence_available", False),
                "verified_by_audit_only": False,
                "completed": False,
                "completion_not_inferred_from_task_existence": True,
            }
        )
    counts = {status: sum(1 for row in rows if row["status"] == status) for status in ALLOWED_TASK_STATUSES}
    return {
        "tracker_id": "A-SHARE-RECOVERY-TASK-STATUS-TRACKER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": source_gate_decision,
        "task_count": len(rows),
        "planned_count": counts.get("planned", 0),
        "in_progress_count": counts.get("in_progress", 0),
        "evidence_available_count": counts.get("evidence_available", 0),
        "verified_by_audit_only_count": counts.get("verified_by_audit_only", 0),
        "blocked_count": counts.get("blocked", 0),
        "not_actionable_count": counts.get("not_actionable", 0),
        "waiting_for_more_history_count": counts.get("waiting_for_more_history", 0),
        "completed_count": sum(1 for row in rows if row["completed"]),
        "tasks_marked_complete_by_default": any(row["completed"] for row in rows),
        "allowed_statuses": sorted(ALLOWED_TASK_STATUSES),
        "items": rows,
    }
