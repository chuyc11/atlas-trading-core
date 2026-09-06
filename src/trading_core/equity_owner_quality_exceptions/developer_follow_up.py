"""Developer follow-up tracker."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, FORBIDDEN_COMMAND_FRAGMENTS, TARGET_VERSION

SAFE_AUDIT_COMMANDS = [
    "python -m trading_core.cli audit-a-share-owner-readiness-gate --as-of-date 2026-06-26",
    "python -m trading_core.cli audit-a-share-owner-daily-pack-history --as-of-date 2026-06-26",
    "python -m trading_core.cli audit-a-share-owner-daily-pack --as-of-date 2026-06-26",
]
FORBIDDEN_ACTIONS = ["do not connect broker", "do not place orders", "do not generate buy or sell signals", "do not call run-daily"]


def build_developer_follow_up_tracker(*, as_of_date: str = DEFAULT_AS_OF_DATE, classification: dict[str, Any]) -> dict[str, Any]:
    items = []
    for row in classification.get("classifications", []):
        if row.get("developer_follow_up_required"):
            items.append(
                {
                    "follow_up_id": f"FOLLOW-UP:{row['exception_id']}",
                    "source_exception_id": row["exception_id"],
                    "priority": "P1" if row["severity"] == "blocking" else "P2",
                    "owner_visible": True,
                    "developer_action_required": True,
                    "suggested_investigation": f"Review {row['category']} evidence and update quality improvement plan.",
                    "safe_audit_only_commands": list(SAFE_AUDIT_COMMANDS),
                    "forbidden_actions": list(FORBIDDEN_ACTIONS),
                    "status": "open",
                }
            )
    return {
        "tracker_id": "A-SHARE-DEVELOPER-FOLLOW-UP-TRACKER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "follow_up_count": len(items),
        "items": items,
        "no_forbidden_follow_up_commands": _commands_clean(items),
    }


def _commands_clean(items: list[dict[str, Any]]) -> bool:
    for item in items:
        for command in item.get("safe_audit_only_commands", []):
            lower = command.lower()
            if any(fragment.lower() in lower for fragment in FORBIDDEN_COMMAND_FRAGMENTS if fragment != "run-daily"):
                return False
            if "run-daily" in lower:
                return False
    return True
