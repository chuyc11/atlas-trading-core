"""Safe action recurrence baseline."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_history.ops_history_config import TARGET_VERSION


FORBIDDEN_ACTION_TOKENS = ["place_order", "cancel_order", "buy_stock", "sell_stock", "connect_broker", "read_real_account", "enable_live_trading", "rebalance"]


def build_ops_action_recurrence_baseline(*, as_of_date: str, action_checklist: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    items = []
    source_items = list(action_checklist.get("items", []))
    if not source_items:
        source_items = [
            {
                "safe_action_type": f"manual_owner_review_{index:02d}",
                "title_zh": title,
                "allowed_to_execute_automatically": False,
                "command_if_any": "",
            }
            for index, title in enumerate(action_checklist.get("top_owner_actions", []), start=1)
        ]
        target_count = int(action_checklist.get("safe_action_count", len(source_items)) or len(source_items))
        for index in range(len(source_items) + 1, target_count + 1):
            source_items.append(
                {
                    "safe_action_type": f"manual_safe_action_{index:02d}",
                    "title_zh": f"manual safe action {index:02d}",
                    "allowed_to_execute_automatically": False,
                    "command_if_any": "",
                }
            )
    for item in source_items:
        text = " ".join(str(item.get(key, "")).lower() for key in ["safe_action_type", "command_if_any"])
        trade_related = any(token in text for token in FORBIDDEN_ACTION_TOKENS)
        items.append(
            {
                "safe_action_type": item.get("safe_action_type"),
                "action_title": item.get("title_zh"),
                "first_seen_date": as_of_date,
                "last_seen_date": as_of_date,
                "seen_count": 1,
                "automatic_action_allowed": item.get("allowed_to_execute_automatically") is True,
                "trade_related": trade_related,
                "broker_related": "broker" in text and trade_related,
                "order_related": "order" in text and trade_related,
                "recurrence_status": "new" if len(records) <= 1 else "insufficient_history",
            }
        )
    return {"baseline_id": "A-SHARE-OPS-ACTION-RECURRENCE-BASELINE", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "items": items}
