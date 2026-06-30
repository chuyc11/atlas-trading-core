"""Owner release recommendation for readiness gate."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_gate.gate_config import DEFAULT_AS_OF_DATE, FORBIDDEN_RECOMMENDATIONS, TARGET_VERSION


def build_owner_release_recommendation(*, as_of_date: str = DEFAULT_AS_OF_DATE, decision: dict[str, Any]) -> dict[str, Any]:
    if decision["decision"] == "owner_operationally_acceptable":
        recommendation = "accept_daily_pack_for_owner_review"
    elif decision["decision"] == "owner_operationally_acceptable_with_warnings":
        recommendation = "accept_daily_pack_with_warnings"
    elif "insufficient_history_correctly_flagged" in decision.get("warnings", []) and not decision.get("blocking_reasons"):
        recommendation = "wait_for_more_history"
    else:
        recommendation = "block_daily_pack"
    if recommendation in FORBIDDEN_RECOMMENDATIONS:
        raise ValueError("forbidden owner release recommendation")
    return {
        "recommendation_id": "A-SHARE-OWNER-RELEASE-RECOMMENDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "recommendation": recommendation,
        "reasoning_summary": _reasoning(decision),
        "required_owner_actions": ["Read the owner readiness gate report.", "Review exception candidates before owner review release."] if decision.get("blocking_reasons") else ["Review daily pack quality notes."],
        "developer_follow_up_items": decision.get("blocking_reasons", []),
        "not_investment_recommendation": True,
        "not_trade_instruction": True,
    }


def _reasoning(decision: dict[str, Any]) -> list[str]:
    if decision.get("blocking_reasons"):
        return ["At least one required owner operations quality gate failed.", "The daily pack should be held for developer review."]
    if decision.get("warnings"):
        return ["Required gates passed, but non-blocking warnings need owner awareness."]
    return ["All owner operations quality gates passed."]
