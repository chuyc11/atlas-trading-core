"""Manifest and summary for evidence-backed reevaluation prep."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_prep_manifest(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    availability: dict[str, Any],
    sufficiency: dict[str, Any],
    eligibility: dict[str, Any],
    gap_decision: dict[str, Any],
    boundary: dict[str, Any],
    blocking_reasons: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-EVIDENCE-BACKED-PREP-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": availability.get("source_gate_decision"),
        "source_readiness_score": availability.get("source_readiness_score"),
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "score_gap": availability.get("score_gap"),
        "evidence_record_count": availability.get("evidence_record_count"),
        "strong_evidence_count": availability.get("strong_evidence_count"),
        "audit_verified_evidence_count": availability.get("audit_verified_evidence_count"),
        "missing_evidence_count": availability.get("missing_evidence_count"),
        "overall_evidence_quality": availability.get("overall_evidence_quality"),
        "remaining_gap_count": gap_decision.get("remaining_gap_count"),
        "blocking_gap_count": gap_decision.get("blocking_gap_count"),
        "evidence_ready_for_next_reevaluation_prep": availability.get("evidence_ready_for_next_reevaluation_prep"),
        "ready_for_controlled_gate_reevaluation": eligibility.get("ready_for_controlled_gate_reevaluation"),
        "eligibility_decision": eligibility.get("eligibility_decision"),
        "source_gate_decision_preserved": True,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "reevaluation_executed": False,
        "score_impact_readiness_is_not_official_score": True,
        "full_pytest_run": False,
        "targeted_pytest_required": True,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "sufficiency_blocking_reasons": sufficiency.get("blocking_reasons", []),
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_prep_summary(*, as_of_date: str, manifest: dict[str, Any], input_package: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-EVIDENCE-BACKED-PREP-SUMMARY",
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
        "remaining_gap_count": manifest.get("remaining_gap_count"),
        "blocking_gap_count": manifest.get("blocking_gap_count"),
        "evidence_ready_for_next_reevaluation_prep": manifest.get("evidence_ready_for_next_reevaluation_prep"),
        "ready_for_controlled_gate_reevaluation": manifest.get("ready_for_controlled_gate_reevaluation"),
        "eligibility_decision": manifest.get("eligibility_decision"),
        "reevaluation_input_package_generated": input_package.get("reevaluation_input_package_generated"),
        "reevaluation_executed": False,
        "actual_audited_score_changed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "source_gate_decision_preserved": True,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "score_impact_readiness_is_not_official_score": True,
        "not_investment_advice": True,
        "not_order_instruction": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

