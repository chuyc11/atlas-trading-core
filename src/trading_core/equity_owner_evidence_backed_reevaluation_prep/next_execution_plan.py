"""Next controlled reevaluation execution plan."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_next_gate_reevaluation_execution_plan(*, as_of_date: str = DEFAULT_AS_OF_DATE, eligibility: dict[str, Any]) -> dict[str, Any]:
    eligible = eligibility.get("ready_for_controlled_gate_reevaluation") is True
    return {
        "plan_id": "A-SHARE-NEXT-GATE-REEVALUATION-EXECUTION-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "next_action": "execute_controlled_gate_reevaluation" if eligible else "final_blocked_closeout_or_further_evidence_collection",
        "v0_8_19_executes_gate": False,
        "reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "ready_for_controlled_gate_reevaluation": eligible,
        "blocking_reasons": eligibility.get("blocking_reasons", []),
    }

