"""Input availability for v0.8.21 owner-readiness closeout review."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.equity_owner_closeout_review.io import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

V0820_FILES = {
    "v0820_outcome_config": "v0820_outcome_config.json",
    "v0820_input_availability": "v0820_input_availability.json",
    "v0820_source_resolution": "v0820_source_resolution.json",
    "v0820_date_alignment": "v0820_date_alignment.json",
    "v0820_branch_decision": "v0820_branch_decision.json",
    "controlled_gate_reevaluation_outcome": "controlled_gate_reevaluation_outcome.json",
    "final_blocked_closeout": "final_blocked_closeout.json",
    "threshold_preservation_check": "threshold_preservation_check.json",
    "waiver_exclusion_check": "waiver_exclusion_check.json",
    "boundary_preservation_check": "boundary_preservation_check.json",
    "v0820_owner_outcome_summary": "v0820_owner_outcome_summary.json",
    "v0820_source_trace": "v0820_source_trace.json",
    "v0820_boundary_check": "v0820_boundary_check.json",
    "v0820_manifest": "v0820_manifest.json",
}

AUDIT_FILES = {
    "v0813_owner_readiness_gate_audit": "a_share_owner_readiness_gate_audit.json",
    "v0814_quality_exception_workflow_audit": "a_share_owner_quality_exception_workflow_audit.json",
    "v0815_recovery_plan_audit": "a_share_owner_readiness_recovery_audit.json",
    "v0816_recovery_execution_audit": "a_share_owner_readiness_recovery_execution_audit.json",
    "v0817_controlled_reevaluation_audit": "a_share_owner_controlled_gate_reevaluation_audit.json",
    "v0818_recovery_evidence_audit": "a_share_owner_recovery_evidence_audit.json",
    "v0819_evidence_backed_prep_audit": "a_share_owner_evidence_backed_reevaluation_prep_audit.json",
    "v0820_gate_outcome_audit": "a_share_owner_v0820_gate_outcome_audit.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    v0820_dir = paths.data_dir / "equity_owner_v0820_gate_outcome" / "daily" / as_of_date
    sources = {key: v0820_dir / name for key, name in V0820_FILES.items()}
    sources.update({key: paths.data_dir / "equity_data_quality" / name for key, name in AUDIT_FILES.items()})
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in sources.items()}
    missing = sorted(key for key, path in sources.items() if not path.exists())
    v0820_audit = payloads["v0820_gate_outcome_audit"]
    branch = payloads["v0820_branch_decision"]
    controlled = payloads["controlled_gate_reevaluation_outcome"]
    closeout = payloads["final_blocked_closeout"]
    summary = payloads["v0820_owner_outcome_summary"]
    threshold = payloads["threshold_preservation_check"]
    waiver = payloads["waiver_exclusion_check"]
    blocking: list[str] = []
    if missing:
        blocking.append("required_inputs_missing")
    if v0820_audit.get("overall_passed") is not True:
        blocking.append("v0820_outcome_audit_not_passed")
    if v0820_audit.get("blocking_reasons") not in ([], None):
        blocking.append("v0820_outcome_audit_has_blockers")
    if v0820_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("v0820_recommended_next_version_mismatch")
    if branch.get("selected_branch") != "final_blocked_closeout":
        blocking.append("selected_v0820_branch_not_final_blocked_closeout")
    if controlled.get("controlled_reevaluation_executed") is not False:
        blocking.append("controlled_reevaluation_was_executed")
    if closeout.get("final_blocked_closeout_generated") is not True:
        blocking.append("final_blocked_closeout_missing")
    if summary.get("source_gate_decision") != "blocked" or closeout.get("source_gate_decision") != "blocked":
        blocking.append("source_gate_decision_not_blocked")
    if threshold.get("threshold_lowered") is not False or waiver.get("auto_waiver_allowed") is not False:
        blocking.append("threshold_or_auto_waiver_boundary_broken")
    return {
        "availability_id": "A-SHARE-OWNER-CLOSEOUT-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
        "missing_required_inputs": missing,
        "v0820_outcome_audit_passed": v0820_audit.get("overall_passed") is True,
        "selected_v0820_branch": branch.get("selected_branch"),
        "controlled_reevaluation_executed": controlled.get("controlled_reevaluation_executed"),
        "final_blocked_closeout_generated": closeout.get("final_blocked_closeout_generated"),
        "source_gate_decision": summary.get("source_gate_decision"),
        "previous_readiness_score": summary.get("previous_readiness_score"),
        "minimum_owner_readiness_score": summary.get("minimum_owner_readiness_score"),
        "score_gap": _score_gap(summary, closeout),
        "owner_operationally_acceptable": summary.get("owner_operationally_acceptable"),
        "new_gate_score_generated": controlled.get("new_controlled_readiness_score_generated"),
        "new_gate_decision_generated": controlled.get("new_controlled_gate_decision_generated"),
        "threshold_lowered": threshold.get("threshold_lowered", summary.get("threshold_lowered")),
        "auto_waiver_allowed": waiver.get("auto_waiver_allowed", summary.get("auto_waiver_allowed")),
        "manual_waiver_approval_recorded": waiver.get("manual_waiver_approval_recorded", summary.get("manual_waiver_approval_recorded")),
        "waiver_used_for_outcome": waiver.get("waiver_used_for_outcome", summary.get("waiver_used_for_outcome")),
        "remaining_gap_count": closeout.get("remaining_gap_count"),
        "blocking_gap_count": closeout.get("blocking_gap_count"),
        "overall_evidence_quality": closeout.get("overall_evidence_quality"),
        "evidence_insufficient": closeout.get("evidence_insufficient"),
        "preferred_source": "v0.8.20_gate_outcome_artifacts",
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }


def _score_gap(summary: dict[str, Any], closeout: dict[str, Any]) -> int | None:
    previous = summary.get("previous_readiness_score", closeout.get("previous_readiness_score"))
    minimum = summary.get("minimum_owner_readiness_score", closeout.get("minimum_owner_readiness_score"))
    if isinstance(previous, int) and isinstance(minimum, int):
        return minimum - previous
    return None
