"""Input availability checks for owner remediation."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import current_day_artifact_paths
from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.equity_owner_dashboard.dashboard_config import dashboard_artifact_paths
from trading_core.equity_owner_monitoring.monitoring_config import monitoring_artifact_paths
from trading_core.equity_owner_remediation.remediation_config import BASELINE_MONITORING_VERSION, TARGET_VERSION
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


def remediation_input_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    monitoring = monitoring_artifact_paths(paths, as_of_date)
    dashboard = dashboard_artifact_paths(paths, as_of_date)
    current = current_day_artifact_paths(paths, as_of_date)
    refresh = data_refresh_artifact_paths(paths, as_of_date)
    return {
        "owner_monitoring_audit": monitoring["monitoring_audit_json"],
        "monitoring_config": monitoring["monitoring_config"],
        "monitoring_input_availability": monitoring["monitoring_input_availability"],
        "run_history_snapshot": monitoring["run_history_snapshot"],
        "alert_rule_config": monitoring["alert_rule_config"],
        "alert_evaluation_result": monitoring["alert_evaluation_result"],
        "alert_event_log": monitoring["alert_event_log"],
        "warning_trend_snapshot": monitoring["warning_trend_snapshot"],
        "blocking_trend_snapshot": monitoring["blocking_trend_snapshot"],
        "provider_health_trend_snapshot": monitoring["provider_health_trend_snapshot"],
        "workflow_health_trend_snapshot": monitoring["workflow_health_trend_snapshot"],
        "dashboard_health_trend_snapshot": monitoring["dashboard_health_trend_snapshot"],
        "monitoring_status_card": monitoring["monitoring_status_card"],
        "owner_alert_summary_card": monitoring["owner_alert_summary_card"],
        "run_history_summary_card": monitoring["run_history_summary_card"],
        "monitoring_source_trace": monitoring["monitoring_source_trace"],
        "monitoring_boundary_check": monitoring["monitoring_boundary_check"],
        "monitoring_manifest": monitoring["monitoring_manifest"],
        "monitoring_summary": monitoring["monitoring_summary"],
        "warning_and_blocker_card": dashboard["warning_and_blocker_card"],
        "dashboard_boundary_check": dashboard["dashboard_boundary_check"],
        "dashboard_summary": dashboard["dashboard_summary"],
        "owner_dashboard_audit": dashboard["dashboard_audit_json"],
        "current_day_warning_summary": current["current_day_warning_summary"],
        "current_day_boundary_check": current["current_day_boundary_check"],
        "current_day_run_manifest": current["current_day_run_manifest"],
        "current_day_run_audit": current["current_day_audit_json"],
        "data_gap_report": refresh["data_gap_report"],
        "provider_fallback_report": refresh["provider_fallback_report"],
        "provider_health_check": refresh["provider_health_check"],
        "dataset_schema_validation": refresh["dataset_schema_validation"],
        "dataset_freshness_validation": refresh["dataset_freshness_validation"],
        "dataset_coverage_summary": refresh["dataset_coverage_summary"],
        "data_refresh_audit": refresh["data_refresh_audit_json"],
    }


def build_remediation_input_availability(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    input_paths = remediation_input_paths(paths, as_of_date)
    records = [
        artifact_record(paths, path, artifact_id=artifact_id, required=True, category="audit" if artifact_id.endswith("audit") else "source")
        for artifact_id, path in input_paths.items()
    ]
    missing = [row["artifact_id"] for row in records if row["required"] and not row["exists"]]
    monitoring_audit = load_json(input_paths["owner_monitoring_audit"])
    dashboard_audit = load_json(input_paths["owner_dashboard_audit"])
    current_audit = load_json(input_paths["current_day_run_audit"])
    refresh_audit = load_json(input_paths["data_refresh_audit"])
    audit_checks = {
        "owner_monitoring_audit_passed": monitoring_audit.get("overall_passed") is True,
        "owner_dashboard_audit_passed": dashboard_audit.get("overall_passed") is True,
        "current_day_run_audit_passed": current_audit.get("overall_passed") is True,
        "data_refresh_audit_passed": refresh_audit.get("overall_passed") is True,
    }
    blocking = [f"{item}_missing" for item in missing]
    blocking.extend(f"{key}=false" for key, passed in audit_checks.items() if not passed)
    if monitoring_audit.get("target_version") != BASELINE_MONITORING_VERSION:
        blocking.append("owner_monitoring_target_version_unexpected")
    if monitoring_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("owner_monitoring_recommended_next_version_unexpected")
    return {
        "availability_id": "A-SHARE-OWNER-REMEDIATION-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "input_artifacts": records,
        "input_audit_checks": audit_checks,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
    }
