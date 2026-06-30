"""Input availability for owner readiness recovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_readiness_recovery.io import load_json
from trading_core.equity_owner_readiness_recovery.recovery_config import BASELINE_VERSION, DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

EXCEPTION_KEYS = {
    "quality_exception_workflow_config": "quality_exception_workflow_config.json",
    "quality_exception_input_availability": "quality_exception_input_availability.json",
    "quality_exception_source_resolution": "quality_exception_source_resolution.json",
    "quality_exception_date_alignment": "quality_exception_date_alignment.json",
    "blocked_gate_intake": "blocked_gate_intake.json",
    "quality_exception_registry": "quality_exception_registry.json",
    "quality_exception_classification": "quality_exception_classification.json",
    "owner_readiness_gap_analysis": "owner_readiness_gap_analysis.json",
    "threshold_failure_explanation": "threshold_failure_explanation.json",
    "waiver_candidate_evaluation": "waiver_candidate_evaluation.json",
    "manual_waiver_policy": "manual_waiver_policy.json",
    "manual_waiver_decision_record": "manual_waiver_decision_record.json",
    "escalation_workflow": "escalation_workflow.json",
    "developer_follow_up_tracker": "developer_follow_up_tracker.json",
    "owner_follow_up_checklist": "owner_follow_up_checklist.json",
    "blocked_daily_pack_owner_notice": "blocked_daily_pack_owner_notice.json",
    "exception_severity_matrix": "exception_severity_matrix.json",
    "exception_routing_matrix": "exception_routing_matrix.json",
    "exception_sla_policy": "exception_sla_policy.json",
    "exception_audit_trail": "exception_audit_trail.json",
    "quality_exception_source_trace": "quality_exception_source_trace.json",
    "quality_exception_boundary_check": "quality_exception_boundary_check.json",
    "quality_exception_manifest": "quality_exception_manifest.json",
    "quality_exception_summary": "quality_exception_summary.json",
}
GATE_KEYS = {
    "owner_readiness_gate_decision": "owner_readiness_gate_decision.json",
    "quality_threshold_evaluation": "quality_threshold_evaluation.json",
    "quality_exception_candidate_list": "quality_exception_candidate_list.json",
    "owner_release_recommendation": "owner_release_recommendation.json",
    "owner_readiness_gate_boundary_check": "owner_readiness_gate_boundary_check.json",
}
HISTORY_KEYS = {
    "owner_readiness_score": "owner_readiness_score.json",
    "owner_readiness_trend_sufficiency": "owner_readiness_trend_sufficiency.json",
    "daily_pack_quality_baseline": "daily_pack_quality_baseline.json",
    "daily_pack_history_boundary_check": "daily_pack_history_boundary_check.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    exception_dir = paths.data_dir / "equity_owner_quality_exceptions" / "daily" / as_of_date
    gate_dir = paths.data_dir / "equity_owner_readiness_gate" / "daily" / as_of_date
    history_dir = paths.data_dir / "equity_owner_daily_pack_history" / "daily" / as_of_date
    sources = {key: exception_dir / name for key, name in EXCEPTION_KEYS.items()}
    sources.update({key: gate_dir / name for key, name in GATE_KEYS.items()})
    sources.update({key: history_dir / name for key, name in HISTORY_KEYS.items()})
    sources["quality_exception_workflow_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_quality_exception_workflow_audit.json"
    sources["owner_readiness_gate_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json"
    sources["owner_daily_pack_history_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_daily_pack_history_audit.json"
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    missing = sorted(key for key, path in sources.items() if not path.exists())
    audit = load_json(sources["quality_exception_workflow_audit"])
    intake = load_json(sources["blocked_gate_intake"])
    waiver = load_json(sources["manual_waiver_decision_record"])
    blocking: list[str] = []
    if missing:
        blocking.append("required_inputs_missing")
    if audit.get("overall_passed") is not True:
        blocking.append("quality_exception_workflow_audit_not_passed")
    if audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("quality_exception_recommended_next_version_mismatch")
    if load_json(sources["quality_exception_workflow_config"]).get("target_version") != BASELINE_VERSION:
        blocking.append("quality_exception_workflow_version_mismatch")
    if intake.get("source_gate_decision") != "blocked":
        blocking.append("source_gate_decision_not_blocked")
    if intake.get("blocked_state_preserved") is not True:
        blocking.append("blocked_gate_decision_not_preserved")
    if intake.get("owner_operationally_acceptable") is not False:
        blocking.append("owner_operationally_acceptable_not_false")
    if waiver.get("auto_waiver_allowed") is not False:
        blocking.append("automatic_waiver_not_disabled")
    if waiver.get("waiver_changes_gate_decision") is not False:
        blocking.append("waiver_changes_gate_decision")
    return {
        "availability_id": "A-SHARE-OWNER-READINESS-RECOVERY-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "missing_required_inputs": missing,
        "quality_exception_workflow_audit_passed": audit.get("overall_passed") is True,
        "source_gate_decision": intake.get("source_gate_decision"),
        "blocked_gate_decision_preserved": intake.get("blocked_state_preserved") is True,
        "owner_operationally_acceptable": intake.get("owner_operationally_acceptable"),
        "auto_waiver_allowed": waiver.get("auto_waiver_allowed"),
        "waiver_changes_gate_decision": waiver.get("waiver_changes_gate_decision"),
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }
