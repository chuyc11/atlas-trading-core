"""Ops plan and safe command policy."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_center.ops_config import FORBIDDEN_COMMAND_TOKENS, TARGET_VERSION


def build_ops_plan(*, as_of_date: str, mode: str) -> dict[str, Any]:
    commands = safe_audit_commands(as_of_date)
    planned = [
        {"step": 1, "action": "validate data refresh audit", "command": commands[0], "command_class": "audit"},
        {"step": 2, "action": "validate current-day run audit", "command": commands[1], "command_class": "audit"},
        {"step": 3, "action": "validate owner dashboard audit", "command": commands[2], "command_class": "audit"},
        {"step": 4, "action": "validate owner monitoring audit", "command": commands[3], "command_class": "audit"},
        {"step": 5, "action": "validate owner remediation audit", "command": commands[4], "command_class": "audit"},
        {"step": 6, "action": "aggregate module statuses", "command": None, "command_class": "aggregate"},
        {"step": 7, "action": "aggregate issues and safe actions", "command": None, "command_class": "aggregate"},
        {"step": 8, "action": "generate ops center reports", "command": None, "command_class": "aggregate"},
        {"step": 9, "action": "audit ops center", "command": commands[5], "command_class": "audit"},
    ]
    disallowed = forbidden_command_hits([row["command"] for row in planned if row.get("command")])
    return {
        "plan_id": "A-SHARE-DAILY-OPS-CENTER-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "planned_sequence": planned,
        "planned_commands": commands,
        "commands_allowed": [] if disallowed else commands,
        "commands_disallowed": disallowed,
        "commands_executed": [],
        "execute_plan": False,
        "execution_policy": "aggregate_existing_artifacts_only",
        "external_side_effects": False,
    }


def safe_audit_commands(as_of_date: str) -> list[str]:
    return [
        f"python -m trading_core.cli audit-a-share-daily-data-refresh --as-of-date {as_of_date}",
        f"python -m trading_core.cli audit-a-share-current-day-research-run --as-of-date {as_of_date}",
        f"python -m trading_core.cli audit-a-share-owner-dashboard --as-of-date {as_of_date}",
        f"python -m trading_core.cli audit-a-share-owner-monitoring --as-of-date {as_of_date}",
        f"python -m trading_core.cli audit-a-share-owner-remediation --as-of-date {as_of_date}",
        f"python -m trading_core.cli build-and-audit-a-share-daily-ops-center --as-of-date {as_of_date} --mode aggregate_existing_ops_artifacts",
    ]


def forbidden_command_hits(commands: list[str]) -> list[str]:
    hits: list[str] = []
    for command in commands:
        lower = command.lower()
        for token in FORBIDDEN_COMMAND_TOKENS:
            if token in lower:
                hits.append(f"{command}:{token}")
    return sorted(set(hits))
