"""Controlled owner-readiness reevaluation outcome."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v0820_gate_outcome.outcome_config import BRANCH_CONTROLLED, DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_controlled_gate_reevaluation_outcome(*, as_of_date: str = DEFAULT_AS_OF_DATE, branch: dict[str, Any], availability: dict[str, Any]) -> dict[str, Any]:
    if branch.get("selected_branch") != BRANCH_CONTROLLED:
        return {
            "outcome_id": "A-SHARE-CONTROLLED-GATE-REEVALUATION-OUTCOME",
            "target_version": TARGET_VERSION,
            "as_of_date": as_of_date,
            "branch_not_selected": True,
            "controlled_reevaluation_executed": False,
            "reevaluation_refused_reason": "branch_not_selected_or_not_eligible",
            "previous_readiness_score": availability.get("previous_readiness_score"),
            "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
            "new_controlled_readiness_score_generated": False,
            "new_controlled_readiness_score": None,
            "new_controlled_readiness_grade": None,
            "new_controlled_gate_decision_generated": False,
            "new_controlled_gate_decision": None,
            "owner_operationally_acceptable": False,
            "threshold_lowered": False,
            "auto_waiver_allowed": False,
            "manual_waiver_approval_recorded": False,
            "waiver_used_for_outcome": False,
        }
    score = int(availability.get("previous_readiness_score") or 0)
    minimum = int(availability.get("minimum_owner_readiness_score") or 75)
    decision = "owner_operationally_acceptable" if score >= minimum else "blocked"
    return {
        "outcome_id": "A-SHARE-CONTROLLED-GATE-REEVALUATION-OUTCOME",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "branch_not_selected": False,
        "controlled_reevaluation_executed": True,
        "previous_readiness_score": score,
        "minimum_owner_readiness_score": minimum,
        "new_controlled_readiness_score_generated": True,
        "new_controlled_readiness_score": score,
        "new_controlled_readiness_grade": "A" if score >= minimum else "D",
        "new_controlled_gate_decision_generated": True,
        "new_controlled_gate_decision": decision,
        "owner_operationally_acceptable": decision != "blocked",
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "waiver_used_for_outcome": False,
    }

