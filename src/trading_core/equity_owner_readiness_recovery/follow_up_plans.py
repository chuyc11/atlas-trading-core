"""Developer and owner follow-up recovery plans."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.equity_owner_readiness_recovery.task_backlog import FORBIDDEN_ACTIONS, SAFE_AUDIT_COMMANDS


def build_developer_follow_up_recovery_plan(*, as_of_date: str = DEFAULT_AS_OF_DATE, developer_tracker: dict[str, Any]) -> dict[str, Any]:
    items = []
    for item in developer_tracker.get("items", []):
        items.append(
            {
                "follow_up_id": item["follow_up_id"],
                "source_exception_id": item["source_exception_id"],
                "priority": item["priority"],
                "suggested_investigation": item["suggested_investigation"],
                "expected_artifacts_to_inspect": ["owner_readiness_gap_analysis.json", "quality_exception_classification.json"],
                "expected_fix_type": "threshold_explanation_fix",
                "safe_audit_only_commands": list(SAFE_AUDIT_COMMANDS),
                "forbidden_actions": list(FORBIDDEN_ACTIONS),
                "completion_evidence_required": ["updated quality explanation", "passing audit-only verification"],
                "status": "planned",
            }
        )
    return {"plan_id": "A-SHARE-DEVELOPER-FOLLOW-UP-RECOVERY-PLAN", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "follow_up_count": len(items), "items": items}


def build_owner_follow_up_recovery_plan(*, as_of_date: str = DEFAULT_AS_OF_DATE, owner_checklist: dict[str, Any]) -> dict[str, Any]:
    actions = [
        "review_blocked_daily_pack_notice",
        "review_readiness_gap_summary",
        "review_quality_exception_report",
        "review_developer_follow_up_tracker",
        "confirm_no_trade_action",
        "wait_for_more_history",
        "rerun_audit_only_after_fix",
    ]
    items = [{"action": action, "status": "planned", "trade_related": False, "broker_related": False, "order_related": False} for action in actions]
    return {"plan_id": "A-SHARE-OWNER-FOLLOW-UP-RECOVERY-PLAN", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "owner_follow_up_count": len(items), "items": items, "source_owner_follow_up_count": owner_checklist.get("owner_follow_up_count", 0)}
