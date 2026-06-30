"""Controlled reevaluation decision."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_controlled_reevaluation_decision(*, as_of_date: str = DEFAULT_AS_OF_DATE, skip_decision: dict[str, Any]) -> dict[str, Any]:
    skipped = skip_decision.get("reevaluation_skipped") is True
    return {
        "decision_id": "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "decision": "skipped_not_ready" if skipped else "allowed_not_executed",
        "reevaluation_skipped": skipped,
        "reevaluation_skip_reason": skip_decision.get("reevaluation_skip_reason"),
        "owner_operationally_acceptable": False,
        "source_gate_decision_preserved": True,
        "gate_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "not_investment_advice": True,
        "not_order_instruction": True,
    }

