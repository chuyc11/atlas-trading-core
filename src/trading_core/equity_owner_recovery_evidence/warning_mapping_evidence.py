"""Warning mapping evidence package."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_warning_mapping_evidence_package(*, as_of_date: str = DEFAULT_AS_OF_DATE, threshold_evaluation: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    classification_by_gate = {row.get("source_gate"): row for row in classification.get("classifications", [])}
    items = []
    for warning in threshold_evaluation.get("warnings", []):
        source_gate = "trend_sufficiency_quality_gate" if "history" in warning else "warning_issue_quality_gate"
        row = classification_by_gate.get(source_gate, {})
        items.append(
            {
                "quality_exception_id": row.get("exception_id", warning),
                "warning_or_issue_id": warning,
                "source_artifact": "quality_threshold_evaluation.json",
                "mapped_root_cause": row.get("category", warning),
                "evidence_artifacts": ["quality_threshold_evaluation.json", "quality_exception_classification.json"],
                "evidence_quality": "strong" if row else "partial",
                "known_non_blocking": True,
                "requires_developer_follow_up": row.get("developer_follow_up_required", False),
                "requires_more_history": "history" in warning,
                "readiness_score_relevance": row.get("readiness_score_impact", 0),
            }
        )
    return {
        "package_id": "A-SHARE-WARNING-MAPPING-EVIDENCE-PACKAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "warning_count": len(items),
        "known_non_blocking_warning_count": sum(1 for item in items if item["known_non_blocking"]),
        "items": items,
    }

