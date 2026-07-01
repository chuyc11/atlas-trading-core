"""Quality issue evidence package."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_quality_issue_evidence_package(*, as_of_date: str = DEFAULT_AS_OF_DATE, classification: dict[str, Any], blocked_gate_intake: dict[str, Any]) -> dict[str, Any]:
    items = []
    for row in classification.get("classifications", []):
        exception_id = row.get("exception_id")
        items.append(
            {
                "quality_exception_id": exception_id,
                "warning_or_issue_id": exception_id,
                "source_artifact": "quality_exception_classification.json",
                "mapped_root_cause": row.get("category"),
                "evidence_artifacts": ["quality_exception_classification.json", "blocked_gate_intake.json"],
                "evidence_quality": "strong" if row.get("status") == "classified" else "weak",
                "known_non_blocking": row.get("severity") != "blocking",
                "requires_developer_follow_up": row.get("developer_follow_up_required", False),
                "requires_more_history": row.get("category") == "insufficient_history",
                "readiness_score_relevance": row.get("readiness_score_impact", 0),
            }
        )
    return {
        "package_id": "A-SHARE-QUALITY-ISSUE-EVIDENCE-PACKAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": blocked_gate_intake.get("source_gate_decision"),
        "quality_issue_count": len(items),
        "items": items,
    }

