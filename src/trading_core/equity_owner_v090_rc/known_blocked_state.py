"""Known blocked owner-readiness disclosure."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_known_blocked_state_disclosure(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any]) -> dict[str, Any]:
    return {
        "disclosure_id": "A-SHARE-V090-KNOWN-BLOCKED-OWNER-READINESS-STATE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": availability.get("owner_operationally_acceptable"),
        "previous_readiness_score": availability.get("previous_readiness_score"),
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "score_gap": availability.get("score_gap"),
        "blocked_state_intentional": availability.get("blocked_state_intentional"),
        "blocked_state_audited": availability.get("blocked_state_audited"),
        "blocked_state_misrepresented_as_acceptable": availability.get("blocked_state_misrepresented_as_acceptable"),
        "blocks_owner_readiness_acceptance": availability.get("blocks_owner_readiness_acceptance"),
        "blocks_v090_rc": availability.get("blocks_v090_rc"),
        "not_live_trading_ready": True,
        "not_trade_instruction": True,
        "overall_passed": availability.get("owner_operationally_acceptable") is False and availability.get("blocks_v090_rc") is False,
        "blocking_reasons": [] if availability.get("owner_operationally_acceptable") is False and availability.get("blocks_v090_rc") is False else ["known_blocked_state_disclosure_inconsistent"],
        "warnings": [],
    }
