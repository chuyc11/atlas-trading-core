"""Input availability checks for v0.8.8 repeatability."""

from __future__ import annotations

import json
from pathlib import Path

from trading_core.equity_build_repeatability.repeatability_config import (
    BASELINE_VERSION,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


REQUIRED_GATED_BUILD_ARTIFACTS = {
    "gated_build_config": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_config.json",
    "preflight_gate": "data/equity_current_day_builds/daily/{as_of_date}/preflight_gate.json",
    "gated_build_execution_record": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_execution_record.json",
    "build_from_existing_data_workflow_result": "data/equity_current_day_builds/daily/{as_of_date}/build_from_existing_data_workflow_result.json",
    "build_from_existing_data_audit_link": "data/equity_current_day_builds/daily/{as_of_date}/build_from_existing_data_audit_link.json",
    "build_artifact_index": "data/equity_current_day_builds/daily/{as_of_date}/build_artifact_index.json",
    "validate_vs_build_comparison": "data/equity_current_day_builds/daily/{as_of_date}/validate_vs_build_comparison.json",
    "artifact_drift_summary": "data/equity_current_day_builds/daily/{as_of_date}/artifact_drift_summary.json",
    "gated_build_warning_summary": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_warning_summary.json",
    "gated_build_source_trace": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_source_trace.json",
    "gated_build_boundary_check": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_boundary_check.json",
    "gated_build_manifest": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_manifest.json",
    "gated_build_summary": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_summary.json",
    "gated_build_audit": "data/equity_data_quality/a_share_gated_build_from_existing_data_audit.json",
}

UPSTREAM_ARTIFACTS = {
    "ops_history_manifest": "data/equity_ops_history/daily/{as_of_date}/ops_history_manifest.json",
    "ops_history_boundary_check": "data/equity_ops_history/daily/{as_of_date}/ops_history_boundary_check.json",
    "ops_history_audit": "data/equity_data_quality/a_share_ops_history_baseline_audit.json",
    "ops_health_score_card": "data/equity_ops_center/daily/{as_of_date}/ops_health_score_card.json",
    "ops_issue_summary": "data/equity_ops_center/daily/{as_of_date}/ops_issue_summary.json",
    "ops_boundary_check": "data/equity_ops_center/daily/{as_of_date}/ops_boundary_check.json",
    "ops_center_audit": "data/equity_data_quality/a_share_daily_ops_center_audit.json",
    "dataset_schema_validation": "data/equity_data_refresh/daily/{as_of_date}/dataset_schema_validation.json",
    "dataset_freshness_validation": "data/equity_data_refresh/daily/{as_of_date}/dataset_freshness_validation.json",
    "dataset_coverage_summary": "data/equity_data_refresh/daily/{as_of_date}/dataset_coverage_summary.json",
    "data_refresh_audit": "data/equity_data_quality/a_share_daily_data_refresh_audit.json",
}


def build_repeatability_input_availability(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
) -> dict:
    paths = default_paths(paths)
    artifacts = {**REQUIRED_GATED_BUILD_ARTIFACTS, **UPSTREAM_ARTIFACTS}
    entries = []
    blocking: list[str] = []
    warnings: list[str] = []
    loaded: dict[str, dict] = {}

    for artifact_id, template in artifacts.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        exists = path.exists()
        payload = _load_json(path) if exists else {}
        if exists:
            loaded[artifact_id] = payload
        required = artifact_id in REQUIRED_GATED_BUILD_ARTIFACTS
        if required and not exists:
            blocking.append(f"missing_required_input:{artifact_id}")
        entries.append({
            "artifact_id": artifact_id,
            "path": relative(path, paths.project_root),
            "exists": exists,
            "required": required,
            "overall_passed": payload.get("overall_passed"),
            "target_version": payload.get("target_version"),
            "workflow_mode": payload.get("workflow_mode"),
        })

    audit = loaded.get("gated_build_audit", {})
    execution = loaded.get("gated_build_execution_record", {})
    workflow = loaded.get("build_from_existing_data_workflow_result", {})
    boundary = loaded.get("gated_build_boundary_check", {})

    if audit.get("overall_passed") is not True:
        blocking.append("gated_build_audit_not_passed")
    if audit.get("blocking_reasons", []) != []:
        blocking.append("gated_build_audit_has_blocking_reasons")
    if audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("gated_build_recommended_next_version_mismatch")
    if execution.get("workflow_mode") != "build_from_existing_data":
        blocking.append("gated_build_execution_mode_mismatch")
    if workflow.get("workflow_mode") != "build_from_existing_data":
        blocking.append("gated_build_workflow_mode_mismatch")
    if boundary.get("overall_passed") is not True:
        blocking.append("gated_build_boundary_not_passed")
    if boundary.get("blocking_reasons", []) != []:
        blocking.append("gated_build_boundary_has_blocking_reasons")
    if loaded.get("gated_build_manifest", {}).get("target_version") != BASELINE_VERSION:
        warnings.append("gated_build_manifest_target_version_not_baseline")

    return {
        "availability_id": "A-SHARE-BUILD-REPEATABILITY-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
        "entries": entries,
        "gated_build_audit_passed": audit.get("overall_passed") is True,
        "gated_build_workflow_mode": execution.get("workflow_mode") or workflow.get("workflow_mode"),
    }


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

