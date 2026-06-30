"""Execution plan for controlled gate reevaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_reevaluation_execution_plan(*, as_of_date: str = DEFAULT_AS_OF_DATE, prerequisite_validation: dict[str, Any]) -> dict[str, Any]:
    allowed = prerequisite_validation.get("reevaluation_prerequisites_met") is True
    return {
        "plan_id": "A-SHARE-OWNER-CONTROLLED-REEVALUATION-EXECUTION-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "execution_status": "not_executed" if not allowed else "allowed_but_not_executed_by_this_adapter",
        "reevaluation_allowed": allowed,
        "gate_reevaluation_executed": False,
        "rerun_owner_readiness_gate": False,
        "rerun_build_from_existing_data": False,
        "rerun_daily_pack": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "future_version": RECOMMENDED_NEXT_VERSION,
        "blocking_reasons": list(prerequisite_validation.get("failed_prerequisites", [])),
    }

