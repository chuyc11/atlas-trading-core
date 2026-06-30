"""Manifest and summary for owner readiness recovery execution."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_execution_manifest(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    source_summary: dict[str, Any],
    status_tracker: dict[str, Any],
    evidence_registry: dict[str, Any],
    readiness_decision: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-READINESS-RECOVERY-EXECUTION-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": source_summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": source_summary.get("blocked_gate_decision_preserved"),
        "minimum_owner_readiness_score": source_summary.get("minimum_owner_readiness_score"),
        "actual_owner_readiness_score": source_summary.get("actual_owner_readiness_score"),
        "readiness_score_gap": source_summary.get("readiness_score_gap"),
        "task_count": status_tracker.get("task_count"),
        "evidence_available_count": evidence_registry.get("evidence_available_count"),
        "verified_by_audit_only_count": status_tracker.get("verified_by_audit_only_count"),
        "completed_count": status_tracker.get("completed_count"),
        "ready_for_future_gate_reevaluation": readiness_decision.get("ready_for_future_gate_reevaluation"),
        "gate_reevaluation_readiness_decision": readiness_decision.get("gate_reevaluation_readiness_decision"),
        "gate_reevaluation_executed": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_execution_summary(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    source_summary: dict[str, Any],
    status_tracker: dict[str, Any],
    evidence_registry: dict[str, Any],
    readiness_decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-READINESS-RECOVERY-EXECUTION-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": source_summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": source_summary.get("blocked_gate_decision_preserved"),
        "minimum_owner_readiness_score": source_summary.get("minimum_owner_readiness_score"),
        "actual_owner_readiness_score": source_summary.get("actual_owner_readiness_score"),
        "readiness_score_gap": source_summary.get("readiness_score_gap"),
        "task_count": status_tracker.get("task_count"),
        "evidence_available_count": evidence_registry.get("evidence_available_count"),
        "verified_by_audit_only_count": status_tracker.get("verified_by_audit_only_count"),
        "completed_count": status_tracker.get("completed_count"),
        "tasks_marked_complete_by_default": status_tracker.get("tasks_marked_complete_by_default"),
        "ready_for_future_gate_reevaluation": readiness_decision.get("ready_for_future_gate_reevaluation"),
        "gate_reevaluation_readiness_decision": readiness_decision.get("gate_reevaluation_readiness_decision"),
        "gate_reevaluation_executed": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "not_investment_advice": True,
        "not_order_instruction": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
