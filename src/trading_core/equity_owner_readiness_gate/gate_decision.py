"""Gate decision and quality threshold evaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_gate.gate_config import DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_gate_decision(*, as_of_date: str = DEFAULT_AS_OF_DATE, gates: dict[str, dict[str, Any]], score: dict[str, Any], policy: dict[str, Any], exceptions: list[dict[str, Any]]) -> dict[str, Any]:
    blocking = sorted({reason for gate in gates.values() for reason in gate.get("blocking_reasons", [])})
    warnings = sorted({warning for gate in gates.values() for warning in gate.get("warnings", [])})
    required_passed = not blocking
    if required_passed and warnings:
        decision = "owner_operationally_acceptable_with_warnings"
    elif required_passed:
        decision = "owner_operationally_acceptable"
    else:
        decision = "blocked"
    return {
        "decision_id": "A-SHARE-OWNER-READINESS-GATE-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "decision": decision,
        "owner_operationally_acceptable": decision.startswith("owner_operationally_acceptable"),
        "minimum_owner_readiness_score": policy["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": score.get("score"),
        "actual_owner_readiness_grade": score.get("grade"),
        "required_gates_passed": required_passed,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "quality_exception_candidates": exceptions,
        "next_operational_step": "review_owner_release_recommendation" if required_passed else "hold_daily_pack_for_developer_review",
        "not_investment_decision": True,
        "not_trade_instruction": True,
    }


def build_quality_threshold_evaluation(*, as_of_date: str = DEFAULT_AS_OF_DATE, gates: dict[str, dict[str, Any]], decision: dict[str, Any]) -> dict[str, Any]:
    failed = [name for name, gate in gates.items() if gate.get("passed") is not True]
    passed = [name for name, gate in gates.items() if gate.get("passed") is True]
    return {
        "evaluation_id": "A-SHARE-QUALITY-THRESHOLD-EVALUATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "passed_gates": passed,
        "failed_gates": failed,
        "required_gates_passed": not failed,
        "decision": decision["decision"],
        "blocking_reasons": decision["blocking_reasons"],
        "warnings": decision["warnings"],
        "not_investment_decision": True,
        "not_trade_instruction": True,
    }
