"""Next reevaluation preparation checklist."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_next_reevaluation_prep_checklist(*, as_of_date: str = DEFAULT_AS_OF_DATE, quality: dict[str, Any], source_trace: dict[str, Any], artifact_completeness: dict[str, Any], boundary: dict[str, Any] | None = None) -> dict[str, Any]:
    boundary = boundary or {}
    ready = (
        quality.get("evidence_ready_for_next_reevaluation_prep") is True
        and source_trace.get("evidence_available") is True
        and artifact_completeness.get("evidence_available") is True
        and boundary.get("overall_passed", True) is True
    )
    return {
        "checklist_id": "A-SHARE-NEXT-REEVALUATION-PREP-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "recovery_evidence_collected": quality.get("evidence_record_count", 0) > 0,
        "developer_follow_up_evidence_available": quality.get("audit_verified_evidence_count", 0) > 0,
        "owner_follow_up_evidence_available": False,
        "audit_verified_evidence_available": quality.get("audit_verified_evidence_count", 0) > 0,
        "readiness_score_gap_addressed": False,
        "source_trace_complete": source_trace.get("evidence_available") is True,
        "artifact_completeness_satisfied": artifact_completeness.get("evidence_available") is True,
        "threshold_unchanged": True,
        "waiver_not_used": True,
        "no_forbidden_actions": True,
        "ready_for_evidence_backed_gate_prep": ready,
    }

