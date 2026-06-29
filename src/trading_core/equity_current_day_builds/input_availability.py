"""Input availability checks for v0.8.7 gated build."""

from __future__ import annotations

from pathlib import Path

from trading_core.equity_current_day_builds.gated_build_config import (
    DATA_REFRESH_VERSION,
    CURRENT_DAY_VERSION,
    OPS_CENTER_VERSION,
    BASELINE_VERSION,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_gated_build_input_availability(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
) -> dict:
    paths = default_paths(paths)

    ops_history_audit = (
        paths.data_dir / "equity_data_quality" / "a_share_ops_history_baseline_audit.json"
    )
    ops_center_audit = (
        paths.data_dir / "equity_data_quality" / "a_share_daily_ops_center_audit.json"
    )
    current_day_audit = (
        paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json"
    )
    data_refresh_audit = (
        paths.data_dir / "equity_data_quality" / "a_share_daily_data_refresh_audit.json"
    )

    # v0.8.6 artifacts
    ops_history_dir = paths.data_dir / "equity_ops_history" / "daily" / as_of_date
    ops_history_files = {
        "ops_trend_sufficiency": ops_history_dir / "ops_trend_sufficiency.json",
        "ops_health_score_baseline": ops_history_dir / "ops_health_score_baseline.json",
        "ops_boundary_history_snapshot": ops_history_dir / "ops_boundary_history_snapshot.json",
        "ops_history_boundary_check": ops_history_dir / "ops_history_boundary_check.json",
        "ops_history_manifest": ops_history_dir / "ops_history_manifest.json",
    }

    # v0.8.5 artifacts
    ops_center_dir = paths.data_dir / "equity_ops_center" / "daily" / as_of_date
    ops_center_files = {
        "ops_health_score_card": ops_center_dir / "ops_health_score_card.json",
        "ops_module_status_matrix": ops_center_dir / "ops_module_status_matrix.json",
        "ops_issue_summary": ops_center_dir / "ops_issue_summary.json",
        "ops_action_summary": ops_center_dir / "ops_action_summary.json",
        "ops_boundary_check": ops_center_dir / "ops_boundary_check.json",
        "ops_manifest": ops_center_dir / "ops_manifest.json",
    }

    # v0.8.1 artifacts
    current_day_dir = paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date
    current_day_files = {
        "current_day_run_config": current_day_dir / "current_day_run_config.json",
        "current_day_readiness": current_day_dir / "current_day_readiness.json",
        "current_day_workflow_execution": current_day_dir / "current_day_workflow_execution.json",
        "current_day_stage_manifest": current_day_dir / "current_day_stage_manifest.json",
        "current_day_artifact_index": current_day_dir / "current_day_artifact_index.json",
        "current_day_boundary_check": current_day_dir / "current_day_boundary_check.json",
        "current_day_run_manifest": current_day_dir / "current_day_run_manifest.json",
    }

    # v0.8.0 artifacts
    data_refresh_dir = paths.data_dir / "equity_data_refresh" / "daily" / as_of_date
    data_refresh_files = {
        "dataset_schema_validation": data_refresh_dir / "dataset_schema_validation.json",
        "dataset_freshness_validation": data_refresh_dir / "dataset_freshness_validation.json",
        "dataset_coverage_summary": data_refresh_dir / "dataset_coverage_summary.json",
        "data_refresh_boundary_check": data_refresh_dir / "data_refresh_boundary_check.json",
        "data_refresh_manifest": data_refresh_dir / "data_refresh_manifest.json",
    }

    audit_sources = {
        "ops_history_audit": ops_history_audit,
        "ops_center_audit": ops_center_audit,
        "current_day_audit": current_day_audit,
        "data_refresh_audit": data_refresh_audit,
    }

    all_inputs = {}
    all_inputs.update(audit_sources)
    all_inputs.update(ops_history_files)
    all_inputs.update(ops_center_files)
    all_inputs.update(current_day_files)
    all_inputs.update(data_refresh_files)

    availability = {}
    missing = []
    for key, path in all_inputs.items():
        exists = path.exists()
        availability[key] = {
            "path": relative(path, paths.project_root),
            "exists": exists,
        }
        if not exists:
            missing.append(key)

    blocking = list(missing)
    warnings = []

    overall_passed = not blocking

    return {
        "availability_id": "A-SHARE-GATED-BUILD-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "inputs": availability,
        "missing_inputs": sorted(missing),
        "overall_passed": overall_passed,
        "blocking_reasons": sorted(blocking),
        "warnings": sorted(warnings),
    }
