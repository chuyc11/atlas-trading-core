"""Execution record for v0.8.7 gated build."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime

from trading_core.equity_current_day_builds.gated_build_config import (
    TARGET_VERSION,
    TO_WORKFLOW_MODE,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths
from trading_core.system.safe_workflow_command import current_day_workflow_argv, current_day_workflow_display, normalize_iso_date


def execute_gated_build_and_record(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    preflight_gate: dict,
    execution_plan: dict,
) -> dict:
    paths = default_paths(paths)
    as_of_date = normalize_iso_date(as_of_date)

    if not preflight_gate.get("overall_passed", False):
        return {
            "execution_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-EXECUTION",
            "target_version": TARGET_VERSION,
            "as_of_date": as_of_date,
            "workflow_mode": TO_WORKFLOW_MODE,
            "command": execution_plan.get("workflow_command", ""),
            "command_executed": False,
            "exit_code": None,
            "status": "preflight_failed",
            "started_at": None,
            "finished_at": None,
            "duration_seconds": None,
            "workflow_audit_path": "",
            "workflow_audit_overall_passed": False,
            "blocking_reasons": ["preflight_gate_not_passed"],
            "warnings": [],
            "old_run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "buy_sell_signals_generated": False,
            "order_preview_generated": False,
        }

    command = current_day_workflow_display(as_of_date)
    expected_plan_argv = current_day_workflow_argv(as_of_date)
    if execution_plan.get("workflow_command") != command or execution_plan.get("workflow_argv") != expected_plan_argv:
        return {
            "execution_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-EXECUTION",
            "target_version": TARGET_VERSION,
            "as_of_date": as_of_date,
            "workflow_mode": TO_WORKFLOW_MODE,
            "command": command,
            "command_executed": False,
            "exit_code": None,
            "status": "preflight_failed",
            "started_at": None,
            "finished_at": None,
            "duration_seconds": None,
            "workflow_audit_path": "",
            "workflow_audit_overall_passed": False,
            "blocking_reasons": ["execution_plan_command_mismatch"],
            "warnings": [],
            "old_run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "buy_sell_signals_generated": False,
            "order_preview_generated": False,
        }
    command_argv = current_day_workflow_argv(as_of_date, executable=True)
    started = datetime.now(UTC)
    exit_code = None

    try:
        result = subprocess.run(
            command_argv,
            shell=False,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(paths.project_root),
        )
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        exit_code = -1
    except Exception:
        exit_code = -1

    finished = datetime.now(UTC)
    duration = (finished - started).total_seconds()

    status = "passed" if exit_code == 0 else "failed"

    # Locate workflow audit
    current_day_audit = (
        paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json"
    )
    workflow_audit_passed = False
    workflow_audit_path = ""
    workflow_blocking = []
    workflow_warnings_list = []

    if current_day_audit.exists():
        import json
        try:
            audit_payload = json.loads(current_day_audit.read_text(encoding="utf-8"))
            workflow_audit_passed = audit_payload.get("overall_passed", False)
            workflow_audit_path = str(current_day_audit)
            workflow_blocking = audit_payload.get("blocking_reasons", [])
            workflow_warnings_list = audit_payload.get("warnings", [])
        except Exception:
            workflow_audit_path = str(current_day_audit)

    blocking = []
    if exit_code != 0:
        blocking.append("workflow_command_failed")
    if not workflow_audit_passed and workflow_audit_path:
        blocking.append("workflow_audit_failed")
    blocking.extend(workflow_blocking)

    return {
        "execution_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-EXECUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "workflow_mode": TO_WORKFLOW_MODE,
        "command": command,
        "command_executed": True,
        "exit_code": exit_code,
        "status": status,
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "finished_at": finished.isoformat().replace("+00:00", "Z"),
        "duration_seconds": round(duration, 3),
        "workflow_audit_path": workflow_audit_path,
        "workflow_audit_overall_passed": workflow_audit_passed,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(workflow_warnings_list)),
        "old_run_daily_called": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "buy_sell_signals_generated": False,
        "order_preview_generated": False,
    }
