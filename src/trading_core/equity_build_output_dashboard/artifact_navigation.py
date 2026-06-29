"""Artifact navigation for build-output dashboard."""

from __future__ import annotations

from pathlib import Path

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


NAVIGATION_TARGETS = {
    "repeatability_summary": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_summary.json",
    "repeatability_audit": "data/equity_data_quality/a_share_build_repeatability_audit.json",
    "gated_build_summary": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_summary.json",
    "build_artifact_index": "data/equity_current_day_builds/daily/{as_of_date}/build_artifact_index.json",
    "current_day_summary": "data/equity_current_day_runs/daily/{as_of_date}/current_day_summary.json",
    "candidate_summary": "data/equity_selection/daily/{as_of_date}/candidate_generation_summary.json",
    "portfolio_manifest": "data/equity_portfolios/daily/{as_of_date}/portfolio_manifest.json",
    "briefing": "data/equity_briefings/daily/{as_of_date}/daily_stock_selection_briefing.json",
    "tracking_summary": "data/equity_portfolio_tracking/daily/{as_of_date}/tracking_summary.json",
    "build_output_dashboard_report": "outputs/equity_build_output_dashboard/daily/{as_of_date}/A_SHARE_BUILD_OUTPUT_OWNER_DASHBOARD.md",
}


def build_artifact_navigation(*, paths: ProjectPaths | None, as_of_date: str) -> dict:
    paths = default_paths(paths)
    entries = []
    for artifact_id, template in NAVIGATION_TARGETS.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        entries.append({
            "artifact_id": artifact_id,
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "source_workflow_mode": "build_from_existing_data",
        })
    return {
        "navigation_id": "A-SHARE-BUILD-OUTPUT-ARTIFACT-NAVIGATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "artifact_count": len(entries),
        "entries": entries,
    }


def source_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    return {key: paths.project_root / template.format(as_of_date=as_of_date) for key, template in NAVIGATION_TARGETS.items()}

