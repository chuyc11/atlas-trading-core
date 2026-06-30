"""Input availability checks for owner quality exception workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import BASELINE_VERSION, DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION
from trading_core.equity_owner_quality_exceptions.io import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

GATE_KEYS = {
    "owner_readiness_gate_config": "owner_readiness_gate_config.json",
    "owner_readiness_gate_input_availability": "owner_readiness_gate_input_availability.json",
    "owner_readiness_gate_source_resolution": "owner_readiness_gate_source_resolution.json",
    "owner_readiness_gate_date_alignment": "owner_readiness_gate_date_alignment.json",
    "owner_readiness_threshold_policy": "owner_readiness_threshold_policy.json",
    "daily_pack_quality_threshold_policy": "daily_pack_quality_threshold_policy.json",
    "owner_readiness_score_gate": "owner_readiness_score_gate.json",
    "daily_pack_completeness_gate": "daily_pack_completeness_gate.json",
    "warning_issue_quality_gate": "warning_issue_quality_gate.json",
    "safe_action_quality_gate": "safe_action_quality_gate.json",
    "protected_path_quality_gate": "protected_path_quality_gate.json",
    "boundary_quality_gate": "boundary_quality_gate.json",
    "source_trace_quality_gate": "source_trace_quality_gate.json",
    "trend_sufficiency_quality_gate": "trend_sufficiency_quality_gate.json",
    "markdown_report_quality_gate": "markdown_report_quality_gate.json",
    "artifact_navigation_quality_gate": "artifact_navigation_quality_gate.json",
    "owner_next_step_quality_gate": "owner_next_step_quality_gate.json",
    "owner_readiness_gate_decision": "owner_readiness_gate_decision.json",
    "quality_threshold_evaluation": "quality_threshold_evaluation.json",
    "quality_exception_candidate_list": "quality_exception_candidate_list.json",
    "owner_release_recommendation": "owner_release_recommendation.json",
    "owner_readiness_gate_source_trace": "owner_readiness_gate_source_trace.json",
    "owner_readiness_gate_boundary_check": "owner_readiness_gate_boundary_check.json",
    "owner_readiness_gate_manifest": "owner_readiness_gate_manifest.json",
    "owner_readiness_gate_summary": "owner_readiness_gate_summary.json",
}

HISTORY_KEYS = {
    "owner_readiness_score": "owner_readiness_score.json",
    "owner_readiness_trend_sufficiency": "owner_readiness_trend_sufficiency.json",
    "daily_pack_quality_baseline": "daily_pack_quality_baseline.json",
    "warning_issue_trend_baseline": "warning_issue_trend_baseline.json",
    "safe_action_trend_baseline": "safe_action_trend_baseline.json",
    "daily_pack_history_boundary_check": "daily_pack_history_boundary_check.json",
    "daily_pack_history_manifest": "daily_pack_history_manifest.json",
}

DAILY_PACK_KEYS = {
    "owner_operations_decision_pack": "owner_operations_decision_pack.json",
    "owner_next_step_checklist": "owner_next_step_checklist.json",
    "warning_issue_digest": "warning_issue_digest.json",
    "safe_action_digest": "safe_action_digest.json",
    "daily_pack_boundary_check": "daily_pack_boundary_check.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    gate_dir = paths.data_dir / "equity_owner_readiness_gate" / "daily" / as_of_date
    history_dir = paths.data_dir / "equity_owner_daily_pack_history" / "daily" / as_of_date
    pack_dir = paths.data_dir / "equity_owner_daily_pack" / "daily" / as_of_date
    sources = {key: gate_dir / name for key, name in GATE_KEYS.items()}
    sources.update({key: history_dir / name for key, name in HISTORY_KEYS.items()})
    sources.update({key: pack_dir / name for key, name in DAILY_PACK_KEYS.items()})
    sources["owner_readiness_gate_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json"
    sources["owner_daily_pack_history_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_daily_pack_history_audit.json"
    sources["owner_daily_pack_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_daily_pack_audit.json"
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    missing = sorted(key for key, path in sources.items() if not path.exists())
    gate_audit = load_json(sources["owner_readiness_gate_audit"])
    decision = load_json(sources["owner_readiness_gate_decision"])
    candidates = load_json(sources["quality_exception_candidate_list"])
    boundary = load_json(sources["owner_readiness_gate_boundary_check"])
    blocking: list[str] = []
    if missing:
        blocking.append("required_inputs_missing")
    if gate_audit.get("overall_passed") is not True:
        blocking.append("owner_readiness_gate_audit_not_passed")
    if gate_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("owner_readiness_gate_recommended_next_version_mismatch")
    if decision.get("target_version") != BASELINE_VERSION:
        blocking.append("owner_readiness_gate_decision_version_mismatch")
    if decision.get("decision") == "blocked" and gate_audit.get("gate_checks", {}).get("blocked_state_represented_correctly") is not True:
        blocking.append("blocked_state_not_represented_correctly")
    if candidates.get("auto_waiver_allowed") is not False:
        blocking.append("automatic_waiver_not_disabled")
    if boundary.get("overall_passed") is not True:
        blocking.append("owner_readiness_gate_boundary_not_clean")
    return {
        "availability_id": "A-SHARE-OWNER-QUALITY-EXCEPTION-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "missing_required_inputs": missing,
        "owner_readiness_gate_audit_passed": gate_audit.get("overall_passed") is True,
        "source_gate_decision": decision.get("decision"),
        "blocked_state_represented_correctly": gate_audit.get("gate_checks", {}).get("blocked_state_represented_correctly") is True,
        "no_automatic_waiver": candidates.get("auto_waiver_allowed") is False,
        "boundary_clean": boundary.get("overall_passed") is True,
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }
