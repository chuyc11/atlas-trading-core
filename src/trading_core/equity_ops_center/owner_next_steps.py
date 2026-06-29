"""Owner next-step classification for the daily ops center."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_center.ops_config import TARGET_VERSION


def build_ops_owner_next_steps(*, as_of_date: str, health_score: dict[str, Any], action_summary: dict[str, Any]) -> dict[str, Any]:
    do_now = [] if health_score.get("blocking_issue_count", 0) == 0 else ["Stop release validation and review blocking issues."]
    review_today = action_summary.get("top_owner_actions", [])
    wait = ["等待更多 monitoring/run-history 样本后再解释趋势。"] if action_summary.get("wait_for_history_count", 0) else []
    developer = ["开发者跟进 blocking 或 forbidden boundary 命中。"] if do_now else []
    no_action = ["当前无需自动操作；继续观察并按 checklist 人工复核。"] if not do_now else []
    return {
        "next_steps_id": "A-SHARE-DAILY-OPS-CENTER-OWNER-NEXT-STEPS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "do_now": do_now,
        "review_today": review_today,
        "wait_for_more_history": wait,
        "developer_follow_up": developer,
        "no_action_required": no_action,
    }
