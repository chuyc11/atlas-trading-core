"""Artifact navigation for owner daily pack."""

from __future__ import annotations

from pathlib import Path

from trading_core.equity_owner_daily_pack.daily_pack_config import FILES, REPORTS, TARGET_VERSION, artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_artifact_navigation(*, paths: ProjectPaths, as_of_date: str) -> dict:
    artifacts = artifact_paths(paths, as_of_date)
    entries = []
    for key in [*FILES, *REPORTS, "owner_daily_pack_audit_json", "owner_daily_pack_audit_report"]:
        path = artifacts[key]
        entries.append({
            "artifact_id": key,
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "artifact_type": "report" if key in REPORTS or key.endswith("_report") else "json",
        })
    return {
        "navigation_id": "A-SHARE-OWNER-DAILY-PACK-ARTIFACT-NAVIGATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "entries": entries,
    }


def source_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    base = paths.data_dir
    return {
        "build_output_ops_refresh_audit": base / "equity_data_quality" / "a_share_build_output_ops_refresh_audit.json",
        "build_output_ops_summary": base / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_ops_summary.json",
        "build_output_ops_source_trace": base / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_ops_source_trace.json",
        "build_output_ops_boundary_check": base / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_ops_boundary_check.json",
        "build_output_dashboard_audit": base / "equity_data_quality" / "a_share_build_output_owner_dashboard_audit.json",
        "build_output_dashboard_summary": base / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_dashboard_summary.json",
        "repeatability_audit": base / "equity_data_quality" / "a_share_build_repeatability_audit.json",
        "protected_path_modification_check": base / "equity_build_repeatability" / "daily" / as_of_date / "protected_path_modification_check.json",
        "gated_build_audit": base / "equity_data_quality" / "a_share_gated_build_from_existing_data_audit.json",
        "data_refresh_audit": base / "equity_data_quality" / "a_share_daily_data_refresh_audit.json",
    }

