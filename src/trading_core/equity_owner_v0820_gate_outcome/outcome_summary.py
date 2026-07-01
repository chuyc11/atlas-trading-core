"""Owner outcome summary for v0.8.20."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v0820_gate_outcome.outcome_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_owner_outcome_summary(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    branch: dict[str, Any],
    controlled: dict[str, Any],
    closeout: dict[str, Any],
    availability: dict[str, Any],
) -> dict[str, Any]:
    selected_branch = branch.get("selected_branch")
    return {
        "summary_id": "A-SHARE-OWNER-V0820-OUTCOME-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": availability.get("source_gate_decision"),
        "selected_branch": selected_branch,
        "branch_decision_consistent": (selected_branch == "controlled_gate_reevaluation") == bool(branch.get("controlled_reevaluation_allowed")),
        "controlled_reevaluation_allowed": branch.get("controlled_reevaluation_allowed"),
        "controlled_reevaluation_executed": controlled.get("controlled_reevaluation_executed") is True,
        "final_blocked_closeout_generated": closeout.get("final_blocked_closeout_generated") is True,
        "previous_readiness_score": availability.get("previous_readiness_score"),
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "new_controlled_readiness_score_generated": controlled.get("new_controlled_readiness_score_generated") is True,
        "new_controlled_readiness_score": controlled.get("new_controlled_readiness_score"),
        "new_controlled_readiness_grade": controlled.get("new_controlled_readiness_grade"),
        "new_controlled_gate_decision_generated": controlled.get("new_controlled_gate_decision_generated") is True,
        "new_controlled_gate_decision": controlled.get("new_controlled_gate_decision"),
        "owner_operationally_acceptable": controlled.get("owner_operationally_acceptable") is True,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "waiver_used_for_outcome": False,
        "not_investment_advice": True,
        "not_order_instruction": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

