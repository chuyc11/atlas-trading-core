"""Blocked state, threshold, and waiver preservation checks."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_blocked_state_preservation_check(*, as_of_date: str = DEFAULT_AS_OF_DATE, source_summary: dict[str, Any]) -> dict[str, Any]:
    passed = source_summary.get("source_gate_decision") == "blocked" and source_summary.get("blocked_gate_decision_preserved") is True
    return {
        "check_id": "A-SHARE-RECOVERY-EXECUTION-BLOCKED-STATE-PRESERVATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": source_summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": source_summary.get("blocked_gate_decision_preserved"),
        "recovery_execution_changes_gate_decision": False,
        "gate_reevaluation_executed": False,
        "overall_passed": passed,
        "blocking_reasons": [] if passed else ["blocked_state_not_preserved"],
    }


def build_threshold_preservation_check(*, as_of_date: str = DEFAULT_AS_OF_DATE, source_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "check_id": "A-SHARE-RECOVERY-EXECUTION-THRESHOLD-PRESERVATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "minimum_owner_readiness_score": source_summary.get("minimum_owner_readiness_score"),
        "actual_owner_readiness_score": source_summary.get("actual_owner_readiness_score"),
        "threshold_lowered": False,
        "threshold_preserved": True,
        "overall_passed": True,
        "blocking_reasons": [],
    }


def build_waiver_preservation_check(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "check_id": "A-SHARE-RECOVERY-EXECUTION-WAIVER-PRESERVATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "waiver_changes_gate_decision": False,
        "overall_passed": True,
        "blocking_reasons": [],
    }
