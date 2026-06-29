"""Input availability checks for owner monitoring."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import current_day_artifact_paths
from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.equity_owner_dashboard.dashboard_config import dashboard_artifact_paths
from trading_core.equity_owner_monitoring.monitoring_config import TARGET_VERSION, monitoring_history_dir
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def artifact_record(paths: ProjectPaths, path: Path, *, artifact_id: str, required: bool, category: str) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "category": category,
        "required": required,
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }


def monitoring_input_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    dashboard = dashboard_artifact_paths(paths, as_of_date)
    current = current_day_artifact_paths(paths, as_of_date)
    refresh = data_refresh_artifact_paths(paths, as_of_date)
    return {
        "owner_dashboard_audit": dashboard["dashboard_audit_json"],
        "current_day_run_audit": current["current_day_audit_json"],
        "data_refresh_audit": refresh["data_refresh_audit_json"],
        "dashboard_config": dashboard["dashboard_config"],
        "dashboard_input_availability": dashboard["dashboard_input_availability"],
        "executive_status_card": dashboard["executive_status_card"],
        "data_freshness_card": dashboard["data_freshness_card"],
        "provider_health_card": dashboard["provider_health_card"],
        "workflow_status_card": dashboard["workflow_status_card"],
        "research_output_card": dashboard["research_output_card"],
        "warning_and_blocker_card": dashboard["warning_and_blocker_card"],
        "artifact_navigation_index": dashboard["artifact_navigation_index"],
        "dashboard_source_trace": dashboard["dashboard_source_trace"],
        "dashboard_boundary_check": dashboard["dashboard_boundary_check"],
        "dashboard_manifest": dashboard["dashboard_manifest"],
        "dashboard_summary": dashboard["dashboard_summary"],
        "owner_dashboard_report": dashboard["owner_dashboard_report"],
        "owner_dashboard_compact_report": dashboard["owner_dashboard_compact_report"],
        "owner_warning_blocker_report": dashboard["owner_warning_blocker_report"],
        "current_day_run_manifest": current["current_day_run_manifest"],
        "current_day_warning_summary": current["current_day_warning_summary"],
        "current_day_boundary_check": current["current_day_boundary_check"],
        "provider_health_check": refresh["provider_health_check"],
        "dataset_freshness_validation": refresh["dataset_freshness_validation"],
        "dataset_coverage_summary": refresh["dataset_coverage_summary"],
        "data_gap_report": refresh["data_gap_report"],
    }


def build_monitoring_input_availability(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    required = set(monitoring_input_paths(paths, as_of_date))
    records = []
    for artifact_id, path in monitoring_input_paths(paths, as_of_date).items():
        category = "audit" if artifact_id.endswith("audit") else "source"
        records.append(artifact_record(paths, path, artifact_id=artifact_id, required=True, category=category))
    history_dir = monitoring_history_dir(paths)
    records.append(
        {
            "artifact_id": "run_history_directory",
            "category": "history",
            "required": False,
            "path": relative(history_dir, paths.project_root),
            "exists": history_dir.exists(),
            "sha256": None,
        }
    )
    missing_required = [row["artifact_id"] for row in records if row["artifact_id"] in required and not row["exists"]]
    dashboard_audit = load_json(monitoring_input_paths(paths, as_of_date)["owner_dashboard_audit"])
    current_audit = load_json(monitoring_input_paths(paths, as_of_date)["current_day_run_audit"])
    refresh_audit = load_json(monitoring_input_paths(paths, as_of_date)["data_refresh_audit"])
    audit_checks = {
        "owner_dashboard_audit_passed": dashboard_audit.get("overall_passed") is True,
        "current_day_run_audit_passed": current_audit.get("overall_passed") is True,
        "data_refresh_audit_passed": refresh_audit.get("overall_passed") is True,
    }
    blocking = [f"{item}_missing" for item in missing_required]
    blocking.extend(f"{key}=false" for key, passed in audit_checks.items() if not passed)
    warnings = []
    if not history_dir.exists():
        warnings.append("run_history_directory_missing_will_create")
    if dashboard_audit.get("recommended_next_version") != "v0.8.3-a-share-owner-alerting-and-run-history-monitoring":
        warnings.append("owner_dashboard_recommended_next_version_unexpected")
    return {
        "availability_id": "A-SHARE-OWNER-MONITORING-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "input_artifacts": records,
        "input_audit_checks": audit_checks,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }
