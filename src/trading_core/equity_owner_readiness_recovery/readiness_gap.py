"""Readiness gap summary."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_readiness_gap_summary(*, as_of_date: str = DEFAULT_AS_OF_DATE, intake: dict[str, Any], registry: dict[str, Any], developer_tracker: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-READINESS-GAP-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": intake.get("source_gate_decision"),
        "minimum_owner_readiness_score": intake.get("minimum_owner_readiness_score"),
        "actual_owner_readiness_score": intake.get("actual_owner_readiness_score"),
        "actual_owner_readiness_grade": intake.get("actual_owner_readiness_grade"),
        "readiness_score_gap": intake.get("readiness_score_gap"),
        "quality_exception_count": registry.get("exception_count", 0),
        "developer_follow_up_count": developer_tracker.get("follow_up_count", 0),
        "owner_operationally_acceptable": intake.get("owner_operationally_acceptable"),
        "blocked_state_preserved": intake.get("blocked_state_preserved"),
        "recovery_target_score": intake.get("minimum_owner_readiness_score"),
        "minimum_score_improvement_needed": intake.get("readiness_score_gap"),
        "not_trade_instruction": True,
    }
