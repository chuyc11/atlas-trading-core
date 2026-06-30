"""Owner next-step trends."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import FORBIDDEN_SAFE_ACTION_MARKERS, TARGET_VERSION


def build_owner_next_step_trend(*, as_of_date: str, records: list[dict[str, Any]], checklist: dict[str, Any]) -> dict[str, Any]:
    steps = []
    for key in ["do_now", "review_today", "wait_for_more_history", "developer_follow_up", "no_action_required"]:
        steps.extend(str(item) for item in checklist.get(key, []))
    blocked = [step for step in steps if any(marker in step.lower() for marker in FORBIDDEN_SAFE_ACTION_MARKERS)]
    return {
        "trend_id": "A-SHARE-OWNER-NEXT-STEP-TREND",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "observation_count": len(records),
        "current_step_count": len(steps),
        "blocked_trade_like_steps": blocked,
        "owner_next_steps_trade_instruction_free": not blocked,
        "no_fabricated_trends": True,
    }
