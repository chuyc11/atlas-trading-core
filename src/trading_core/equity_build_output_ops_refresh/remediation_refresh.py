"""Remediation refresh sourced from build-output dashboard."""

from __future__ import annotations

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import TARGET_VERSION
from trading_core.equity_build_output_ops_refresh.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


FORBIDDEN_SAFE_ACTION_TYPES = {"place_order", "connect_broker", "read_real_account", "generate_order_preview"}


def build_remediation_refresh(*, paths: ProjectPaths, as_of_date: str) -> dict:
    priority = load_json(paths.data_dir / "equity_owner_remediation" / "daily" / as_of_date / "remediation_priority_summary.json")
    protected = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_protected_path_card.json")
    return {
        "refresh_id": "A-SHARE-BUILD-OUTPUT-REMEDIATION-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "remediation_refresh_performed": True,
        "status": priority.get("status", "manual_review_required"),
        "priority_buckets": priority.get("priority_buckets", {}),
        "protected_path_modifications_detected": protected.get("protected_path_modifications_detected", True),
        "execute_remediation_actions": False,
        "commands_executed": [],
        "external_notifications_sent": False,
        "remediation_used_as_trade_instruction": False,
    }


def build_safe_action_refresh(*, paths: ProjectPaths, as_of_date: str) -> dict:
    checklist = load_json(paths.data_dir / "equity_owner_remediation" / "daily" / as_of_date / "safe_owner_action_checklist.json")
    items = checklist.get("items", [])
    forbidden_hits = [
        item.get("item_id") or item.get("safe_action_type")
        for item in items
        if item.get("safe_action_type") in FORBIDDEN_SAFE_ACTION_TYPES
        or item.get("allowed_to_execute_automatically") is True
    ]
    refreshed_items = []
    for item in items:
        refreshed = dict(item)
        refreshed["allowed_to_execute_automatically"] = False
        refreshed["command_if_any"] = None
        refreshed_items.append(refreshed)
    return {
        "refresh_id": "A-SHARE-BUILD-OUTPUT-SAFE-ACTION-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "safe_action_refresh_performed": True,
        "safe_action_count": len(refreshed_items),
        "manual_review_count": len(refreshed_items),
        "automatic_action_count": 0,
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
        "forbidden_safe_action_type_hits": sorted(set(filter(None, forbidden_hits))),
        "items": refreshed_items,
        "overall_passed": not forbidden_hits,
        "blocking_reasons": ["forbidden_safe_action_type_present"] if forbidden_hits else [],
    }

