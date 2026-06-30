"""Readiness guard for controlled gate reevaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_reevaluation_readiness_guard(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    source_summary: dict[str, Any],
    status_tracker: dict[str, Any],
    evidence_registry: dict[str, Any],
    readiness_decision: dict[str, Any],
    threshold: dict[str, Any],
    waiver: dict[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    if readiness_decision.get("ready_for_future_gate_reevaluation") is not True:
        reasons.append("source_readiness_not_ready")
    if evidence_registry.get("evidence_available_count", 0) <= 0:
        reasons.append("no_recovery_evidence_available")
    if status_tracker.get("completed_count", 0) <= 0:
        reasons.append("no_recovery_tasks_completed")
    if status_tracker.get("verified_by_audit_only_count", 0) <= 0:
        reasons.append("no_tasks_verified_by_audit_only")
    if source_summary.get("source_gate_decision") != "blocked":
        reasons.append("source_gate_decision_not_blocked")
    if source_summary.get("blocked_gate_decision_preserved") is not True:
        reasons.append("source_blocked_gate_decision_not_preserved")
    if threshold.get("threshold_lowered") is not False:
        reasons.append("threshold_lowered")
    if waiver.get("auto_waiver_allowed") is not False or waiver.get("manual_waiver_approval_recorded") is not False:
        reasons.append("waiver_recorded")
    passed = not reasons
    return {
        "guard_id": "A-SHARE-OWNER-REEVALUATION-READINESS-GUARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "readiness_guard_passed": passed,
        "reevaluation_allowed": passed,
        "reevaluation_block_reason": "" if passed else "evidence_not_ready",
        "block_reasons": reasons,
        "source_gate_decision": source_summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": source_summary.get("blocked_gate_decision_preserved"),
        "ready_for_future_gate_reevaluation": readiness_decision.get("ready_for_future_gate_reevaluation"),
        "gate_reevaluation_executed": False,
        "task_count": status_tracker.get("task_count"),
        "evidence_available_count": evidence_registry.get("evidence_available_count"),
        "verified_by_audit_only_count": status_tracker.get("verified_by_audit_only_count"),
        "completed_count": status_tracker.get("completed_count"),
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "overall_passed": True,
        "blocking_reasons": [],
    }

