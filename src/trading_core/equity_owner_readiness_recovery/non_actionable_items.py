"""Non-actionable recovery items."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_non_actionable_recovery_items(*, as_of_date: str = DEFAULT_AS_OF_DATE, root_map: dict[str, Any]) -> dict[str, Any]:
    items = [
        {
            "item_id": f"NON-ACTIONABLE:{item['exception_id']}",
            "source_exception_id": item["exception_id"],
            "reason": "requires more real history before trend interpretation",
            "status": "waiting_for_more_history",
        }
        for item in root_map.get("items", [])
        if item.get("requires_more_history")
    ]
    return {"list_id": "A-SHARE-NON-ACTIONABLE-RECOVERY-ITEMS", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "item_count": len(items), "items": items}
