"""Readiness score lineage artifact."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_readiness_score_lineage(*, as_of_date: str = DEFAULT_AS_OF_DATE, lineage: dict[str, Any], availability: dict[str, Any] | None = None) -> dict[str, Any]:
    rows = [
        {
            "version": row["version"],
            "stage": row["stage"],
            "readiness_score_if_available": row["readiness_score_if_available"],
            "minimum_owner_readiness_score": row["minimum_owner_readiness_score"],
            "score_gap_if_available": row["score_gap_if_available"],
            "new_gate_score_generated": row["new_gate_score_generated"],
            "new_gate_decision_generated": row["new_gate_decision_generated"],
            "source_missing_reason": row.get("source_missing_reason", {}),
        }
        for row in lineage.get("stages", [])
    ]
    availability = availability or {}
    previous_score = availability.get("previous_readiness_score", _first_present(row["readiness_score_if_available"] for row in rows))
    minimum_score = availability.get("minimum_owner_readiness_score", _first_present(row["minimum_owner_readiness_score"] for row in rows))
    score_gap = availability.get("score_gap", _first_present(row["score_gap_if_available"] for row in rows))
    if score_gap is None and isinstance(previous_score, int) and isinstance(minimum_score, int):
        score_gap = minimum_score - previous_score
    passed = previous_score is not None and minimum_score is not None and score_gap is not None
    return {
        "lineage_id": "A-SHARE-READINESS-SCORE-LINEAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": passed,
        "blocking_reasons": [] if passed else ["readiness_score_or_threshold_not_visible"],
        "warnings": [],
        "previous_readiness_score": previous_score,
        "minimum_owner_readiness_score": minimum_score,
        "score_gap": score_gap,
        "new_gate_score_generated_anywhere": lineage.get("new_gate_score_generated_anywhere"),
        "new_gate_decision_generated_anywhere": lineage.get("new_gate_decision_generated_anywhere"),
        "stages": rows,
    }


def _first_present(values) -> Any:
    for value in values:
        if value is not None:
            return value
    return None
