"""Input availability checks for the daily ops center."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import current_day_artifact_paths
from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.equity_ops_center.ops_config import BASELINE_REMEDIATION_VERSION, MODULE_IDS, TARGET_VERSION
from trading_core.equity_owner_dashboard.dashboard_config import dashboard_artifact_paths
from trading_core.equity_owner_monitoring.monitoring_config import monitoring_artifact_paths
from trading_core.equity_owner_remediation.remediation_config import remediation_artifact_paths
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


def ops_input_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    refresh = data_refresh_artifact_paths(paths, as_of_date)
    current = current_day_artifact_paths(paths, as_of_date)
    dashboard = dashboard_artifact_paths(paths, as_of_date)
    monitoring = monitoring_artifact_paths(paths, as_of_date)
    remediation = remediation_artifact_paths(paths, as_of_date)
    return {
        "data_refresh_audit": refresh["data_refresh_audit_json"],
        "data_refresh_summary": refresh["data_refresh_summary"],
        "dataset_freshness_validation": refresh["dataset_freshness_validation"],
        "dataset_coverage_summary": refresh["dataset_coverage_summary"],
        "data_refresh_boundary_check": refresh["data_refresh_boundary_check"],
        "current_day_run_audit": current["current_day_audit_json"],
        "current_day_run_manifest": current["current_day_run_manifest"],
        "current_day_readiness": current["current_day_readiness"],
        "current_day_warning_summary": current["current_day_warning_summary"],
        "current_day_boundary_check": current["current_day_boundary_check"],
        "owner_dashboard_audit": dashboard["dashboard_audit_json"],
        "executive_status_card": dashboard["executive_status_card"],
        "data_freshness_card": dashboard["data_freshness_card"],
        "workflow_status_card": dashboard["workflow_status_card"],
        "research_output_card": dashboard["research_output_card"],
        "warning_and_blocker_card": dashboard["warning_and_blocker_card"],
        "artifact_navigation_index": dashboard["artifact_navigation_index"],
        "dashboard_boundary_check": dashboard["dashboard_boundary_check"],
        "dashboard_manifest": dashboard["dashboard_manifest"],
        "owner_monitoring_audit": monitoring["monitoring_audit_json"],
        "monitoring_status_card": monitoring["monitoring_status_card"],
        "owner_alert_summary_card": monitoring["owner_alert_summary_card"],
        "run_history_summary_card": monitoring["run_history_summary_card"],
        "monitoring_boundary_check": monitoring["monitoring_boundary_check"],
        "monitoring_manifest": monitoring["monitoring_manifest"],
        "owner_remediation_audit": remediation["remediation_audit_json"],
        "remediation_config": remediation["remediation_config"],
        "remediation_input_availability": remediation["remediation_input_availability"],
        "issue_catalog": remediation["issue_catalog"],
        "safe_owner_action_checklist": remediation["safe_owner_action_checklist"],
        "manual_verification_checklist": remediation["manual_verification_checklist"],
        "non_actionable_issue_list": remediation["non_actionable_issue_list"],
        "dry_run_remediation_plan": remediation["dry_run_remediation_plan"],
        "remediation_priority_summary": remediation["remediation_priority_summary"],
        "remediation_source_trace": remediation["remediation_source_trace"],
        "remediation_boundary_check": remediation["remediation_boundary_check"],
        "remediation_manifest": remediation["remediation_manifest"],
        "remediation_summary": remediation["remediation_summary"],
    }


def build_ops_input_availability(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    input_paths = ops_input_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in input_paths.items()}
    modules = _module_records(paths, input_paths, payloads)
    missing = [key for key, path in input_paths.items() if not path.exists()]
    audit_checks = {f"{module['module_id']}_audit_passed": module["audit_passed"] for module in modules}
    blocking = [f"{item}_missing" for item in missing]
    blocking.extend(f"{key}=false" for key, passed in audit_checks.items() if not passed)
    remediation_audit = payloads.get("owner_remediation_audit", {})
    if remediation_audit.get("target_version") != BASELINE_REMEDIATION_VERSION:
        blocking.append("owner_remediation_target_version_unexpected")
    if remediation_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("owner_remediation_recommended_next_version_unexpected")
    return {
        "availability_id": "A-SHARE-DAILY-OPS-CENTER-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "required_modules": list(MODULE_IDS),
        "modules": modules,
        "input_artifacts": [_artifact_record(paths, artifact_id, path) for artifact_id, path in input_paths.items()],
        "input_audit_checks": audit_checks,
        "required_modules_available": all(module["available"] for module in modules),
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
    }


def _module_records(paths: ProjectPaths, input_paths: dict[str, Path], payloads: dict[str, Any]) -> list[dict[str, Any]]:
    module_specs = {
        "data_refresh": ("data_refresh_audit", "data_refresh_boundary_check", "data_refresh_summary", "data_refresh_summary"),
        "current_day_research_run": ("current_day_run_audit", "current_day_boundary_check", "current_day_run_manifest", "current_day_warning_summary"),
        "owner_dashboard": ("owner_dashboard_audit", "dashboard_boundary_check", "dashboard_manifest", "artifact_navigation_index"),
        "owner_monitoring": ("owner_monitoring_audit", "monitoring_boundary_check", "monitoring_manifest", "monitoring_status_card"),
        "owner_remediation": ("owner_remediation_audit", "remediation_boundary_check", "remediation_manifest", "remediation_source_trace"),
    }
    records = []
    for module_id, (audit_key, boundary_key, manifest_key, summary_key) in module_specs.items():
        audit = payloads.get(audit_key, {})
        boundary = payloads.get(boundary_key, {})
        manifest = payloads.get(manifest_key, {})
        summary = payloads.get(summary_key, {})
        records.append(
            {
                "module_id": module_id,
                "required": True,
                "available": input_paths[audit_key].exists() and input_paths[boundary_key].exists() and input_paths[manifest_key].exists(),
                "audit_path": relative(input_paths[audit_key], paths.project_root),
                "audit_passed": audit.get("overall_passed") is True,
                "blocking_reasons": audit.get("blocking_reasons", []),
                "warning_count": len(audit.get("warnings", [])),
                "boundary_passed": boundary.get("overall_passed") is True or audit.get("boundary", {}).get("overall_passed") is True,
                "manifest_path": relative(input_paths[manifest_key], paths.project_root),
                "summary_path": relative(input_paths[summary_key], paths.project_root),
                "source_trace_path": _source_trace_path(paths, module_id, input_paths),
                "recommended_next_version": audit.get("recommended_next_version"),
                "target_version": audit.get("target_version") or manifest.get("target_version") or summary.get("target_version"),
            }
        )
    return records


def _source_trace_path(paths: ProjectPaths, module_id: str, input_paths: dict[str, Path]) -> str | None:
    keys = {
        "owner_dashboard": "artifact_navigation_index",
        "owner_monitoring": "monitoring_manifest",
        "owner_remediation": "remediation_source_trace",
    }
    key = keys.get(module_id)
    return relative(input_paths[key], paths.project_root) if key else None


def _artifact_record(paths: ProjectPaths, artifact_id: str, path: Path) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }
