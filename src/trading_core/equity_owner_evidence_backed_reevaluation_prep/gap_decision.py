"""Remaining evidence gap decision."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_remaining_evidence_gap_decision(*, as_of_date: str = DEFAULT_AS_OF_DATE, gaps: dict[str, Any], blockers: dict[str, Any], sufficiency: dict[str, Any]) -> dict[str, Any]:
    gap_count = int(gaps.get("gap_count", 0) or 0)
    blocker_count = int(blockers.get("blocker_count", 0) or 0)
    return {
        "decision_id": "A-SHARE-REMAINING-EVIDENCE-GAP-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "remaining_gap_count": gap_count,
        "blocking_gap_count": blocker_count,
        "has_remaining_evidence_gaps": gap_count > 0,
        "blocks_controlled_gate_reevaluation": blocker_count > 0 or not sufficiency.get("ready_for_controlled_gate_reevaluation"),
        "decision": "blocked_by_remaining_evidence_gaps" if blocker_count > 0 else "no_remaining_evidence_gaps",
        "items": blockers.get("items", gaps.get("items", [])),
    }

