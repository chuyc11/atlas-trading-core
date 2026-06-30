"""Skip decision for controlled gate reevaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_reevaluation_skip_decision(*, as_of_date: str = DEFAULT_AS_OF_DATE, guard: dict[str, Any], execution_plan: dict[str, Any]) -> dict[str, Any]:
    skipped = guard.get("reevaluation_allowed") is not True
    return {
        "decision_id": "A-SHARE-OWNER-REEVALUATION-SKIP-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "reevaluation_skipped": skipped,
        "reevaluation_skip_reason": "not_ready" if skipped else "",
        "skip_reason_details": list(guard.get("block_reasons", [])),
        "owner_operationally_acceptable": False,
        "source_gate_decision_preserved": True,
        "gate_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "execution_status": execution_plan.get("execution_status"),
        "overall_passed": True,
        "blocking_reasons": [],
    }

