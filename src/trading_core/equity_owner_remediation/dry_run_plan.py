"""Dry-run remediation plan. This module never executes commands."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_remediation.remediation_config import TARGET_VERSION


def build_dry_run_remediation_plan(*, as_of_date: str, checklist: dict[str, Any]) -> dict[str, Any]:
    return {
        "plan_id": "A-SHARE-OWNER-REMEDIATION-DRY-RUN-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "execute_remediation_actions": False,
        "dry_run_only": True,
        "planned_actions": [
            {
                "item_id": item["item_id"],
                "safe_action_type": item["safe_action_type"],
                "manual_review_required": item["manual_review_required"],
            }
            for item in checklist.get("items", [])
        ],
        "commands_to_review": [item["command_if_any"] for item in checklist.get("items", []) if item.get("command_if_any")],
        "commands_executed": [],
        "external_side_effects": False,
        "broker_or_order_side_effects": False,
    }
