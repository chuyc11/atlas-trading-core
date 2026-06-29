"""Repeat build execution record."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime

from trading_core.equity_build_repeatability.repeatability_config import TARGET_VERSION, WORKFLOW_MODE
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def execute_repeat_build_and_record(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    input_availability: dict,
    date_alignment: dict,
    execution_plan: dict,
) -> dict:
    paths = default_paths(paths)
    preflight_ok = input_availability.get("overall_passed", False) and date_alignment.get("overall_passed", False)
    command = execution_plan.get("workflow_command") or execution_plan.get("command", "")
    if not preflight_ok or not execution_plan.get("command_allowed", False):
        return _base_record(
            as_of_date=as_of_date,
            command=command,
            command_executed=False,
            exit_code=None,
            status="preflight_failed",
            started_at=None,
            finished_at=None,
            duration_seconds=None,
            blocking_reasons=["repeatability_preflight_failed"],
            warnings=[],
            workflow_audit_path="",
            workflow_audit_overall_passed=False,
        )

    started = datetime.now(UTC)
    exit_code = -1
    stderr_text = ""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(paths.project_root),
        )
        exit_code = result.returncode
        stderr_text = result.stderr
    except subprocess.TimeoutExpired:
        stderr_text = "command timed out after 300s"
    except Exception as exc:
        stderr_text = str(exc)
    finished = datetime.now(UTC)
    duration = round((finished - started).total_seconds(), 3)

    audit_path = paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json"
    audit_passed = False
    workflow_blocking: list[str] = []
    warnings: list[str] = []
    if audit_path.exists():
        try:
            payload = json.loads(audit_path.read_text(encoding="utf-8"))
            audit_passed = payload.get("overall_passed", False) is True
            workflow_blocking = payload.get("blocking_reasons", [])
            warnings = payload.get("warnings", [])
        except Exception:
            pass

    blocking = []
    if exit_code != 0:
        blocking.append("repeat_build_command_failed")
    if not audit_passed:
        blocking.append("repeat_build_audit_failed")
    blocking.extend(workflow_blocking)
    if stderr_text and exit_code != 0:
        warnings.append(stderr_text[:500])

    return _base_record(
        as_of_date=as_of_date,
        command=command,
        command_executed=True,
        exit_code=exit_code,
        status="passed" if exit_code == 0 and audit_passed and not workflow_blocking else "failed",
        started_at=started.isoformat().replace("+00:00", "Z"),
        finished_at=finished.isoformat().replace("+00:00", "Z"),
        duration_seconds=duration,
        blocking_reasons=sorted(set(blocking)),
        warnings=sorted(set(warnings)),
        workflow_audit_path=str(audit_path) if audit_path.exists() else "",
        workflow_audit_overall_passed=audit_passed,
    )


def _base_record(**kwargs) -> dict:
    return {
        "execution_id": "A-SHARE-REPEAT-BUILD-FROM-EXISTING-DATA-EXECUTION",
        "target_version": TARGET_VERSION,
        "workflow_mode": WORKFLOW_MODE,
        **kwargs,
        "old_run_daily_called": False,
        "run_daily_called": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "buy_sell_signals_generated": False,
        "order_preview_generated": False,
        "real_account_data_read": False,
        "public_network_refresh_run": False,
        "full_research_run": False,
    }

