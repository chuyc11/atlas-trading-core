"""Workflow execution record for current-day research runs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from trading_core.equity_current_day.current_day_config import TARGET_VERSION
from trading_core.equity_data_quality.common import utc_now
from trading_core.equity_workflows.workflow_config import workflow_artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_blocked_workflow_execution(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    resolved_as_of_date: str,
    mode: str,
    workflow_mode: str,
    command: str,
    blocking_reasons: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = workflow_artifact_paths(paths, resolved_as_of_date)
    now = utc_now()
    return {
        "execution_id": "A-SHARE-CURRENT-DAY-WORKFLOW-EXECUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "mode": mode,
        "workflow_mode": workflow_mode,
        "command": command,
        "started_at": now,
        "finished_at": now,
        "duration_seconds": 0.0,
        "exit_code": 1,
        "status": "blocked",
        "workflow_audit_path": relative(artifacts["workflow_audit_json"], paths.project_root),
        "workflow_audit_overall_passed": False,
        "workflow_blocking_reasons": list(blocking_reasons),
        "workflow_warnings": list(warnings),
        "post_workflow_modules_run": False,
        "post_workflow_results": [],
        "blocking_reasons": list(blocking_reasons),
        "warnings": list(warnings),
    }


def build_workflow_execution_record(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    resolved_as_of_date: str,
    mode: str,
    workflow_mode: str,
    command: str,
    started_at: str,
    finished_at: str,
    exit_code: int,
    workflow_audit: dict[str, Any],
    post_workflow_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = workflow_artifact_paths(paths, resolved_as_of_date)
    post_results = post_workflow_results or []
    blocking = list(workflow_audit.get("blocking_reasons", []))
    warnings = list(workflow_audit.get("warnings", []))
    return {
        "execution_id": "A-SHARE-CURRENT-DAY-WORKFLOW-EXECUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "mode": mode,
        "workflow_mode": workflow_mode,
        "command": command,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": _duration_seconds(started_at, finished_at),
        "exit_code": exit_code,
        "status": "passed" if exit_code == 0 and workflow_audit.get("overall_passed") is True else "failed",
        "workflow_audit_path": relative(artifacts["workflow_audit_json"], paths.project_root),
        "workflow_audit_overall_passed": workflow_audit.get("overall_passed") is True,
        "workflow_blocking_reasons": blocking,
        "workflow_warnings": warnings,
        "post_workflow_modules_run": bool(post_results),
        "post_workflow_results": post_results,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }


def build_not_run_workflow_execution(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    resolved_as_of_date: str,
    mode: str,
    workflow_mode: str,
    command: str,
    warnings: list[str],
) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = workflow_artifact_paths(paths, resolved_as_of_date)
    now = utc_now()
    return {
        "execution_id": "A-SHARE-CURRENT-DAY-WORKFLOW-EXECUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "mode": mode,
        "workflow_mode": workflow_mode,
        "command": command,
        "started_at": now,
        "finished_at": now,
        "duration_seconds": 0.0,
        "exit_code": 0,
        "status": "not_run",
        "workflow_audit_path": relative(artifacts["workflow_audit_json"], paths.project_root),
        "workflow_audit_overall_passed": False,
        "workflow_blocking_reasons": [],
        "workflow_warnings": [],
        "post_workflow_modules_run": False,
        "post_workflow_results": [],
        "blocking_reasons": [],
        "warnings": list(warnings),
    }


def _duration_seconds(started_at: str, finished_at: str) -> float:
    started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    finished = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
    return round((finished - started).total_seconds(), 6)

