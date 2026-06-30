"""Input availability for controlled owner-readiness gate reevaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import BASELINE_VERSION, DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION
from trading_core.equity_owner_controlled_gate_reevaluation.io import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

RECOVERY_EXECUTION_KEYS = {
    "recovery_execution_config": "recovery_execution_config.json",
    "recovery_execution_input_availability": "recovery_execution_input_availability.json",
    "recovery_execution_source_resolution": "recovery_execution_source_resolution.json",
    "recovery_execution_date_alignment": "recovery_execution_date_alignment.json",
    "recovery_task_evidence_registry": "recovery_task_evidence_registry.json",
    "recovery_task_status_tracker": "recovery_task_status_tracker.json",
    "developer_follow_up_evidence_tracker": "developer_follow_up_evidence_tracker.json",
    "owner_follow_up_evidence_tracker": "owner_follow_up_evidence_tracker.json",
    "audit_only_verification_evidence": "audit_only_verification_evidence.json",
    "recovery_task_completion_evaluation": "recovery_task_completion_evaluation.json",
    "recovery_evidence_quality_assessment": "recovery_evidence_quality_assessment.json",
    "score_impact_evidence_assessment": "score_impact_evidence_assessment.json",
    "readiness_improvement_evidence_summary": "readiness_improvement_evidence_summary.json",
    "gate_reevaluation_prerequisite_checklist": "gate_reevaluation_prerequisite_checklist.json",
    "gate_reevaluation_readiness_decision": "gate_reevaluation_readiness_decision.json",
    "controlled_reevaluation_plan": "controlled_reevaluation_plan.json",
    "blocked_state_preservation_check": "blocked_state_preservation_check.json",
    "threshold_preservation_check": "threshold_preservation_check.json",
    "waiver_preservation_check": "waiver_preservation_check.json",
    "recovery_execution_source_trace": "recovery_execution_source_trace.json",
    "recovery_execution_boundary_check": "recovery_execution_boundary_check.json",
    "recovery_execution_manifest": "recovery_execution_manifest.json",
    "recovery_execution_summary": "recovery_execution_summary.json",
}

GATE_KEYS = {
    "owner_readiness_gate_decision": "owner_readiness_gate_decision.json",
    "owner_readiness_gate_boundary_check": "owner_readiness_gate_boundary_check.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    execution_dir = paths.data_dir / "equity_owner_readiness_recovery_execution" / "daily" / as_of_date
    gate_dir = paths.data_dir / "equity_owner_readiness_gate" / "daily" / as_of_date
    sources = {key: execution_dir / name for key, name in RECOVERY_EXECUTION_KEYS.items()}
    sources.update({key: gate_dir / name for key, name in GATE_KEYS.items()})
    sources["recovery_execution_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_recovery_execution_audit.json"
    sources["owner_readiness_gate_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json"
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    missing = sorted(key for key, path in sources.items() if not path.exists())
    execution_audit = load_json(sources["recovery_execution_audit"])
    gate_audit = load_json(sources["owner_readiness_gate_audit"])
    config = load_json(sources["recovery_execution_config"])
    summary = load_json(sources["recovery_execution_summary"])
    readiness = load_json(sources["gate_reevaluation_readiness_decision"])
    plan = load_json(sources["controlled_reevaluation_plan"])
    blocked = load_json(sources["blocked_state_preservation_check"])
    threshold = load_json(sources["threshold_preservation_check"])
    waiver = load_json(sources["waiver_preservation_check"])
    boundary = load_json(sources["recovery_execution_boundary_check"])
    blocking: list[str] = []
    if missing:
        blocking.append("required_inputs_missing")
    if execution_audit.get("overall_passed") is not True:
        blocking.append("recovery_execution_audit_not_passed")
    if execution_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("recovery_execution_recommended_next_version_mismatch")
    if gate_audit.get("overall_passed") is not True:
        blocking.append("owner_readiness_gate_audit_not_passed")
    if config.get("target_version") != BASELINE_VERSION:
        blocking.append("recovery_execution_version_mismatch")
    if summary.get("source_gate_decision") != "blocked":
        blocking.append("source_gate_decision_not_blocked")
    if summary.get("blocked_gate_decision_preserved") is not True:
        blocking.append("blocked_gate_decision_not_preserved")
    if readiness.get("ready_for_future_gate_reevaluation") is not False:
        blocking.append("source_readiness_not_not_ready")
    if readiness.get("gate_reevaluation_executed") is not False or summary.get("gate_reevaluation_executed") is not False:
        blocking.append("source_gate_reevaluation_already_executed")
    if plan.get("rerun_owner_readiness_gate") is not False:
        blocking.append("source_plan_attempts_gate_rerun")
    if blocked.get("overall_passed") is not True:
        blocking.append("blocked_state_not_preserved")
    if threshold.get("threshold_lowered") is not False:
        blocking.append("threshold_lowered")
    if waiver.get("auto_waiver_allowed") is not False or waiver.get("manual_waiver_approval_recorded") is not False:
        blocking.append("waiver_recorded")
    if boundary.get("overall_passed") is not True:
        blocking.append("recovery_execution_boundary_not_clean")
    return {
        "availability_id": "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "missing_required_inputs": missing,
        "recovery_execution_audit_passed": execution_audit.get("overall_passed") is True,
        "owner_readiness_gate_audit_passed": gate_audit.get("overall_passed") is True,
        "source_gate_decision": summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": summary.get("blocked_gate_decision_preserved") is True,
        "source_ready_for_future_gate_reevaluation": readiness.get("ready_for_future_gate_reevaluation"),
        "source_gate_reevaluation_executed": readiness.get("gate_reevaluation_executed"),
        "threshold_lowered": threshold.get("threshold_lowered"),
        "auto_waiver_allowed": waiver.get("auto_waiver_allowed"),
        "manual_waiver_approval_recorded": waiver.get("manual_waiver_approval_recorded"),
        "preferred_source": "v0.8.16_owner_readiness_recovery_execution_artifacts",
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }

