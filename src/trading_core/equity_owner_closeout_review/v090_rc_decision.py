"""v0.9.0 release candidate readiness decision."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_v090_release_candidate_readiness_decision(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    final_review: dict[str, Any],
    regression_plan: dict[str, Any],
    audit_sweep_plan: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    ready = (
        final_review.get("blocked_state_intentional") is True
        and final_review.get("blocked_state_audited") is True
        and final_review.get("blocked_state_misrepresented_as_acceptable") is False
        and regression_plan.get("full_pytest_run") is False
        and regression_plan.get("full_pytest_required_in_v090") is True
        and audit_sweep_plan.get("audit_count", 0) >= 9
        and boundary.get("overall_passed") is True
    )
    decision = "ready_with_known_blocked_owner_readiness_state" if ready else "not_ready_for_v090_rc"
    return {
        "decision_id": "A-SHARE-V090-RELEASE-CANDIDATE-READINESS-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "allowed_decisions": [
            "ready_for_v090_rc_full_regression",
            "not_ready_for_v090_rc",
            "ready_with_known_blocked_owner_readiness_state",
        ],
        "decision": decision,
        "owner_readiness_remains_blocked": True,
        "owner_operationally_acceptable": False,
        "blocked_state_intentional": final_review.get("blocked_state_intentional"),
        "blocked_state_audited": final_review.get("blocked_state_audited"),
        "blocked_state_misrepresented_as_acceptable": final_review.get("blocked_state_misrepresented_as_acceptable"),
        "v090_full_regression_plan_generated": regression_plan.get("plan_id") == "A-SHARE-V090-FULL-REGRESSION-PLAN",
        "v090_audit_sweep_plan_generated": audit_sweep_plan.get("plan_id") == "A-SHARE-V090-AUDIT-SWEEP-PLAN",
        "overall_passed": ready,
        "blocking_reasons": [] if ready else ["v090_rc_readiness_decision_not_ready"],
        "warnings": [],
    }
