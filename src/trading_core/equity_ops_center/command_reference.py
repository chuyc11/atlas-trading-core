"""Safe command reference for the daily ops center."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_center.ops_config import TARGET_VERSION
from trading_core.equity_ops_center.ops_plan import safe_audit_commands


def build_ops_command_reference(*, as_of_date: str) -> dict[str, Any]:
    commands = safe_audit_commands(as_of_date)
    return {
        "reference_id": "A-SHARE-DAILY-OPS-CENTER-COMMAND-REFERENCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "safe_owner_commands": [{"command": command, "class": "audit_or_aggregate", "allowed_by_default": command.endswith("aggregate_existing_ops_artifacts")} for command in commands],
        "excluded_command_classes": ["run-daily", "broker commands", "order commands", "trade commands", "real account commands"],
    }
