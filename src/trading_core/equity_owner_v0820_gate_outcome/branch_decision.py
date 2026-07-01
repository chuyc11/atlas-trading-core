"""Branch decision for v0.8.20 outcome."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v0820_gate_outcome.outcome_config import BRANCH_CLOSEOUT, BRANCH_CONTROLLED, DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_branch_decision(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any], boundary_clean: bool = True) -> dict[str, Any]:
    checks = {
        "source_gate_decision_blocked": availability.get("source_gate_decision") == "blocked",
        "source_gate_decision_preserved": availability.get("source_gate_decision_preserved") is True,
        "ready_for_controlled_gate_reevaluation": availability.get("v0819_ready_for_controlled_gate_reevaluation") is True,
        "eligibility_decision_ready": availability.get("v0819_eligibility_decision") in {"eligible", "ready_for_controlled_gate_reevaluation"},
        "reevaluation_input_package_generated": availability.get("reevaluation_input_package_generated") is True,
        "no_remaining_gaps": int(availability.get("remaining_gap_count") or 0) == 0,
        "no_blocking_gaps": int(availability.get("blocking_gap_count") or 0) == 0,
        "threshold_not_lowered": availability.get("threshold_lowered") is False,
        "waiver_not_used": availability.get("auto_waiver_allowed") is False and availability.get("manual_waiver_approval_recorded") is False,
        "v0819_no_gate_outputs": availability.get("new_gate_score_generated") is False and availability.get("new_gate_decision_generated") is False,
        "boundary_clean": boundary_clean,
    }
    controlled_allowed = all(checks.values())
    branch_reasons = [key for key, passed in checks.items() if not passed]
    return {
        "decision_id": "A-SHARE-V0820-BRANCH-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": availability.get("source_gate_decision"),
        "v0819_eligibility_decision": availability.get("v0819_eligibility_decision"),
        "v0819_ready_for_controlled_gate_reevaluation": availability.get("v0819_ready_for_controlled_gate_reevaluation"),
        "remaining_gap_count": availability.get("remaining_gap_count"),
        "blocking_gap_count": availability.get("blocking_gap_count"),
        "selected_branch": BRANCH_CONTROLLED if controlled_allowed else BRANCH_CLOSEOUT,
        "controlled_reevaluation_allowed": controlled_allowed,
        "final_blocked_closeout_required": not controlled_allowed,
        "branch_reasons": branch_reasons,
        "branch_checks": checks,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "blocking_reasons": [],
        "warnings": [],
    }

