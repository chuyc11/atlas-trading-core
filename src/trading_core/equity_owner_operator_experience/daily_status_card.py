"""Owner daily status card."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, SOURCE_RELEASE_CANDIDATE, TARGET_VERSION


def build_owner_daily_status_card(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any], full_pytest: dict[str, Any], summary: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    return {
        "status_card_id": "A-SHARE-OWNER-DAILY-STATUS-CARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "system_release": SOURCE_RELEASE_CANDIDATE,
        "system_state": "research_system_rc_passed",
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": availability.get("owner_operationally_acceptable"),
        "readiness_score": availability.get("previous_readiness_score"),
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "score_gap": availability.get("score_gap"),
        "blocked_state_intentional": availability.get("blocked_state_intentional"),
        "blocked_state_audited": availability.get("blocked_state_audited"),
        "blocked_state_misrepresented_as_acceptable": availability.get("blocked_state_misrepresented_as_acceptable"),
        "full_pytest_passed": full_pytest.get("overall_passed") is True,
        "full_pytest_result": f"{full_pytest.get('passed_count')} passed, {full_pytest.get('skipped_count')} skipped",
        "audit_sweep_passed": summary.get("audit_sweep_passed") is True,
        "boundary_clean": boundary.get("overall_passed") is True,
        "live_trading_ready": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "buy_sell_signals_generated": False,
        "recommended_owner_action": "review_known_blocked_state_and_unresolved_blockers",
        "not_trade_instruction": True,
        "overall_passed": availability.get("owner_operationally_acceptable") is False and boundary.get("overall_passed") is True,
        "blocking_reasons": [],
        "warnings": [],
    }
