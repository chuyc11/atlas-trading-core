"""Final blocked closeout review artifact."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_final_blocked_closeout_review(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any]) -> dict[str, Any]:
    passed = (
        availability.get("selected_v0820_branch") == "final_blocked_closeout"
        and availability.get("source_gate_decision") == "blocked"
        and availability.get("owner_operationally_acceptable") is False
        and availability.get("controlled_reevaluation_executed") is False
        and availability.get("new_gate_score_generated") is False
        and availability.get("new_gate_decision_generated") is False
        and availability.get("v0820_outcome_audit_passed") is True
    )
    return {
        "review_id": "A-SHARE-FINAL-BLOCKED-CLOSEOUT-REVIEW",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "selected_v0820_branch": availability.get("selected_v0820_branch"),
        "source_gate_decision": availability.get("source_gate_decision"),
        "owner_operationally_acceptable": availability.get("owner_operationally_acceptable"),
        "previous_readiness_score": availability.get("previous_readiness_score"),
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "score_gap": availability.get("score_gap"),
        "controlled_reevaluation_executed": availability.get("controlled_reevaluation_executed"),
        "new_gate_score_generated": availability.get("new_gate_score_generated"),
        "new_gate_decision_generated": availability.get("new_gate_decision_generated"),
        "blocked_state_intentional": True,
        "blocked_state_audited": availability.get("v0820_outcome_audit_passed") is True,
        "blocked_state_misrepresented_as_acceptable": False,
        "closeout_review_passed": passed,
        "blocking_reasons": [] if passed else ["final_blocked_closeout_review_failed"],
        "warnings": [],
    }
