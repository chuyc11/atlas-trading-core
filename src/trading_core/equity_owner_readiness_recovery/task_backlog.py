"""Recovery task backlog."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, FORBIDDEN_TASK_CATEGORIES, TARGET_VERSION

SAFE_AUDIT_COMMANDS = [
    "python -m trading_core.cli audit-a-share-owner-quality-exceptions --as-of-date 2026-06-26",
    "python -m trading_core.cli audit-a-share-owner-readiness-gate --as-of-date 2026-06-26",
    "python -m trading_core.cli audit-a-share-owner-daily-pack-history --as-of-date 2026-06-26",
    "python -m trading_core.cli audit-a-share-owner-daily-pack --as-of-date 2026-06-26",
]
FORBIDDEN_ACTIONS = ["do not connect broker", "do not place orders", "do not generate buy or sell signals", "do not call run-daily"]


def build_recovery_task_backlog(*, as_of_date: str = DEFAULT_AS_OF_DATE, root_map: dict[str, Any], score_gap: int) -> dict[str, Any]:
    tasks = []
    for item in root_map.get("items", []):
        category = _task_category(item)
        tasks.append(
            {
                "task_id": item["proposed_recovery_task_ids"][0],
                "target_version": TARGET_VERSION,
                "as_of_date": as_of_date,
                "title_zh": _title(item["category"]),
                "category": category,
                "source_exception_id": item["exception_id"],
                "priority": "P1" if item["severity"] == "blocking" else "P2",
                "owner_visible": True,
                "developer_action_required": item["requires_developer_follow_up"],
                "owner_action_required": item["requires_owner_review"],
                "requires_more_history": item["requires_more_history"],
                "expected_score_impact": _impact(item["category"], score_gap),
                "evidence_required": item["evidence"],
                "verification_method": "audit_only_verification",
                "safe_audit_only_commands": list(SAFE_AUDIT_COMMANDS),
                "forbidden_actions": list(FORBIDDEN_ACTIONS),
                "status": "planned",
            }
        )
    return {
        "backlog_id": "A-SHARE-RECOVERY-TASK-BACKLOG",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "task_count": len(tasks),
        "tasks": tasks,
        "tasks_marked_complete_by_default": any(task["status"] == "complete" for task in tasks),
        "forbidden_recovery_task_categories_detected": sorted({task["category"] for task in tasks if task["category"] in FORBIDDEN_TASK_CATEGORIES}),
    }


def _task_category(item: dict[str, Any]) -> str:
    if item["requires_more_history"]:
        return "wait_for_more_history"
    if item["category"] == "warning_issue_threshold_issue":
        return "resolve_warning_source"
    if item["requires_developer_follow_up"]:
        return "developer_follow_up"
    return "audit_only_verification"


def _title(category: str) -> str:
    return {
        "readiness_score_below_threshold": "定位 readiness score 未达标的可恢复质量短板",
        "warning_issue_threshold_issue": "梳理 warning issue 并补充安全解释",
        "insufficient_history": "等待更多真实历史样本后再解释趋势",
    }.get(category, "补充质量异常证据")


def _impact(category: str, score_gap: int) -> int:
    if category == "readiness_score_below_threshold":
        return score_gap
    if category == "warning_issue_threshold_issue":
        return 10
    return 0
