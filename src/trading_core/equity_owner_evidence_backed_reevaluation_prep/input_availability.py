"""Input availability for evidence-backed reevaluation prep."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.io import load_json
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import BASELINE_VERSION, DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

RECOVERY_KEYS = {
    "recovery_evidence_config": "recovery_evidence_config.json",
    "recovery_evidence_input_availability": "recovery_evidence_input_availability.json",
    "recovery_evidence_source_resolution": "recovery_evidence_source_resolution.json",
    "recovery_evidence_date_alignment": "recovery_evidence_date_alignment.json",
    "recovery_task_evidence_collection": "recovery_task_evidence_collection.json",
    "developer_follow_up_evidence_package": "developer_follow_up_evidence_package.json",
    "owner_follow_up_evidence_package": "owner_follow_up_evidence_package.json",
    "quality_issue_evidence_package": "quality_issue_evidence_package.json",
    "warning_mapping_evidence_package": "warning_mapping_evidence_package.json",
    "source_trace_improvement_evidence": "source_trace_improvement_evidence.json",
    "markdown_quality_improvement_evidence": "markdown_quality_improvement_evidence.json",
    "artifact_completeness_evidence": "artifact_completeness_evidence.json",
    "readiness_improvement_evidence_ledger": "readiness_improvement_evidence_ledger.json",
    "evidence_backed_score_impact_estimate": "evidence_backed_score_impact_estimate.json",
    "evidence_quality_grading": "evidence_quality_grading.json",
    "evidence_gap_register": "evidence_gap_register.json",
    "remaining_blocker_register": "remaining_blocker_register.json",
    "next_reevaluation_prep_checklist": "next_reevaluation_prep_checklist.json",
    "recovery_evidence_source_trace": "recovery_evidence_source_trace.json",
    "recovery_evidence_boundary_check": "recovery_evidence_boundary_check.json",
    "recovery_evidence_manifest": "recovery_evidence_manifest.json",
    "recovery_evidence_summary": "recovery_evidence_summary.json",
}
CONTROLLED_KEYS = {
    "controlled_reevaluation_decision": "controlled_reevaluation_decision.json",
    "controlled_evidence_sufficiency_check": "evidence_sufficiency_check.json",
    "controlled_reevaluation_boundary_check": "controlled_reevaluation_boundary_check.json",
}
GATE_KEYS = {
    "owner_readiness_gate_decision": "owner_readiness_gate_decision.json",
    "owner_readiness_score_gate": "owner_readiness_score_gate.json",
    "quality_threshold_evaluation": "quality_threshold_evaluation.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    recovery_dir = paths.data_dir / "equity_owner_recovery_evidence" / "daily" / as_of_date
    controlled_dir = paths.data_dir / "equity_owner_controlled_gate_reevaluation" / "daily" / as_of_date
    gate_dir = paths.data_dir / "equity_owner_readiness_gate" / "daily" / as_of_date
    sources = {key: recovery_dir / name for key, name in RECOVERY_KEYS.items()}
    sources.update({key: controlled_dir / name for key, name in CONTROLLED_KEYS.items()})
    sources.update({key: gate_dir / name for key, name in GATE_KEYS.items()})
    sources["recovery_evidence_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_recovery_evidence_audit.json"
    sources["controlled_reevaluation_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_controlled_gate_reevaluation_audit.json"
    sources["owner_readiness_gate_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json"
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    missing = sorted(key for key, path in sources.items() if not path.exists())
    recovery_audit = load_json(sources["recovery_evidence_audit"])
    recovery_config = load_json(sources["recovery_evidence_config"])
    summary = load_json(sources["recovery_evidence_summary"])
    manifest = load_json(sources["recovery_evidence_manifest"])
    quality = load_json(sources["evidence_quality_grading"])
    gaps = load_json(sources["evidence_gap_register"])
    blockers = load_json(sources["remaining_blocker_register"])
    prep = load_json(sources["next_reevaluation_prep_checklist"])
    controlled_audit = load_json(sources["controlled_reevaluation_audit"])
    controlled_decision = load_json(sources["controlled_reevaluation_decision"])
    gate_audit = load_json(sources["owner_readiness_gate_audit"])
    gate_decision = load_json(sources["owner_readiness_gate_decision"])
    blocking: list[str] = []
    if missing:
        blocking.append("required_inputs_missing")
    if recovery_audit.get("overall_passed") is not True:
        blocking.append("recovery_evidence_audit_not_passed")
    if recovery_audit.get("blocking_reasons") not in ([], None):
        blocking.append("recovery_evidence_audit_has_blockers")
    if recovery_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("recovery_evidence_recommended_next_version_mismatch")
    if recovery_config.get("target_version") != BASELINE_VERSION:
        blocking.append("recovery_evidence_version_mismatch")
    if controlled_audit.get("overall_passed") is not True:
        blocking.append("controlled_reevaluation_audit_not_passed")
    if gate_audit.get("overall_passed") is not True:
        blocking.append("owner_readiness_gate_audit_not_passed")
    if summary.get("source_gate_decision") != "blocked" or gate_decision.get("decision") != "blocked":
        blocking.append("source_gate_decision_not_blocked")
    if summary.get("source_gate_decision_preserved") is not True:
        blocking.append("source_gate_decision_not_preserved")
    if summary.get("new_gate_score_generated") is not False or controlled_decision.get("new_gate_score_generated") is not False:
        blocking.append("source_generated_new_gate_score")
    if summary.get("new_gate_decision_generated") is not False or controlled_decision.get("new_gate_decision_generated") is not False:
        blocking.append("source_generated_new_gate_decision")
    if summary.get("threshold_lowered") is not False:
        blocking.append("source_threshold_lowered")
    if summary.get("auto_waiver_allowed") is not False:
        blocking.append("source_auto_waiver_allowed")
    return {
        "availability_id": "A-SHARE-OWNER-EVIDENCE-BACKED-REEVALUATION-PREP-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "missing_required_inputs": missing,
        "recovery_evidence_audit_passed": recovery_audit.get("overall_passed") is True,
        "controlled_reevaluation_audit_passed": controlled_audit.get("overall_passed") is True,
        "owner_readiness_gate_audit_passed": gate_audit.get("overall_passed") is True,
        "source_gate_decision": summary.get("source_gate_decision"),
        "source_gate_decision_preserved": summary.get("source_gate_decision_preserved"),
        "source_readiness_score": summary.get("source_readiness_score"),
        "minimum_owner_readiness_score": summary.get("minimum_owner_readiness_score"),
        "score_gap": summary.get("score_gap"),
        "evidence_record_count": quality.get("evidence_record_count", summary.get("evidence_record_count")),
        "strong_evidence_count": quality.get("strong_evidence_count", summary.get("strong_evidence_count")),
        "audit_verified_evidence_count": quality.get("audit_verified_evidence_count", summary.get("audit_verified_evidence_count")),
        "missing_evidence_count": quality.get("missing_evidence_count", summary.get("missing_evidence_count")),
        "overall_evidence_quality": quality.get("overall_evidence_quality", summary.get("overall_evidence_quality")),
        "remaining_gap_count": gaps.get("gap_count", summary.get("evidence_gap_count")),
        "blocking_gap_count": blockers.get("blocker_count", summary.get("remaining_blocker_count")),
        "evidence_ready_for_next_reevaluation_prep": prep.get("ready_for_evidence_backed_gate_prep", summary.get("evidence_ready_for_next_reevaluation_prep")),
        "actual_audited_score_changed": summary.get("actual_audited_score_changed"),
        "new_audited_score": summary.get("new_audited_score"),
        "new_gate_score_generated": summary.get("new_gate_score_generated"),
        "new_gate_decision_generated": summary.get("new_gate_decision_generated"),
        "threshold_lowered": summary.get("threshold_lowered"),
        "auto_waiver_allowed": summary.get("auto_waiver_allowed"),
        "manual_waiver_approval_recorded": summary.get("manual_waiver_approval_recorded"),
        "preferred_source": "v0.8.18_recovery_evidence_artifacts",
        "source_artifacts": {key: str(path) for key, path in sources.items()},
        "manifest_artifact_count": len(manifest.get("output_artifacts", {})),
    }

