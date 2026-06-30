"""Blocked owner readiness gate intake."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_blocked_gate_intake(*, as_of_date: str = DEFAULT_AS_OF_DATE, decision: dict[str, Any], evaluation: dict[str, Any], candidates: dict[str, Any]) -> dict[str, Any]:
    minimum = int(decision.get("minimum_owner_readiness_score") or 0)
    actual = int(decision.get("actual_owner_readiness_score") or 0)
    return {
        "intake_id": "A-SHARE-BLOCKED-OWNER-READINESS-GATE-INTAKE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": decision.get("decision"),
        "owner_operationally_acceptable": decision.get("owner_operationally_acceptable"),
        "required_gates_passed": decision.get("required_gates_passed"),
        "minimum_owner_readiness_score": minimum,
        "actual_owner_readiness_score": actual,
        "actual_owner_readiness_grade": decision.get("actual_owner_readiness_grade"),
        "readiness_score_gap": max(minimum - actual, 0),
        "failed_gates": evaluation.get("failed_gates", []),
        "warning_gates": _warning_gates(candidates),
        "quality_exception_candidates": candidates.get("candidates", []),
        "blocked_state_preserved": decision.get("decision") == "blocked" and decision.get("owner_operationally_acceptable") is False,
        "audit_passed_but_gate_blocked_explanation": "Audit passed because the blocked gate state is represented correctly; it does not mean the gate was released.",
        "blocking_reasons": decision.get("blocking_reasons", []),
        "warnings": decision.get("warnings", []),
    }


def _warning_gates(candidates: dict[str, Any]) -> list[str]:
    return sorted({item.get("source_gate") for item in candidates.get("candidates", []) if item.get("severity") == "warning" and item.get("source_gate")})
