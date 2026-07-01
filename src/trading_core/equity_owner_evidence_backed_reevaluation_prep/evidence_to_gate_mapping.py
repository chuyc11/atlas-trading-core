"""Map recovery evidence and gaps to owner-readiness gate prerequisites."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_evidence_to_gate_mapping(*, as_of_date: str = DEFAULT_AS_OF_DATE, gaps: dict[str, Any], sufficiency: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for item in gaps.get("items", []):
        rows.append(
            {
                "gap_id": item.get("gap_id"),
                "related_exception_id": item.get("related_exception_id"),
                "gate_prerequisite": "owner_readiness_evidence",
                "blocks_controlled_reevaluation": item.get("blocks_next_reevaluation_prep") is True,
                "required_next_action": item.get("recommended_next_action"),
            }
        )
    return {
        "mapping_id": "A-SHARE-EVIDENCE-TO-GATE-MAPPING",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mapping_count": len(rows),
        "items": rows,
        "ready_for_controlled_gate_reevaluation": sufficiency.get("ready_for_controlled_gate_reevaluation"),
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
    }

