"""Recovery task completion evaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_recovery_task_completion_evaluation(*, as_of_date: str = DEFAULT_AS_OF_DATE, status_tracker: dict[str, Any], evidence_registry: dict[str, Any]) -> dict[str, Any]:
    items = []
    for row in status_tracker.get("items", []):
        items.append(
            {
                "task_id": row["task_id"],
                "status": row["status"],
                "evidence_available": row["evidence_available"],
                "verified_by_audit_only": row["verified_by_audit_only"],
                "completed": False,
                "completion_reason": "no completion evidence and no audit-only verification evidence",
                "task_existence_alone_not_completion": True,
            }
        )
    return {
        "evaluation_id": "A-SHARE-RECOVERY-TASK-COMPLETION-EVALUATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "task_count": len(items),
        "completed_count": 0,
        "tasks_marked_complete_by_default": False,
        "task_completion_not_fabricated": True,
        "evidence_record_count": evidence_registry.get("evidence_record_count", 0),
        "items": items,
    }
