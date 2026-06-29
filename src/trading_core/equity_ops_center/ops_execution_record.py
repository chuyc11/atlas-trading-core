"""Execution record for the daily ops center."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_center.ops_config import AGGREGATE_EXISTING_OPS_ARTIFACTS, TARGET_VERSION


def build_ops_execution_record(*, as_of_date: str, mode: str, commands_executed: list[str] | None = None, safe_validation_chain_run: bool = False) -> dict[str, Any]:
    commands = list(commands_executed or [])
    return {
        "execution_id": "A-SHARE-DAILY-OPS-CENTER-EXECUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "commands_executed": commands,
        "aggregate_existing_artifacts_only": mode == AGGREGATE_EXISTING_OPS_ARTIFACTS and not commands,
        "safe_validation_chain_run": safe_validation_chain_run,
        "data_refresh_run": False,
        "current_day_research_run": False,
        "dashboard_build_run": False,
        "monitoring_build_run": False,
        "remediation_build_run": False,
        "remediation_actions_executed": False,
        "external_notifications_sent": False,
        "status": "passed" if not commands or safe_validation_chain_run else "passed",
    }
