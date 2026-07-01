"""Evidence insufficiency lineage artifact."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_evidence_insufficiency_lineage(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    lineage: dict[str, Any],
    availability: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        {
            "version": row["version"],
            "stage": row["stage"],
            "evidence_status": row["evidence_status"],
            "audit_overall_passed": row["audit_overall_passed"],
        }
        for row in lineage.get("stages", [])
    ]
    evidence_insufficient = availability.get("evidence_insufficient") is True
    return {
        "lineage_id": "A-SHARE-EVIDENCE-INSUFFICIENCY-LINEAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": evidence_insufficient,
        "blocking_reasons": [] if evidence_insufficient else ["final_evidence_insufficiency_not_visible"],
        "warnings": [],
        "overall_evidence_quality": availability.get("overall_evidence_quality"),
        "remaining_gap_count": availability.get("remaining_gap_count"),
        "blocking_gap_count": availability.get("blocking_gap_count"),
        "evidence_insufficient": evidence_insufficient,
        "stages": rows,
    }
