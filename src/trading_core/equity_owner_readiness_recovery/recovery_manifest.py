"""Manifest and summary for owner readiness recovery."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_recovery_manifest(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    gap: dict[str, Any],
    backlog: dict[str, Any],
    developer_plan: dict[str, Any],
    owner_plan: dict[str, Any],
    checklist: dict[str, Any],
    blocked_state: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-READINESS-RECOVERY-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": gap["source_gate_decision"],
        "blocked_gate_decision_preserved": gap["blocked_state_preserved"],
        "owner_operationally_acceptable": gap["owner_operationally_acceptable"],
        "minimum_owner_readiness_score": gap["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": gap["actual_owner_readiness_score"],
        "actual_owner_readiness_grade": gap["actual_owner_readiness_grade"],
        "readiness_score_gap": gap["readiness_score_gap"],
        "quality_exception_count": gap["quality_exception_count"],
        "recovery_task_count": backlog["task_count"],
        "developer_follow_up_task_count": developer_plan["follow_up_count"],
        "owner_follow_up_task_count": owner_plan["owner_follow_up_count"],
        "ready_for_future_gate_reevaluation": checklist["ready_for_future_gate_reevaluation"],
        "recovery_plan_changes_gate_decision": blocked_state["recovery_plan_changes_gate_decision"],
        "threshold_lowered": blocked_state["threshold_lowered"],
        "auto_waiver_allowed": blocked_state["auto_waiver_allowed"],
        "manual_waiver_approval_recorded": blocked_state["manual_waiver_approval_recorded"],
        "execute_recovery_tasks": False,
        "mark_tasks_complete_by_default": False,
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_recovery_summary(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    gap: dict[str, Any],
    backlog: dict[str, Any],
    developer_plan: dict[str, Any],
    owner_plan: dict[str, Any],
    checklist: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-READINESS-RECOVERY-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": gap["source_gate_decision"],
        "blocked_gate_decision_preserved": gap["blocked_state_preserved"],
        "minimum_owner_readiness_score": gap["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": gap["actual_owner_readiness_score"],
        "actual_owner_readiness_grade": gap["actual_owner_readiness_grade"],
        "readiness_score_gap": gap["readiness_score_gap"],
        "recovery_task_count": backlog["task_count"],
        "developer_follow_up_task_count": developer_plan["follow_up_count"],
        "owner_follow_up_task_count": owner_plan["owner_follow_up_count"],
        "ready_for_future_gate_reevaluation": checklist["ready_for_future_gate_reevaluation"],
        "recovery_plan_changes_gate_decision": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "execute_recovery_tasks": False,
        "not_investment_advice": True,
        "not_order_instruction": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
