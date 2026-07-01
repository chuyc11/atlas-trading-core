"""Owner next-step decision aid."""

from __future__ import annotations

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


ALLOWED_NEXT_STEPS = [
    "review_known_blocked_state",
    "review_unresolved_blockers",
    "prepare_future_evidence_collection",
    "improve_operator_report_usability",
    "prepare_next_research_day_simulation_without_broker",
]

FORBIDDEN_NEXT_STEPS = [
    "place_order",
    "connect_broker",
    "enable_live_trading",
    "generate_buy_sell_signals",
    "override_owner_readiness_gate",
    "lower_threshold",
    "approve_auto_waiver",
]


def build_owner_next_step_decision_aid(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    return {
        "decision_aid_id": "A-SHARE-OWNER-NEXT-STEP-DECISION-AID",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "recommended_next_step": "review_known_blocked_state",
        "allowed_next_steps": [{"step_id": step, "allowed": True, "owner_visible": True} for step in ALLOWED_NEXT_STEPS],
        "forbidden_next_steps": [{"step_id": step, "allowed": False, "reason": "Outside current research-only boundary"} for step in FORBIDDEN_NEXT_STEPS],
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
    }
