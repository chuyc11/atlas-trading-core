"""Manifest and summary for owner recovery evidence."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_recovery_evidence_manifest(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    source_gate_decision: str,
    source_readiness_score: int,
    minimum_owner_readiness_score: int,
    quality: dict[str, Any],
    score: dict[str, Any],
    prep: dict[str, Any],
    boundary: dict[str, Any],
    blocking_reasons: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-RECOVERY-EVIDENCE-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": source_gate_decision,
        "source_readiness_score": source_readiness_score,
        "minimum_owner_readiness_score": minimum_owner_readiness_score,
        "score_gap": max(minimum_owner_readiness_score - source_readiness_score, 0),
        "evidence_record_count": quality.get("evidence_record_count", 0),
        "strong_evidence_count": quality.get("strong_evidence_count", 0),
        "audit_verified_evidence_count": quality.get("audit_verified_evidence_count", 0),
        "missing_evidence_count": quality.get("missing_evidence_count", 0),
        "overall_evidence_quality": quality.get("overall_evidence_quality", "none"),
        "actual_audited_score_changed": score.get("actual_audited_score_changed", False),
        "new_audited_score": score.get("new_audited_score"),
        "ready_for_evidence_backed_gate_prep": prep.get("ready_for_evidence_backed_gate_prep", False),
        "source_gate_decision_preserved": True,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "full_pytest_run": False,
        "targeted_pytest_required": True,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_recovery_evidence_summary(*, as_of_date: str, manifest: dict[str, Any], gap_register: dict[str, Any], blockers: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-RECOVERY-EVIDENCE-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": manifest.get("source_gate_decision"),
        "source_readiness_score": manifest.get("source_readiness_score"),
        "minimum_owner_readiness_score": manifest.get("minimum_owner_readiness_score"),
        "score_gap": manifest.get("score_gap"),
        "evidence_record_count": manifest.get("evidence_record_count"),
        "strong_evidence_count": manifest.get("strong_evidence_count"),
        "audit_verified_evidence_count": manifest.get("audit_verified_evidence_count"),
        "missing_evidence_count": manifest.get("missing_evidence_count"),
        "overall_evidence_quality": manifest.get("overall_evidence_quality"),
        "evidence_gap_count": gap_register.get("gap_count"),
        "remaining_blocker_count": blockers.get("blocker_count"),
        "evidence_ready_for_next_reevaluation_prep": manifest.get("ready_for_evidence_backed_gate_prep"),
        "actual_audited_score_changed": manifest.get("actual_audited_score_changed"),
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "source_gate_decision_preserved": True,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "not_investment_advice": True,
        "not_order_instruction": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

