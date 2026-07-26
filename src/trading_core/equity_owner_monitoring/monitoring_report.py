"""Markdown reports for owner monitoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_monitoring_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "owner_monitoring_summary_report": output_dir / "A_SHARE_OWNER_MONITORING_SUMMARY.md",
        "owner_alert_summary_report": output_dir / "A_SHARE_OWNER_ALERT_SUMMARY.md",
        "run_history_summary_report": output_dir / "A_SHARE_RUN_HISTORY_SUMMARY.md",
        "warning_trend_summary_report": output_dir / "A_SHARE_WARNING_TREND_SUMMARY.md",
        "monitoring_source_trace_report": output_dir / "A_SHARE_MONITORING_SOURCE_TRACE.md",
    }
    reports["owner_monitoring_summary_report"].write_text(render_monitoring_summary(payload), encoding="utf-8")
    reports["owner_alert_summary_report"].write_text(render_alert_summary(payload), encoding="utf-8")
    reports["run_history_summary_report"].write_text(render_run_history_summary(payload), encoding="utf-8")
    reports["warning_trend_summary_report"].write_text(render_warning_trend_summary(payload), encoding="utf-8")
    reports["monitoring_source_trace_report"].write_text(render_source_trace(payload), encoding="utf-8")
    return reports


def render_monitoring_summary(payload: dict[str, Any]) -> str:
    status = payload["monitoring_status_card"]
    _alerts = payload["owner_alert_summary_card"]
    warning = payload["warning_trend_snapshot"]
    blocking = payload["blocking_trend_snapshot"]
    provider = payload["provider_health_trend_snapshot"]
    workflow = payload["workflow_health_trend_snapshot"]
    dashboard = payload["dashboard_health_trend_snapshot"]
    boundary = payload["monitoring_boundary_check"]
    lines = [
        "# A股 owner monitoring summary",
        "",
        "## 1. 今日监控总览",
        f"- 监控状态: {status['overall_monitoring_status']}",
        f"- 运行历史观察数: {status['run_history_observation_count']}",
        f"- 趋势分析可用: {status['trend_analysis_available']}",
        "",
        "## 2. 运行历史状态",
        f"- 当前 warning 数: {status['warning_count']}",
        f"- 当前 blocking 数: {status['blocking_count']}",
        "",
        "## 3. Alert 状态",
        f"- critical alerts: {status['critical_alert_count']}",
        f"- warning alerts: {status['warning_alert_count']}",
        f"- known non-blocking alerts: {status['known_non_blocking_alert_count']}",
        f"- external notifications sent: {status['external_notifications_sent']}",
        "",
        "## 4. Warning 趋势",
        f"- trend status: {warning['trend_status']}",
        f"- current warnings: {warning['warning_count_current']}",
        "",
        "## 5. Blocking 趋势",
        f"- trend status: {blocking['trend_status']}",
        f"- current blockers: {blocking['blocking_count_current']}",
        "",
        "## 6. Provider 健康趋势",
        f"- current status: {provider['current_status']}",
        f"- trend status: {provider['trend_status']}",
        "",
        "## 7. Workflow 健康趋势",
        f"- current status: {workflow['current_status']}",
        f"- trend status: {workflow['trend_status']}",
        "",
        "## 8. Dashboard 健康趋势",
        f"- current status: {dashboard['current_status']}",
        f"- trend status: {dashboard['trend_status']}",
        "",
        "## 9. 本地 alert 事件",
    ]
    lines.extend([f"- {event['rule_id']}: {event['status']} / {event['severity']}" for event in payload["alert_event_log"].get("events", [])])
    lines.extend(
        [
            "",
            "## 10. 安全边界状态",
            f"- boundary passed: {boundary['overall_passed']}",
            f"- broker connected: {boundary['broker_connected']}",
            f"- real orders placed: {boundary['real_orders_placed']}",
            f"- old run daily called: {boundary['old_run_daily_called']}",
            "",
            "## 11. 下一步建议",
            "- 继续积累运行历史；当观察数达到阈值后再判断 warning 与健康趋势。",
            "- v0.8.4 应把常见 warning 和失败状态整理成本地 remediation runbook 与安全 checklist。",
            "",
            "## 12. 免责声明",
            "- 本报告只用于研究系统健康监控，不是交易指令。",
            "- 本阶段不生成买卖信号，不连接券商，不读取真实账户，不下真实订单，不发送外部通知。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_alert_summary(payload: dict[str, Any]) -> str:
    card = payload["owner_alert_summary_card"]
    lines = [
        "# A Share Owner Alert Summary",
        "",
        f"- external notification status: sent={card['external_notifications_sent']}",
        "",
        "## critical alerts",
    ]
    lines.extend(_events(card["critical_alerts"]))
    lines.extend(["", "## warning alerts"])
    lines.extend(_events(card["warning_alerts"]))
    lines.extend(["", "## known non-blocking alerts"])
    lines.extend(_events(card["known_non_blocking_alerts"]))
    lines.extend(["", "## informational alerts"])
    lines.extend(_events(card["informational_alerts"]))
    lines.extend(["", "## owner action notes"])
    lines.extend([f"- {item}" for item in card["owner_action_notes"]])
    return "\n".join(lines) + "\n"


def render_run_history_summary(payload: dict[str, Any]) -> str:
    card = payload["run_history_summary_card"]
    lines = [
        "# A Share Run History Summary",
        "",
        f"- trend availability: {card['trend_analysis_available']}",
        "",
        "| as_of_date | overall status | warning count | blocking count | dashboard status |",
        "|---|---|---:|---:|---|",
    ]
    for row in card.get("history_table", []):
        lines.append(f"| {row['as_of_date']} | {row['overall_status']} | {row['warning_count']} | {row['blocking_count']} | {row['dashboard_status']} |")
    return "\n".join(lines) + "\n"


def render_warning_trend_summary(payload: dict[str, Any]) -> str:
    warning = payload["warning_trend_snapshot"]
    lines = [
        "# A Share Warning Trend Summary",
        "",
        f"- trend status: {warning['trend_status']}",
        f"- current warnings: {warning['warning_count_current']}",
        f"- previous warnings: {warning['warning_count_previous']}",
        "",
        "## current warnings",
    ]
    lines.extend([f"- {item}" for item in warning.get("current_warning_codes", [])] or ["- None"])
    lines.extend(["", "## known repeated warnings"])
    lines.extend([f"- {item}" for item in warning.get("repeated_warning_codes", [])] or ["- None"])
    lines.extend(["", "## new warnings"])
    lines.extend([f"- {item}" for item in warning.get("new_warning_codes", [])] or ["- None"])
    lines.extend(["", "## insufficient history explanation"])
    if warning.get("insufficient_history_for_trends"):
        lines.append("- 当前观察数不足，不编造 warning 趋势。")
    else:
        lines.append("- 趋势分析可用。")
    return "\n".join(lines) + "\n"


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["monitoring_source_trace"]
    lines = ["# A Share Monitoring Source Trace", "", f"- source trace complete: {trace.get('source_trace_complete')}", ""]
    for group in ["source_artifacts", "history_artifacts", "output_artifacts"]:
        lines.extend([f"## {group}", ""])
        for row in trace.get(group, []):
            lines.append(f"- {row.get('path')} | exists={row.get('exists')} | sha256={row.get('sha256')}")
        lines.append("")
    return "\n".join(lines)


def render_audit(audit: dict[str, Any]) -> str:
    lines = [
        "# A Share Owner Monitoring Audit",
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


def _events(events: list[dict[str, Any]]) -> list[str]:
    return [f"- {event['rule_id']}: {event['message']}" for event in events] or ["- None"]


def _join(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values) if values else "None"
