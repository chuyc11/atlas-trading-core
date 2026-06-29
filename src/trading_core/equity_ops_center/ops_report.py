"""Markdown reports for the daily ops center."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_ops_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "ops_command_center_report": output_dir / "A_SHARE_DAILY_OPS_COMMAND_CENTER.md",
        "ops_compact_report": output_dir / "A_SHARE_DAILY_OPS_COMPACT.md",
        "ops_module_status_report": output_dir / "A_SHARE_OPS_MODULE_STATUS.md",
        "ops_action_summary_report": output_dir / "A_SHARE_OPS_ACTION_SUMMARY.md",
        "ops_artifact_navigation_report": output_dir / "A_SHARE_OPS_ARTIFACT_NAVIGATION.md",
        "ops_source_trace_report": output_dir / "A_SHARE_OPS_SOURCE_TRACE.md",
    }
    reports["ops_command_center_report"].write_text(render_command_center(payload), encoding="utf-8")
    reports["ops_compact_report"].write_text(render_compact(payload), encoding="utf-8")
    reports["ops_module_status_report"].write_text(render_module_status(payload), encoding="utf-8")
    reports["ops_action_summary_report"].write_text(render_action_summary(payload), encoding="utf-8")
    reports["ops_artifact_navigation_report"].write_text(render_artifact_navigation(payload), encoding="utf-8")
    reports["ops_source_trace_report"].write_text(render_source_trace(payload), encoding="utf-8")
    return reports


def render_command_center(payload: dict[str, Any]) -> str:
    summary = payload["ops_summary"]
    health = payload["ops_health_score_card"]
    boundary = payload["ops_boundary_check"]
    lines = [
        "# A股 Daily Ops Command Center",
        "",
        "## 1. 今日 Ops 总览",
        f"- overall_status: {summary['overall_status']}",
        "",
        "## 2. Ops 健康评分",
        f"- score: {health['score']}",
        f"- grade: {health['grade']}",
        "",
        "## 3. 模块状态矩阵",
    ]
    lines.extend([f"- {row['module_id']}: {row['status']}" for row in payload["ops_module_status_matrix"].get("rows", [])])
    lines.extend(
        [
            "",
            "## 4. 数据刷新状态",
            "- 查看 data refresh audit 与 freshness/coverage artifacts。",
            "",
            "## 5. 当前日研究运行状态",
            "- 查看 current-day audit、readiness 与 warning summary。",
            "",
            "## 6. Owner Dashboard 状态",
            "- 查看 dashboard cards、manifest 与 boundary。",
            "",
            "## 7. Monitoring 状态",
            "- 查看 monitoring status card、alert summary 与 run history。",
            "",
            "## 8. Remediation 状态",
            "- 查看 remediation runbook、safe checklist 与 audit。",
            "",
            "## 9. Issue 摘要",
            f"- blocking={summary['blocking_issue_count']} warning={summary['warning_issue_count']} known_non_blocking={summary['known_non_blocking_issue_count']}",
            "",
            "## 10. Safe Action 摘要",
            f"- safe_action_count={summary['safe_action_count']} automatic_action_count={summary['automatic_action_count']}",
            "",
            "## 11. 关键产物导航",
            "- 查看 A_SHARE_OPS_ARTIFACT_NAVIGATION.md。",
            "",
            "## 12. 安全边界状态",
            f"- boundary passed: {boundary['overall_passed']}",
            "- 本阶段只聚合既有 artifacts，不执行刷新、研究流程、dashboard、monitoring 或 remediation action。",
            "",
            "## 13. 下一步建议",
            "- v0.8.6 应深化 run-history baseline 与趋势基线。",
            "",
            "## 14. 免责声明",
            "- 本报告是研究系统运维状态材料，不是交易系统。",
            "- 本阶段不连接券商，不读取真实账户，不下真实订单，不生成订单预览，不生成买卖信号。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_compact(payload: dict[str, Any]) -> str:
    summary = payload["ops_summary"]
    rows = payload["ops_module_status_matrix"].get("rows", [])
    module_status = ", ".join(f"{row['module_id']}={row['status']}" for row in rows)
    text = (
        f"今日Ops状态：{summary['overall_status']}。健康分：{summary['ops_health_score']}，等级：{summary['ops_health_grade']}。"
        f"模块：{module_status}。blocking={summary['blocking_issue_count']}，warning={summary['warning_issue_count']}，"
        f"safe_action={summary['safe_action_count']}。下一步：查看 remediation checklist 与 artifact navigation。"
        "边界：仅聚合既有artifacts，不执行刷新、研究流程、remediation action，不连接券商，不下单。"
    )
    return text[:1200] + "\n"


def render_module_status(payload: dict[str, Any]) -> str:
    lines = ["# A Share Ops Module Status", "", "| module | status | audit | warnings | blocking | boundary | source trace | summary |", "|---|---|---|---:|---:|---|---|---|"]
    for row in payload["ops_module_status_matrix"].get("rows", []):
        lines.append(f"| {row['module_id']} | {row['status']} | {row['audit_passed']} | {row['warning_count']} | {row['blocking_count']} | {row['boundary_clean']} | {row['source_trace_available']} | {row['summary_available']} |")
    return "\n".join(lines) + "\n"


def render_action_summary(payload: dict[str, Any]) -> str:
    action = payload["ops_action_summary"]
    lines = [
        "# A Share Ops Action Summary",
        "",
        f"- safe actions: {action['safe_action_count']}",
        f"- manual review items: {action['manual_review_count']}",
        f"- wait-for-history items: {action['wait_for_history_count']}",
        f"- developer follow-up items: {action['escalation_count']}",
        "- disallowed actions: broker connection, real account read, real order placement, order preview, buy/sell signal generation",
    ]
    return "\n".join(lines) + "\n"


def render_artifact_navigation(payload: dict[str, Any]) -> str:
    lines = ["# A Share Ops Artifact Navigation", ""]
    for row in payload["ops_artifact_navigation"].get("entries", []):
        lines.append(f"- {row['module_id']} / {row['artifact_id']} / {row['owner_priority']}: {row['path']} exists={row['exists']}")
    return "\n".join(lines) + "\n"


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["ops_source_trace"]
    lines = ["# A Share Ops Source Trace", "", f"- source trace complete: {trace.get('source_trace_complete')}", ""]
    for group in ["source_artifacts", "output_artifacts"]:
        lines.extend([f"## {group}", ""])
        for row in trace.get(group, []):
            lines.append(f"- {row.get('artifact_id')} | {row.get('path')} | exists={row.get('exists')} | sha256={row.get('sha256')}")
        lines.append("")
    return "\n".join(lines)


def render_audit(audit: dict[str, Any]) -> str:
    lines = [
        "# A Share Daily Ops Center Audit",
        "",
        f"- Overall passed: {audit.get('overall_passed')}",
        f"- Blocking reasons: {_join(audit.get('blocking_reasons', []))}",
        f"- Warning count: {len(audit.get('warnings', []))}",
        f"- Recommended next version: {audit.get('recommended_next_version')}",
        "",
        "## Checks",
    ]
    for key, value in audit.get("checks", {}).items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) + "\n"


def _join(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values) if values else "None"
