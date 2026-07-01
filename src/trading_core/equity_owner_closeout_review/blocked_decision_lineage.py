"""Blocked-decision lineage artifact."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_blocked_decision_lineage(*, as_of_date: str = DEFAULT_AS_OF_DATE, lineage: dict[str, Any]) -> dict[str, Any]:
    rows = [
        {
            "version": row["version"],
            "stage": row["stage"],
            "source_gate_decision": row["source_gate_decision"],
            "audit_overall_passed": row["audit_overall_passed"],
            "blocked_state_visible": row["source_gate_decision"] == "blocked",
            "recommended_next_version": row["recommended_next_version"],
        }
        for row in lineage.get("stages", [])
    ]
    return {
        "lineage_id": "A-SHARE-BLOCKED-DECISION-LINEAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": all(row["blocked_state_visible"] for row in rows),
        "blocking_reasons": [] if all(row["blocked_state_visible"] for row in rows) else ["blocked_state_not_visible_in_all_stages"],
        "warnings": [],
        "stages": rows,
        "source_gate_decision": "blocked",
        "blocked_decision_preserved": all(row["source_gate_decision"] == "blocked" for row in rows),
    }
