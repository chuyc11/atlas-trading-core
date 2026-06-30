"""Safe action digest."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import FORBIDDEN_SAFE_ACTION_TYPES, TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_safe_action_digest(*, paths: ProjectPaths, as_of_date: str) -> dict:
    safe = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_safe_action_refresh.json")
    items = safe.get("items", [])
    forbidden = [
        item.get("item_id") or item.get("safe_action_type")
        for item in items
        if item.get("safe_action_type") in FORBIDDEN_SAFE_ACTION_TYPES
        or item.get("allowed_to_execute_automatically") is True
    ]
    return {
        "digest_id": "A-SHARE-SAFE-ACTION-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "safe_action_count": safe.get("safe_action_count", len(items)),
        "manual_review_count": safe.get("manual_review_count", len(items)),
        "automatic_action_count": 0,
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
        "forbidden_safe_action_type_hits": sorted(set(filter(None, forbidden))),
        "overall_passed": not forbidden,
        "blocking_reasons": ["forbidden_safe_action_type_present"] if forbidden else [],
    }

