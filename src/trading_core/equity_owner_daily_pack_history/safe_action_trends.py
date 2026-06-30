"""Safe action trends."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import FORBIDDEN_SAFE_ACTION_MARKERS, TARGET_VERSION


def build_safe_action_trend_baseline(*, as_of_date: str, records: list[dict[str, Any]], safe_action_digest: dict[str, Any], sufficiency: dict[str, Any]) -> dict[str, Any]:
    items = safe_action_digest.get("items", [])
    forbidden = [
        str(item)
        for item in items + safe_action_digest.get("forbidden_safe_action_type_hits", [])
        if any(marker in str(item).lower() for marker in FORBIDDEN_SAFE_ACTION_MARKERS)
    ]
    return {
        "baseline_id": "A-SHARE-SAFE-ACTION-TREND-BASELINE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "observation_count": len(records),
        "trend_analysis_available": sufficiency["trend_analysis_available"],
        "safe_action_count": safe_action_digest.get("safe_action_count", 0),
        "automatic_action_count": safe_action_digest.get("automatic_action_count", 0),
        "forbidden_safe_action_hits": sorted(set(forbidden)),
        "safe_actions_not_trade_related": not forbidden,
        "repeated_items": [] if not sufficiency["trend_analysis_available"] else _repeated(records, "safe_action_count"),
        "no_fabricated_trends": True,
    }


def _repeated(records: list[dict[str, Any]], field: str) -> list[str]:
    return [field] if sum(1 for row in records if row.get(field, 0) > 0) >= 2 else []
