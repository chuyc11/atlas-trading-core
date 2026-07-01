"""Evidence quality grading."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_evidence_quality_grading(*, as_of_date: str = DEFAULT_AS_OF_DATE, task_evidence: dict[str, Any], developer: dict[str, Any], owner: dict[str, Any]) -> dict[str, Any]:
    grades = [item.get("evidence_quality", "none") for item in task_evidence.get("items", [])]
    grades.extend(item.get("evidence_quality", "none") for item in developer.get("items", []))
    grades.extend(item.get("evidence_quality", "none") for item in owner.get("items", []))
    counts = {grade: grades.count(grade) for grade in ["none", "weak", "partial", "strong", "audit_verified"]}
    ready = counts["audit_verified"] > 0 and counts["none"] == 0
    overall = "audit_verified" if ready else "strong" if counts["strong"] else "partial" if counts["partial"] else "weak" if counts["weak"] else "none"
    return {
        "grading_id": "A-SHARE-EVIDENCE-QUALITY-GRADING",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "evidence_record_count": len(grades),
        "strong_evidence_count": counts["strong"],
        "audit_verified_evidence_count": counts["audit_verified"],
        "partial_evidence_count": counts["partial"],
        "weak_evidence_count": counts["weak"],
        "missing_evidence_count": counts["none"],
        "overall_evidence_quality": overall,
        "evidence_ready_for_next_reevaluation_prep": ready,
    }

