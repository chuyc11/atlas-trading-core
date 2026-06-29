"""Safe owner action checklist generation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_remediation.remediation_config import ALLOWED_SAFE_ACTION_TYPES, FORBIDDEN_ACTION_TYPES, TARGET_VERSION
from trading_core.equity_owner_remediation.remediation_mapping import DISALLOWED_ACTIONS


def build_safe_owner_action_checklist(*, as_of_date: str, issue_catalog: dict[str, Any]) -> dict[str, Any]:
    items = [
        _item("VERIFY-AUDITS", "P0", "audit", "检查 audit 是否通过", "确认 data refresh、current-day、dashboard、monitoring audit 都通过。", "verify_audit", None),
        _item("CHECK-WARNINGS", "P1", "warning", "检查 warning 是否为已知非阻塞", "逐条确认 warning 已映射或明确分类为 unknown。", "document_known_warning", None),
        _item("CHECK-SOURCE-TRACE", "P1", "source_trace", "检查 source trace 是否完整", "确认 remediation source trace 没有禁用来源。", "inspect_artifact", None),
        _item("CHECK-BOUNDARY", "P0", "boundary", "检查 boundary 是否干净", "确认没有 broker、真实账户、订单、旧 run-daily 或 day2 执行痕迹。", "verify_audit", None),
        _item(
            "REVIEW-DATA-VALIDATION",
            "P1",
            "data",
            "检查是否需要安全重跑数据验证",
            "仅作为人工可复核命令，不由本 builder 执行。",
            "rerun_safe_data_validation",
            f"python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date {as_of_date} --mode validate_existing_data",
        ),
        _item(
            "REVIEW-CURRENT-DAY-VALIDATION",
            "P1",
            "workflow",
            "检查是否需要安全重跑 current-day validation",
            "仅验证既有 artifacts，不自动刷新数据。",
            "rerun_safe_current_day_research_validation",
            f"python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date {as_of_date} --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts",
        ),
        _item(
            "REVIEW-DASHBOARD-MONITORING",
            "P1",
            "dashboard_monitoring",
            "检查是否需要安全重跑 dashboard / monitoring",
            "仅由 owner 人工决定是否执行本地验证命令。",
            "rerun_safe_dashboard_build",
            f"python -m trading_core.cli build-and-audit-a-share-owner-dashboard --as-of-date {as_of_date} --mode build_dashboard_from_existing_run",
        ),
        _item("WAIT-HISTORY", "P4", "history", "检查是否需要等待更多历史数据", "如果趋势样本不足，记录并等待更多日度观察。", "wait_for_more_history", None),
    ]
    blocking = validate_checklist(items)
    return {
        "checklist_id": "A-SHARE-OWNER-SAFE-ACTION-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "issue_count": issue_catalog.get("issue_count", 0),
        "items": items,
        "safe_action_count": len(items),
        "automatic_action_count": len([item for item in items if item["allowed_to_execute_automatically"]]),
        "blocking_reasons": blocking,
    }


def validate_checklist(items: list[dict[str, Any]]) -> list[str]:
    blocking: list[str] = []
    for item in items:
        action = item.get("safe_action_type")
        if action in FORBIDDEN_ACTION_TYPES:
            blocking.append(f"forbidden_action_type:{action}")
        if action not in ALLOWED_SAFE_ACTION_TYPES:
            blocking.append(f"unknown_safe_action_type:{action}")
        if item.get("allowed_to_execute_automatically") is not False:
            blocking.append(f"automatic_action_not_false:{item.get('item_id')}")
    return blocking


def _item(item_id: str, priority: str, category: str, title: str, description: str, action_type: str, command: str | None) -> dict[str, Any]:
    return {
        "checklist_id": "A-SHARE-OWNER-SAFE-ACTION-CHECKLIST",
        "item_id": item_id,
        "priority": priority,
        "category": category,
        "title_zh": title,
        "description_zh": description,
        "safe_action_type": action_type,
        "command_if_any": command,
        "expected_output": "Audit stays passed, source trace complete, boundary clean.",
        "manual_review_required": True,
        "allowed_to_execute_automatically": False,
        "disallowed_actions": list(DISALLOWED_ACTIONS),
        "status": "pending_manual_review",
    }
