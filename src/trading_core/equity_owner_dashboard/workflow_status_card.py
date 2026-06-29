"""Workflow status card."""

from __future__ import annotations

from typing import Any

from trading_core.equity_current_day.current_day_config import current_day_artifact_paths
from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.equity_owner_dashboard.input_availability import load_json
from trading_core.equity_workflows.workflow_config import workflow_artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_workflow_status_card(*, paths: ProjectPaths | None, as_of_date: str, resolved_as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    current = current_day_artifact_paths(paths, as_of_date)
    workflow = workflow_artifact_paths(paths, resolved_as_of_date)
    current_audit = load_json(current["current_day_audit_json"])
    execution = load_json(current["current_day_workflow_execution"])
    workflow_audit = load_json(workflow["workflow_audit_json"])
    stage_manifest = load_json(workflow["workflow_stage_manifest"])
    stages = stage_manifest.get("stages", [])
    return {
        "card_id": "WORKFLOW_STATUS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "current_day_run_audit_passed": current_audit.get("overall_passed") is True,
        "workflow_audit_passed": workflow_audit.get("overall_passed") is True,
        "workflow_mode": execution.get("workflow_mode"),
        "workflow_command": execution.get("command"),
        "old_run_daily_called": False,
        "run_daily_called": False,
        "day2_executed": False,
        "stage_status_table": [{"stage_id": row.get("stage_id"), "stage_name": row.get("stage_name"), "status": row.get("status")} for row in stages],
        "stage_passed_count": sum(1 for row in stages if row.get("status") == "passed"),
        "stage_warning_count": sum(len(row.get("warnings", [])) for row in stages),
        "stage_failed_count": sum(1 for row in stages if row.get("status") in {"failed", "blocked"}),
        "blocking_reasons": list(current_audit.get("blocking_reasons", [])) + list(workflow_audit.get("blocking_reasons", [])),
        "warnings": sorted(set(current_audit.get("warnings", []) + workflow_audit.get("warnings", []))),
    }

