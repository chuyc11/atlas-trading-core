"""Execution plan for v0.8.7 gated build."""

from __future__ import annotations

from trading_core.equity_current_day_builds.gated_build_config import (
    TARGET_VERSION,
    TO_WORKFLOW_MODE,
)
from trading_core.system.safe_workflow_command import current_day_workflow_argv, current_day_workflow_display


def build_gated_build_execution_plan(
    *,
    as_of_date: str,
    preflight_gate: dict,
) -> dict:
    command_argv = current_day_workflow_argv(as_of_date)
    command = current_day_workflow_display(as_of_date)

    commands_allowed = [command]
    commands_forbidden = [
        "run-daily",
        "broker",
        "order",
        "trade",
        "easytrader",
        "THSTrader",
        "buy",
        "sell",
    ]

    expected_outputs = [
        "gated_build_execution_record",
        "build_from_existing_data_workflow_result",
        "build_from_existing_data_audit_link",
        "build_artifact_index",
        "validate_vs_build_comparison",
        "artifact_drift_summary",
    ]

    return {
        "plan_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-EXECUTION-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "preflight_required": True,
        "preflight_must_pass": True,
        "preflight_passed": preflight_gate.get("overall_passed", False),
        "workflow_command": command,
        "workflow_argv": command_argv,
        "workflow_mode": TO_WORKFLOW_MODE,
        "commands_allowed": commands_allowed,
        "commands_forbidden": commands_forbidden,
        "expected_outputs": expected_outputs,
        "expected_audits": [
            "gated_build_audit_json",
            "gated_build_boundary_check",
        ],
        "boundary_expectations": {
            "gated_build_from_existing_data_only": True,
            "research_only": True,
            "virtual_only": True,
            "old_run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
        },
    }
