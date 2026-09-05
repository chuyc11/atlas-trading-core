"""Safe action aggregation for the daily ops center."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_center.ops_config import TARGET_VERSION


TRADE_ACTION_TOKENS = ["place_order", "cancel_order", "buy_stock", "sell_stock", "connect_broker", "read_real_account", "enable_live_trading", "rebalance real account"]


def build_ops_action_summary(*, as_of_date: str, payloads: dict[str, Any]) -> dict[str, Any]:
    checklist = payloads.get("safe_owner_action_checklist", {})
    items = checklist.get("items", [])
    rerun = [item for item in items if str(item.get("safe_action_type", "")).startswith("rerun_safe")]
    wait = [item for item in items if item.get("safe_action_type") == "wait_for_more_history"]
    escalation = [item for item in items if item.get("safe_action_type") == "escalate_to_developer"]
    manual = [item for item in items if item.get("manual_review_required")]
    forbidden_hits = [item.get("item_id") for item in items if _trade_related(item)]
    return {
        "summary_id": "A-SHARE-DAILY-OPS-CENTER-ACTION-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "safe_action_count": int(checklist.get("safe_action_count", len(items))),
        "automatic_action_count": int(checklist.get("automatic_action_count", 0)),
        "manual_review_count": len(manual),
        "rerun_safe_validation_count": len(rerun),
        "wait_for_history_count": len(wait),
        "escalation_count": len(escalation),
        "top_owner_actions": [item.get("title_zh") for item in items[:5]],
        "forbidden_action_hits": sorted({str(item) for item in forbidden_hits if item}),
    }


def _trade_related(item: dict[str, Any]) -> bool:
    text = " ".join(str(item.get(key, "")).lower() for key in ["title_zh", "description_zh", "safe_action_type", "command_if_any"])
    return any(token in text for token in TRADE_ACTION_TOKENS)
