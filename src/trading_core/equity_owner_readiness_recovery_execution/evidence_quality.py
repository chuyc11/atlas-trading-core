"""Evidence quality assessment for recovery execution."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_recovery_evidence_quality_assessment(*, as_of_date: str = DEFAULT_AS_OF_DATE, evidence_registry: dict[str, Any]) -> dict[str, Any]:
    available = evidence_registry.get("evidence_available_count", 0)
    total = evidence_registry.get("evidence_record_count", 0)
    return {
        "assessment_id": "A-SHARE-RECOVERY-EVIDENCE-QUALITY-ASSESSMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "evidence_record_count": total,
        "evidence_available_count": available,
        "missing_evidence_count": max(total - available, 0),
        "evidence_quality_grade": "insufficient" if available == 0 else "partial",
        "evidence_sufficient_for_completion": available == total and total > 0,
        "evidence_sufficient_for_gate_reevaluation": False,
        "does_not_fabricate_evidence": True,
        "records": [
            {
                "evidence_id": row["evidence_id"],
                "evidence_available": row["evidence_available"],
                "evidence_confidence": row["evidence_confidence"],
                "quality_issue": "" if row["evidence_available"] else "missing_completion_evidence",
            }
            for row in evidence_registry.get("records", [])
        ],
    }
