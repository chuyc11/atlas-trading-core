"""Input availability for v0.8.20 owner gate outcome."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_v0820_gate_outcome.io import load_json
from trading_core.equity_owner_v0820_gate_outcome.outcome_config import BASELINE_VERSION, DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

PREP_KEYS = {
    "evidence_backed_prep_config": "evidence_backed_prep_config.json",
    "evidence_backed_prep_input_availability": "evidence_backed_prep_input_availability.json",
    "evidence_backed_prep_source_resolution": "evidence_backed_prep_source_resolution.json",
    "evidence_backed_prep_date_alignment": "evidence_backed_prep_date_alignment.json",
    "evidence_sufficiency_for_reevaluation_decision": "evidence_sufficiency_for_reevaluation_decision.json",
    "evidence_to_gate_mapping": "evidence_to_gate_mapping.json",
    "reevaluation_input_package": "reevaluation_input_package.json",
    "score_impact_readiness_summary": "score_impact_readiness_summary.json",
    "gate_threshold_preservation_package": "gate_threshold_preservation_package.json",
    "waiver_exclusion_package": "waiver_exclusion_package.json",
    "boundary_preservation_package": "boundary_preservation_package.json",
    "evidence_backed_readiness_checklist": "evidence_backed_readiness_checklist.json",
    "remaining_evidence_gap_decision": "remaining_evidence_gap_decision.json",
    "controlled_reevaluation_eligibility_decision": "controlled_reevaluation_eligibility_decision.json",
    "next_gate_reevaluation_execution_plan": "next_gate_reevaluation_execution_plan.json",
    "evidence_backed_prep_source_trace": "evidence_backed_prep_source_trace.json",
    "evidence_backed_prep_boundary_check": "evidence_backed_prep_boundary_check.json",
    "evidence_backed_prep_manifest": "evidence_backed_prep_manifest.json",
    "evidence_backed_prep_summary": "evidence_backed_prep_summary.json",
}
GATE_KEYS = {
    "owner_readiness_gate_decision": "owner_readiness_gate_decision.json",
    "owner_readiness_score_gate": "owner_readiness_score_gate.json",
    "quality_threshold_evaluation": "quality_threshold_evaluation.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    prep_dir = paths.data_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / as_of_date
    gate_dir = paths.data_dir / "equity_owner_readiness_gate" / "daily" / as_of_date
    sources = {key: prep_dir / name for key, name in PREP_KEYS.items()}
    sources.update({key: gate_dir / name for key, name in GATE_KEYS.items()})
    sources["evidence_backed_prep_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_evidence_backed_reevaluation_prep_audit.json"
    sources["owner_readiness_gate_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json"
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    missing = sorted(key for key, path in sources.items() if not path.exists())
    audit = load_json(sources["evidence_backed_prep_audit"])
    config = load_json(sources["evidence_backed_prep_config"])
    summary = load_json(sources["evidence_backed_prep_summary"])
    eligibility = load_json(sources["controlled_reevaluation_eligibility_decision"])
    input_package = load_json(sources["reevaluation_input_package"])
    threshold = load_json(sources["gate_threshold_preservation_package"])
    waiver = load_json(sources["waiver_exclusion_package"])
    gate_decision = load_json(sources["owner_readiness_gate_decision"])
    gate_audit = load_json(sources["owner_readiness_gate_audit"])
    blocking: list[str] = []
    if missing:
        blocking.append("required_inputs_missing")
    if audit.get("overall_passed") is not True:
        blocking.append("evidence_backed_prep_audit_not_passed")
    if audit.get("blocking_reasons") not in ([], None):
        blocking.append("evidence_backed_prep_audit_has_blockers")
    if audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("evidence_backed_prep_recommended_next_version_mismatch")
    if config.get("target_version") != BASELINE_VERSION:
        blocking.append("evidence_backed_prep_version_mismatch")
    if gate_audit.get("overall_passed") is not True:
        blocking.append("owner_readiness_gate_audit_not_passed")
    if summary.get("source_gate_decision") != "blocked" or gate_decision.get("decision") != "blocked":
        blocking.append("source_gate_decision_not_blocked")
    if summary.get("source_gate_decision_preserved") is not True:
        blocking.append("source_gate_decision_not_preserved")
    if input_package.get("reevaluation_input_package_generated") is not True:
        blocking.append("reevaluation_input_package_missing")
    if summary.get("reevaluation_executed") is not False:
        blocking.append("v0819_reevaluation_already_executed")
    if summary.get("new_gate_score_generated") is not False or summary.get("new_gate_decision_generated") is not False:
        blocking.append("v0819_generated_gate_outputs")
    if threshold.get("threshold_lowered") is not False or waiver.get("auto_waiver_allowed") is not False:
        blocking.append("threshold_or_waiver_boundary_broken")
    return {
        "availability_id": "A-SHARE-OWNER-V0820-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "missing_required_inputs": missing,
        "evidence_backed_prep_audit_passed": audit.get("overall_passed") is True,
        "owner_readiness_gate_audit_passed": gate_audit.get("overall_passed") is True,
        "source_gate_decision": summary.get("source_gate_decision"),
        "source_gate_decision_preserved": summary.get("source_gate_decision_preserved"),
        "previous_readiness_score": summary.get("source_readiness_score"),
        "minimum_owner_readiness_score": summary.get("minimum_owner_readiness_score"),
        "score_gap": summary.get("score_gap"),
        "v0819_eligibility_decision": eligibility.get("eligibility_decision", summary.get("eligibility_decision")),
        "v0819_ready_for_controlled_gate_reevaluation": eligibility.get("ready_for_controlled_gate_reevaluation", summary.get("ready_for_controlled_gate_reevaluation")),
        "reevaluation_input_package_generated": input_package.get("reevaluation_input_package_generated"),
        "remaining_gap_count": summary.get("remaining_gap_count"),
        "blocking_gap_count": summary.get("blocking_gap_count"),
        "overall_evidence_quality": summary.get("overall_evidence_quality"),
        "new_gate_score_generated": summary.get("new_gate_score_generated"),
        "new_gate_decision_generated": summary.get("new_gate_decision_generated"),
        "threshold_lowered": summary.get("threshold_lowered"),
        "auto_waiver_allowed": summary.get("auto_waiver_allowed"),
        "manual_waiver_approval_recorded": summary.get("manual_waiver_approval_recorded"),
        "preferred_source": "v0.8.19_evidence_backed_prep_artifacts",
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }

