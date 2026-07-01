"""Input availability for owner recovery evidence collection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import BASELINE_VERSION, DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.equity_owner_recovery_evidence.io import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

CONTROLLED_KEYS = {
    "controlled_reevaluation_config": "controlled_reevaluation_config.json",
    "controlled_reevaluation_input_availability": "controlled_reevaluation_input_availability.json",
    "controlled_reevaluation_source_resolution": "controlled_reevaluation_source_resolution.json",
    "controlled_reevaluation_date_alignment": "controlled_reevaluation_date_alignment.json",
    "reevaluation_readiness_guard": "reevaluation_readiness_guard.json",
    "reevaluation_prerequisite_validation": "reevaluation_prerequisite_validation.json",
    "reevaluation_execution_plan": "reevaluation_execution_plan.json",
    "reevaluation_skip_decision": "reevaluation_skip_decision.json",
    "not_ready_reason_summary": "not_ready_reason_summary.json",
    "source_gate_preservation_check": "source_gate_preservation_check.json",
    "threshold_preservation_check": "threshold_preservation_check.json",
    "waiver_preservation_check": "waiver_preservation_check.json",
    "evidence_sufficiency_check": "evidence_sufficiency_check.json",
    "controlled_reevaluation_decision": "controlled_reevaluation_decision.json",
    "controlled_reevaluation_source_trace": "controlled_reevaluation_source_trace.json",
    "controlled_reevaluation_boundary_check": "controlled_reevaluation_boundary_check.json",
    "controlled_reevaluation_manifest": "controlled_reevaluation_manifest.json",
    "controlled_reevaluation_summary": "controlled_reevaluation_summary.json",
}
RECOVERY_EXECUTION_KEYS = {
    "recovery_task_evidence_registry": "recovery_task_evidence_registry.json",
    "recovery_task_status_tracker": "recovery_task_status_tracker.json",
    "developer_follow_up_evidence_tracker": "developer_follow_up_evidence_tracker.json",
    "owner_follow_up_evidence_tracker": "owner_follow_up_evidence_tracker.json",
    "recovery_task_completion_evaluation": "recovery_task_completion_evaluation.json",
    "readiness_improvement_evidence_summary": "readiness_improvement_evidence_summary.json",
    "gate_reevaluation_readiness_decision": "gate_reevaluation_readiness_decision.json",
}
RECOVERY_PLAN_KEYS = {
    "recovery_task_backlog": "recovery_task_backlog.json",
    "developer_follow_up_recovery_plan": "developer_follow_up_recovery_plan.json",
    "owner_follow_up_recovery_plan": "owner_follow_up_recovery_plan.json",
    "recovery_verification_plan": "recovery_verification_plan.json",
    "gate_reevaluation_readiness_checklist": "gate_reevaluation_readiness_checklist.json",
}
GATE_KEYS = {
    "owner_readiness_gate_decision": "owner_readiness_gate_decision.json",
    "owner_readiness_score_gate": "owner_readiness_score_gate.json",
    "quality_threshold_evaluation": "quality_threshold_evaluation.json",
}
QUALITY_EXCEPTION_KEYS = {
    "blocked_gate_intake": "blocked_gate_intake.json",
    "quality_exception_classification": "quality_exception_classification.json",
    "developer_follow_up_tracker": "developer_follow_up_tracker.json",
    "owner_readiness_gap_analysis": "owner_readiness_gap_analysis.json",
    "quality_exception_source_trace": "quality_exception_source_trace.json",
    "quality_exception_manifest": "quality_exception_manifest.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    controlled_dir = paths.data_dir / "equity_owner_controlled_gate_reevaluation" / "daily" / as_of_date
    execution_dir = paths.data_dir / "equity_owner_readiness_recovery_execution" / "daily" / as_of_date
    recovery_dir = paths.data_dir / "equity_owner_readiness_recovery" / "daily" / as_of_date
    gate_dir = paths.data_dir / "equity_owner_readiness_gate" / "daily" / as_of_date
    quality_dir = paths.data_dir / "equity_owner_quality_exceptions" / "daily" / as_of_date
    sources = {key: controlled_dir / name for key, name in CONTROLLED_KEYS.items()}
    sources.update({key: execution_dir / name for key, name in RECOVERY_EXECUTION_KEYS.items()})
    sources.update({key: recovery_dir / name for key, name in RECOVERY_PLAN_KEYS.items()})
    sources.update({key: gate_dir / name for key, name in GATE_KEYS.items()})
    sources.update({key: quality_dir / name for key, name in QUALITY_EXCEPTION_KEYS.items()})
    sources["controlled_reevaluation_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_controlled_gate_reevaluation_audit.json"
    sources["recovery_execution_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_recovery_execution_audit.json"
    sources["recovery_plan_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_recovery_audit.json"
    sources["owner_readiness_gate_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json"
    sources["quality_exception_workflow_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_quality_exception_workflow_audit.json"
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    missing = sorted(key for key, path in sources.items() if not path.exists())
    controlled_audit = load_json(sources["controlled_reevaluation_audit"])
    controlled_config = load_json(sources["controlled_reevaluation_config"])
    controlled_summary = load_json(sources["controlled_reevaluation_summary"])
    skip = load_json(sources["reevaluation_skip_decision"])
    guard = load_json(sources["reevaluation_readiness_guard"])
    controlled_decision = load_json(sources["controlled_reevaluation_decision"])
    gate = load_json(sources["owner_readiness_gate_decision"])
    recovery_execution_audit = load_json(sources["recovery_execution_audit"])
    recovery_plan_audit = load_json(sources["recovery_plan_audit"])
    gate_audit = load_json(sources["owner_readiness_gate_audit"])
    blocking: list[str] = []
    if missing:
        blocking.append("required_inputs_missing")
    if controlled_audit.get("overall_passed") is not True:
        blocking.append("controlled_reevaluation_audit_not_passed")
    if controlled_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("controlled_reevaluation_recommended_next_version_mismatch")
    if controlled_config.get("target_version") != BASELINE_VERSION:
        blocking.append("controlled_reevaluation_version_mismatch")
    if recovery_execution_audit.get("overall_passed") is not True:
        blocking.append("recovery_execution_audit_not_passed")
    if recovery_plan_audit.get("overall_passed") is not True:
        blocking.append("recovery_plan_audit_not_passed")
    if gate_audit.get("overall_passed") is not True:
        blocking.append("owner_readiness_gate_audit_not_passed")
    if controlled_summary.get("source_gate_decision") != "blocked" or gate.get("decision") != "blocked":
        blocking.append("source_gate_decision_not_blocked")
    if skip.get("reevaluation_skipped") is not True:
        blocking.append("reevaluation_not_skipped")
    if guard.get("reevaluation_allowed") is not False:
        blocking.append("reevaluation_allowed_by_source_guard")
    if controlled_decision.get("new_gate_score_generated") is not False or controlled_decision.get("new_gate_decision_generated") is not False:
        blocking.append("controlled_reevaluation_generated_gate_output")
    return {
        "availability_id": "A-SHARE-OWNER-RECOVERY-EVIDENCE-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "missing_required_inputs": missing,
        "controlled_reevaluation_audit_passed": controlled_audit.get("overall_passed") is True,
        "recovery_execution_audit_passed": recovery_execution_audit.get("overall_passed") is True,
        "recovery_plan_audit_passed": recovery_plan_audit.get("overall_passed") is True,
        "owner_readiness_gate_audit_passed": gate_audit.get("overall_passed") is True,
        "source_gate_decision": controlled_summary.get("source_gate_decision"),
        "reevaluation_skipped": skip.get("reevaluation_skipped"),
        "new_gate_score_generated": controlled_decision.get("new_gate_score_generated"),
        "new_gate_decision_generated": controlled_decision.get("new_gate_decision_generated"),
        "source_readiness_score": controlled_summary.get("actual_owner_readiness_score"),
        "minimum_owner_readiness_score": controlled_summary.get("minimum_owner_readiness_score"),
        "preferred_source": "v0.8.17_controlled_gate_reevaluation_artifacts",
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }

