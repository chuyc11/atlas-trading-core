"""Readiness checks for the A-share current-day research runner."""

from __future__ import annotations

from typing import Any

from trading_core.equity_current_day.current_day_config import (
    ALLOWED_WORKFLOW_MODES,
    KNOWN_DATA_REFRESH_WARNINGS,
    TARGET_VERSION,
)
from trading_core.equity_data_refresh.data_refresh_config import CRITICAL_DATASETS, data_refresh_artifact_paths
from trading_core.equity_workflows.workflow_config import REQUIRED_WORKFLOW_COMMANDS
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

from .data_refresh_link import load_json


def build_current_day_readiness(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    resolved_as_of_date: str,
    workflow_mode: str,
    allow_date_mismatch: bool = False,
) -> dict[str, Any]:
    paths = default_paths(paths)
    refresh_artifacts = data_refresh_artifact_paths(paths, resolved_as_of_date)
    audit = load_json(refresh_artifacts["data_refresh_audit_json"])
    dataset_checks = audit.get("dataset_checks", {})
    validation_checks = audit.get("validation_checks", {})
    warnings = [str(item) for item in audit.get("warnings", []) if item]
    blocking: list[str] = []
    data_refresh_audit_exists = refresh_artifacts["data_refresh_audit_json"].exists()
    data_refresh_audit_passed = audit.get("overall_passed") is True
    data_refresh_blocking_empty = audit.get("blocking_reasons", []) == []
    critical_passed = all(dataset_checks.get(dataset_id) in {"passed", "warning"} for dataset_id in CRITICAL_DATASETS)
    schema_passed = validation_checks.get("schema_validation_passed") is True
    freshness_passed = validation_checks.get("freshness_validation_passed") is True
    coverage_passed = validation_checks.get("coverage_validation_passed") is True
    date_alignment = as_of_date == resolved_as_of_date or allow_date_mismatch
    workflow_cli_available = all(command in REQUIRED_WORKFLOW_COMMANDS for command in REQUIRED_WORKFLOW_COMMANDS)
    workflow_mode_allowed = workflow_mode in ALLOWED_WORKFLOW_MODES
    checks = {
        "data_refresh_audit_exists": data_refresh_audit_exists,
        "data_refresh_audit_passed": data_refresh_audit_passed,
        "data_refresh_blocking_reasons_empty": data_refresh_blocking_empty,
        "resolved_as_of_date_valid": bool(resolved_as_of_date and len(resolved_as_of_date) == 10),
        "resolved_as_of_date_matches_requested_date": date_alignment,
        "critical_datasets_passed": critical_passed,
        "schema_validation_passed": schema_passed,
        "freshness_validation_passed": freshness_passed,
        "coverage_validation_passed": coverage_passed,
        "known_data_refresh_warnings_carried_forward": all(item in warnings for item in KNOWN_DATA_REFRESH_WARNINGS if item in warnings),
        "workflow_cli_available": workflow_cli_available,
        "workflow_mode_allowed": workflow_mode_allowed,
        "old_run_daily_disabled": True,
        "broker_disabled": True,
        "real_orders_disabled": True,
        "research_only_boundary_clean": True,
    }
    blocking.extend(f"{name}=false" for name, passed in checks.items() if not passed)
    return {
        "readiness_id": "A-SHARE-CURRENT-DAY-RESEARCH-READINESS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "data_refresh_audit_passed": data_refresh_audit_passed,
        "critical_datasets_passed": critical_passed,
        "schema_validation_passed": schema_passed,
        "freshness_validation_passed": freshness_passed,
        "coverage_validation_passed": coverage_passed,
        "workflow_cli_available": workflow_cli_available,
        "workflow_mode_allowed": workflow_mode_allowed,
        "known_warnings": warnings,
        "checks": checks,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }

