"""Owner follow-up checklist."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_owner_follow_up_checklist(*, as_of_date: str = DEFAULT_AS_OF_DATE, classification: dict[str, Any]) -> dict[str, Any]:
    items = [
        {
            "item_id": f"OWNER-REVIEW:{row['exception_id']}",
            "source_exception_id": row["exception_id"],
            "owner_action": "Review exception details and wait for developer follow-up where required.",
            "trade_related": False,
            "broker_related": False,
            "order_related": False,
            "status": "open",
        }
        for row in classification.get("classifications", [])
        if row.get("owner_follow_up_required")
    ]
    return {
        "checklist_id": "A-SHARE-OWNER-FOLLOW-UP-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_follow_up_count": len(items),
        "items": items,
        "not_investment_advice": True,
        "not_order_instruction": True,
    }
