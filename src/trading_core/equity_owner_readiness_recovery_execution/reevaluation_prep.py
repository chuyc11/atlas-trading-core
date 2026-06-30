"""Gate reevaluation preparation artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_gate_reevaluation_prerequisite_checklist(*, as_of_date: str = DEFAULT_AS_OF_DATE, status_tracker: dict[str, Any], evidence_quality: dict[str, Any], audit_only: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "all_recovery_tasks_have_evidence": status_tracker.get("evidence_available_count", 0) == status_tracker.get("task_count", 0) and status_tracker.get("task_count", 0) > 0,
        "all_recovery_tasks_verified_by_audit_only": status_tracker.get("verified_by_audit_only_count", 0) == status_tracker.get("task_count", 0) and status_tracker.get("task_count", 0) > 0,
        "evidence_quality_sufficient": evidence_quality.get("evidence_sufficient_for_gate_reevaluation") is True,
        "audit_only_verification_passed": audit_only.get("audit_only_verification_passed") is True,
        "no_threshold_lowering": True,
        "no_auto_waiver": True,
        "no_gate_reevaluation_executed": True,
    }
    ready = all(checks.values())
    return {
        "checklist_id": "A-SHARE-GATE-REEVALUATION-PREREQUISITE-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "ready_for_future_gate_reevaluation": ready,
        "blocking_reasons": [] if ready else ["recovery_evidence_not_sufficient_for_gate_reevaluation"],
    }


def build_gate_reevaluation_readiness_decision(*, as_of_date: str = DEFAULT_AS_OF_DATE, prerequisite_checklist: dict[str, Any]) -> dict[str, Any]:
    ready = prerequisite_checklist.get("ready_for_future_gate_reevaluation") is True
    return {
        "decision_id": "A-SHARE-GATE-REEVALUATION-READINESS-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "gate_reevaluation_readiness_decision": "ready" if ready else "not_ready",
        "ready_for_future_gate_reevaluation": ready,
        "gate_reevaluation_executed": False,
        "reason": "all prerequisites satisfied" if ready else "recovery evidence remains insufficient",
        "blocking_reasons": [] if ready else prerequisite_checklist.get("blocking_reasons", []),
    }


def build_controlled_reevaluation_plan(*, as_of_date: str = DEFAULT_AS_OF_DATE, readiness_decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "plan_id": "A-SHARE-CONTROLLED-REEVALUATION-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "gate_reevaluation_executed": False,
        "rerun_owner_readiness_gate": False,
        "rerun_build_from_existing_data": False,
        "rerun_daily_pack": False,
        "entry_condition": "future version only when readiness decision is ready",
        "current_readiness_decision": readiness_decision.get("gate_reevaluation_readiness_decision"),
        "future_version": RECOMMENDED_NEXT_VERSION,
        "required_controls": ["preserve threshold", "no automatic waiver", "audit source evidence", "keep execution boundaries"],
    }
