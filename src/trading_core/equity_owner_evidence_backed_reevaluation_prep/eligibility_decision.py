"""Controlled reevaluation eligibility decision."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_controlled_reevaluation_eligibility_decision(*, as_of_date: str = DEFAULT_AS_OF_DATE, sufficiency: dict[str, Any], gap_decision: dict[str, Any]) -> dict[str, Any]:
    ready = sufficiency.get("ready_for_controlled_gate_reevaluation") is True and gap_decision.get("blocks_controlled_gate_reevaluation") is False
    return {
        "decision_id": "A-SHARE-CONTROLLED-REEVALUATION-ELIGIBILITY-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "ready_for_controlled_gate_reevaluation": ready,
        "eligibility_decision": "eligible" if ready else "not_eligible",
        "reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "blocking_reasons": [] if ready else sorted(set(sufficiency.get("blocking_reasons", []) + ["remaining_gap_decision_blocks_reevaluation"])),
    }

