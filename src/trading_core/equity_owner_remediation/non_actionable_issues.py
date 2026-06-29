"""Non-actionable remediation items."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_remediation.remediation_config import TARGET_VERSION


def build_non_actionable_issue_list(*, as_of_date: str, payloads: dict[str, Any], issue_catalog: dict[str, Any]) -> dict[str, Any]:
    run_history = payloads.get("run_history_snapshot", {})
    items: list[dict[str, Any]] = []
    if int(run_history.get("run_history_observation_count", 0)) < int(run_history.get("minimum_history_observations", 3)):
        items.append(
            _item(
                "insufficient_history_for_trends",
                "运行历史观察数不足，不应立即操作。",
                "未来日度 monitoring 记录达到 minimum_history_observations 后可恢复趋势判断。",
                "达到阈值后仍无法生成趋势，或趋势类 warning 变成 triggered。",
            )
        )
    items.append(
        _item(
            "performance_not_yet_observed",
            "首日或早期组合表现样本不足，只能记录观察。",
            "积累多日 tracking 和 performance artifacts。",
            "多日表现审计失败或出现 blocking boundary issue。",
        )
    )
    for issue in issue_catalog.get("issues", []):
        if issue.get("known_non_blocking"):
            items.append(
                _item(
                    str(issue["issue_code"]),
                    "上游 audit 已通过，当前按已知非阻塞事项记录。",
                    "后续数据刷新或更多历史样本可能自然消除该 warning。",
                    "同一 warning 重复并伴随 audit failure 或 boundary failure。",
                )
            )
    return {
        "list_id": "A-SHARE-OWNER-REMEDIATION-NON-ACTIONABLE-ISSUE-LIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "items": list({item["issue_code"]: item for item in items}.values()),
    }


def _item(code: str, why: str, future: str, escalation: str) -> dict[str, str]:
    return {
        "issue_code": code,
        "why_no_immediate_action_is_required": why,
        "what_future_data_will_resolve_it": future,
        "when_it_should_be_escalated": escalation,
    }
