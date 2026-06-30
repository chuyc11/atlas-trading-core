"""Artifact navigation for build-output ops refresh."""

from __future__ import annotations

from pathlib import Path

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import FILES, REPORTS, TARGET_VERSION, artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_artifact_navigation(*, paths: ProjectPaths, as_of_date: str) -> dict:
    artifacts = artifact_paths(paths, as_of_date)
    entries = []
    for key in [*FILES, *REPORTS, "build_output_ops_audit_json", "build_output_ops_audit_report"]:
        path = artifacts[key]
        entries.append({
            "artifact_id": key,
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "artifact_type": "report" if key in REPORTS or key.endswith("_report") else "json",
        })
    return {
        "navigation_id": "A-SHARE-BUILD-OUTPUT-OPS-ARTIFACT-NAVIGATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "entries": entries,
    }


def source_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    base = paths.data_dir
    return {
        "build_output_dashboard_audit": base / "equity_data_quality" / "a_share_build_output_owner_dashboard_audit.json",
        "build_output_dashboard_summary": base / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_dashboard_summary.json",
        "build_output_dashboard_source_trace": base / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_dashboard_source_trace.json",
        "repeatability_audit": base / "equity_data_quality" / "a_share_build_repeatability_audit.json",
        "repeatability_summary": base / "equity_build_repeatability" / "daily" / as_of_date / "repeatability_summary.json",
        "protected_path_modification_check": base / "equity_build_repeatability" / "daily" / as_of_date / "protected_path_modification_check.json",
        "gated_build_audit": base / "equity_data_quality" / "a_share_gated_build_from_existing_data_audit.json",
        "gated_build_summary": base / "equity_current_day_builds" / "daily" / as_of_date / "gated_build_summary.json",
        "monitoring_audit": base / "equity_data_quality" / "a_share_owner_monitoring_audit.json",
        "remediation_audit": base / "equity_data_quality" / "a_share_owner_remediation_audit.json",
        "ops_center_audit": base / "equity_data_quality" / "a_share_daily_ops_center_audit.json",
        "ops_health_score_card": base / "equity_ops_center" / "daily" / as_of_date / "ops_health_score_card.json",
        "ops_action_summary": base / "equity_ops_center" / "daily" / as_of_date / "ops_action_summary.json",
    }

