"""Input availability for owner readiness recovery execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import BASELINE_VERSION, DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION
from trading_core.equity_owner_readiness_recovery_execution.io import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

RECOVERY_KEYS = {
    "recovery_plan_config": "recovery_plan_config.json",
    "recovery_input_availability": "recovery_input_availability.json",
    "recovery_source_resolution": "recovery_source_resolution.json",
    "recovery_date_alignment": "recovery_date_alignment.json",
    "readiness_gap_summary": "readiness_gap_summary.json",
    "score_driver_analysis": "score_driver_analysis.json",
    "quality_exception_root_cause_map": "quality_exception_root_cause_map.json",
    "quality_improvement_target_policy": "quality_improvement_target_policy.json",
    "recovery_task_backlog": "recovery_task_backlog.json",
    "developer_follow_up_recovery_plan": "developer_follow_up_recovery_plan.json",
    "owner_follow_up_recovery_plan": "owner_follow_up_recovery_plan.json",
    "non_actionable_recovery_items": "non_actionable_recovery_items.json",
    "recovery_score_impact_model": "recovery_score_impact_model.json",
    "recovery_milestone_plan": "recovery_milestone_plan.json",
    "quality_improvement_loop_definition": "quality_improvement_loop_definition.json",
    "recovery_verification_plan": "recovery_verification_plan.json",
    "gate_reevaluation_readiness_checklist": "gate_reevaluation_readiness_checklist.json",
    "blocked_state_preservation_check": "blocked_state_preservation_check.json",
    "recovery_risk_register": "recovery_risk_register.json",
    "recovery_source_trace": "recovery_source_trace.json",
    "recovery_boundary_check": "recovery_boundary_check.json",
    "recovery_manifest": "recovery_manifest.json",
    "recovery_summary": "recovery_summary.json",
}
QUALITY_EXCEPTION_KEYS = {
    "blocked_gate_intake": "blocked_gate_intake.json",
    "quality_exception_classification": "quality_exception_classification.json",
    "developer_follow_up_tracker": "developer_follow_up_tracker.json",
    "manual_waiver_decision_record": "manual_waiver_decision_record.json",
    "quality_exception_boundary_check": "quality_exception_boundary_check.json",
}
GATE_KEYS = {
    "owner_readiness_gate_decision": "owner_readiness_gate_decision.json",
    "owner_readiness_gate_boundary_check": "owner_readiness_gate_boundary_check.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    recovery_dir = paths.data_dir / "equity_owner_readiness_recovery" / "daily" / as_of_date
    exception_dir = paths.data_dir / "equity_owner_quality_exceptions" / "daily" / as_of_date
    gate_dir = paths.data_dir / "equity_owner_readiness_gate" / "daily" / as_of_date
    sources = {key: recovery_dir / name for key, name in RECOVERY_KEYS.items()}
    sources.update({key: exception_dir / name for key, name in QUALITY_EXCEPTION_KEYS.items()})
    sources.update({key: gate_dir / name for key, name in GATE_KEYS.items()})
    sources["recovery_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_recovery_audit.json"
    sources["quality_exception_workflow_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_quality_exception_workflow_audit.json"
    sources["owner_readiness_gate_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json"
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    missing = sorted(key for key, path in sources.items() if not path.exists())
    audit = load_json(sources["recovery_audit"])
    config = load_json(sources["recovery_plan_config"])
    summary = load_json(sources["recovery_summary"])
    blocked = load_json(sources["blocked_state_preservation_check"])
    boundary = load_json(sources["recovery_boundary_check"])
    blocking: list[str] = []
    if missing:
        blocking.append("required_inputs_missing")
    if audit.get("overall_passed") is not True:
        blocking.append("recovery_audit_not_passed")
    if audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("recovery_recommended_next_version_mismatch")
    if config.get("target_version") != BASELINE_VERSION:
        blocking.append("recovery_version_mismatch")
    if summary.get("source_gate_decision") != "blocked":
        blocking.append("source_gate_decision_not_blocked")
    if summary.get("blocked_gate_decision_preserved") is not True:
        blocking.append("blocked_gate_decision_not_preserved")
    if blocked.get("recovery_plan_changes_gate_decision") is not False:
        blocking.append("recovery_plan_changes_gate_decision")
    if blocked.get("threshold_lowered") is not False:
        blocking.append("threshold_lowered")
    if blocked.get("auto_waiver_allowed") is not False:
        blocking.append("auto_waiver_allowed")
    if boundary.get("overall_passed") is not True:
        blocking.append("recovery_boundary_not_clean")
    return {
        "availability_id": "A-SHARE-OWNER-READINESS-RECOVERY-EXECUTION-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "missing_required_inputs": missing,
        "recovery_audit_passed": audit.get("overall_passed") is True,
        "source_gate_decision": summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": summary.get("blocked_gate_decision_preserved") is True,
        "recovery_plan_changes_gate_decision": blocked.get("recovery_plan_changes_gate_decision"),
        "threshold_lowered": blocked.get("threshold_lowered"),
        "auto_waiver_allowed": blocked.get("auto_waiver_allowed"),
        "manual_waiver_approval_recorded": blocked.get("manual_waiver_approval_recorded"),
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }
