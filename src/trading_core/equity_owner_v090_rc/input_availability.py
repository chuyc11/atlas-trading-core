"""Input availability for v0.9.0 RC closeout."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_v090_rc.io import load_json
from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

V0821_FILES = {
    "closeout_review_config": "closeout_review_config.json",
    "closeout_input_availability": "closeout_input_availability.json",
    "closeout_source_resolution": "closeout_source_resolution.json",
    "closeout_date_alignment": "closeout_date_alignment.json",
    "v0813_to_v0820_lineage_review": "v0813_to_v0820_lineage_review.json",
    "blocked_decision_lineage": "blocked_decision_lineage.json",
    "readiness_score_lineage": "readiness_score_lineage.json",
    "evidence_insufficiency_lineage": "evidence_insufficiency_lineage.json",
    "final_blocked_closeout_review": "final_blocked_closeout_review.json",
    "unresolved_blocker_register": "unresolved_blocker_register.json",
    "v090_rc_scope_proposal": "v090_rc_scope_proposal.json",
    "v090_full_regression_plan": "v090_full_regression_plan.json",
    "v090_audit_sweep_plan": "v090_audit_sweep_plan.json",
    "v090_documentation_freeze_checklist": "v090_documentation_freeze_checklist.json",
    "v090_release_risk_register": "v090_release_risk_register.json",
    "v090_release_candidate_readiness_decision": "v090_release_candidate_readiness_decision.json",
    "closeout_source_trace": "closeout_source_trace.json",
    "closeout_boundary_check": "closeout_boundary_check.json",
    "closeout_manifest": "closeout_manifest.json",
    "closeout_summary": "closeout_summary.json",
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
    "v0821_closeout_review_audit": "a_share_owner_closeout_review_audit.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    closeout_dir = paths.data_dir / "equity_owner_closeout_review" / "daily" / as_of_date
    sources = {key: closeout_dir / name for key, name in V0821_FILES.items()}
    sources.update({key: paths.data_dir / "equity_data_quality" / name for key, name in AUDIT_FILES.items()})
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in sources.items()}
    missing = sorted(key for key, path in sources.items() if not path.exists())
    audit = payloads["v0821_closeout_review_audit"]
    summary = payloads["closeout_summary"]
    rc_decision = payloads["v090_release_candidate_readiness_decision"]
    blockers = payloads["unresolved_blocker_register"]
    blocking = []
    if missing:
        blocking.append("required_inputs_missing")
    if audit.get("overall_passed") is not True:
        blocking.append("v0821_closeout_review_audit_not_passed")
    if audit.get("blocking_reasons") not in ([], None):
        blocking.append("v0821_closeout_review_audit_has_blockers")
    if audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("v0821_recommended_next_version_mismatch")
    if summary.get("source_gate_decision") != "blocked":
        blocking.append("source_gate_decision_not_blocked")
    if summary.get("owner_operationally_acceptable") is not False:
        blocking.append("owner_operationally_acceptable_not_false")
    if summary.get("blocked_state_intentional") is not True or summary.get("blocked_state_audited") is not True:
        blocking.append("blocked_state_not_confirmed")
    if summary.get("blocked_state_misrepresented_as_acceptable") is not False:
        blocking.append("blocked_state_misrepresented")
    if blockers.get("blockers_that_block_v090_rc") != 0:
        blocking.append("blockers_block_v090_rc")
    if rc_decision.get("decision") != "ready_with_known_blocked_owner_readiness_state":
        blocking.append("v090_rc_source_decision_not_ready_with_known_blocked_state")
    return {
        "availability_id": "A-SHARE-OWNER-V090-RC-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
        "missing_required_inputs": missing,
        "v0821_closeout_review_audit_passed": audit.get("overall_passed") is True,
        "source_gate_decision": summary.get("source_gate_decision"),
        "known_owner_readiness_state": "blocked",
        "previous_readiness_score": summary.get("previous_readiness_score"),
        "minimum_owner_readiness_score": summary.get("minimum_owner_readiness_score"),
        "score_gap": summary.get("score_gap"),
        "owner_operationally_acceptable": summary.get("owner_operationally_acceptable"),
        "blocked_state_intentional": summary.get("blocked_state_intentional"),
        "blocked_state_audited": summary.get("blocked_state_audited"),
        "blocked_state_misrepresented_as_acceptable": summary.get("blocked_state_misrepresented_as_acceptable"),
        "v090_rc_readiness_source_decision": rc_decision.get("decision"),
        "blocks_owner_readiness_acceptance": blockers.get("blockers_that_block_owner_readiness_acceptance", 0) > 0,
        "blocks_v090_rc": blockers.get("blockers_that_block_v090_rc", 0) > 0,
        "new_gate_score_generated": summary.get("new_gate_score_generated"),
        "new_gate_decision_generated": summary.get("new_gate_decision_generated"),
        "preferred_source": "v0.8.21_closeout_review_artifacts",
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }
