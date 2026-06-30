"""Waiver candidate evaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_waiver_candidate_evaluation(*, as_of_date: str = DEFAULT_AS_OF_DATE, classification: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    for row in classification.get("classifications", []):
        allowed = row.get("waiver_allowed") is True and row.get("category") not in {"boundary_quality_issue", "protected_path_issue"}
        candidates.append(
            {
                "exception_id": row["exception_id"],
                "category": row["category"],
                "waiver_candidate": row.get("waiver_candidate") is True,
                "waiver_allowed": allowed,
                "auto_waiver_allowed": False,
                "waiver_scope": "owner_review_only" if allowed else "not_allowed",
                "waiver_changes_gate_decision": False,
                "approved_for_trading": False,
                "reason_required": allowed,
            }
        )
    return {
        "evaluation_id": "A-SHARE-WAIVER-CANDIDATE-EVALUATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "candidate_count": len(candidates),
        "waiver_candidates": candidates,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "waiver_changes_gate_decision": False,
    }
