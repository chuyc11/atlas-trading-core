"""Score impact evidence assessment."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_score_impact_evidence_assessment(*, as_of_date: str = DEFAULT_AS_OF_DATE, source_summary: dict[str, Any], status_tracker: dict[str, Any]) -> dict[str, Any]:
    return {
        "assessment_id": "A-SHARE-SCORE-IMPACT-EVIDENCE-ASSESSMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_score": source_summary.get("actual_owner_readiness_score"),
        "threshold_score": source_summary.get("minimum_owner_readiness_score"),
        "source_score_gap": source_summary.get("readiness_score_gap"),
        "score_rewritten_without_audit_evidence": False,
        "readiness_score_rewritten": False,
        "score_improvement_claimed": False,
        "verified_by_audit_only_count": status_tracker.get("verified_by_audit_only_count", 0),
        "score_impact_evidence_sufficient": False,
        "notes": ["v0.8.16 tracks evidence only; it does not rewrite owner readiness score."],
    }


def build_readiness_improvement_evidence_summary(*, as_of_date: str = DEFAULT_AS_OF_DATE, score_assessment: dict[str, Any], evidence_quality: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-READINESS-IMPROVEMENT-EVIDENCE-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "readiness_improvement_evidence_available": False,
        "readiness_improvement_claimed": False,
        "source_score": score_assessment.get("source_score"),
        "threshold_score": score_assessment.get("threshold_score"),
        "source_score_gap": score_assessment.get("source_score_gap"),
        "evidence_quality_grade": evidence_quality.get("evidence_quality_grade"),
        "ready_for_score_reassessment": False,
        "does_not_claim_improvement_without_audit_evidence": True,
    }
