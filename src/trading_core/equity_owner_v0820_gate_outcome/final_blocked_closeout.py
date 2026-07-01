"""Final blocked closeout for v0.8.20."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v0820_gate_outcome.outcome_config import BRANCH_CLOSEOUT, DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_final_blocked_closeout(*, as_of_date: str = DEFAULT_AS_OF_DATE, branch: dict[str, Any], availability: dict[str, Any]) -> dict[str, Any]:
    selected = branch.get("selected_branch") == BRANCH_CLOSEOUT
    return {
        "closeout_id": "A-SHARE-FINAL-BLOCKED-CLOSEOUT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "branch_not_selected": not selected,
        "final_blocked_closeout_generated": selected,
        "source_gate_decision": availability.get("source_gate_decision"),
        "source_blocked_decision_preserved": True,
        "previous_readiness_score": availability.get("previous_readiness_score"),
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "remaining_gap_count": availability.get("remaining_gap_count"),
        "blocking_gap_count": availability.get("blocking_gap_count"),
        "overall_evidence_quality": availability.get("overall_evidence_quality"),
        "evidence_insufficient": selected,
        "closeout_reason": "v0819_evidence_not_eligible_for_controlled_gate_reevaluation" if selected else "controlled_branch_selected",
        "controlled_reevaluation_executed": False if selected else None,
        "new_controlled_readiness_score_generated": False if selected else None,
        "new_controlled_gate_decision_generated": False if selected else None,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "waiver_used_for_outcome": False,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

