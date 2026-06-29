"""Markdown reports for A-share current-day research runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import CURRENT_DAY_REPORTS, RECOMMENDED_NEXT_VERSION


def write_current_day_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "current_day_summary_report": output_dir / CURRENT_DAY_REPORTS["current_day_summary_report"],
        "current_day_readiness_report": output_dir / CURRENT_DAY_REPORTS["current_day_readiness_report"],
        "current_day_workflow_stage_report": output_dir / CURRENT_DAY_REPORTS["current_day_workflow_stage_report"],
        "current_day_warning_summary_report": output_dir / CURRENT_DAY_REPORTS["current_day_warning_summary_report"],
        "current_day_source_trace_report": output_dir / CURRENT_DAY_REPORTS["current_day_source_trace_report"],
    }
    reports["current_day_summary_report"].write_text(render_summary(payload), encoding="utf-8")
    reports["current_day_readiness_report"].write_text(render_readiness(payload), encoding="utf-8")
    reports["current_day_workflow_stage_report"].write_text(render_stage_report(payload), encoding="utf-8")
    reports["current_day_warning_summary_report"].write_text(render_warning_summary(payload), encoding="utf-8")
    reports["current_day_source_trace_report"].write_text(render_source_trace(payload), encoding="utf-8")
    return {key: str(path) for key, path in reports.items()}


def render_summary(payload: dict[str, Any]) -> str:
    summary = payload["current_day_summary"]
    stages = payload["current_day_stage_manifest"]["stages"]
    lines = [
        "# A 股当前交易日研究运行汇总",
        "",
        f"- 总体结论: {'通过' if summary['overall_passed'] else '未通过'}",
        f"- 数据日期: {summary['as_of_date']}",
        f"- resolved_as_of_date: {summary['resolved_as_of_date']}",
        f"- 运行模式: {summary['mode']}",
        f"- workflow_mode: {summary['workflow_mode']}",
        f"- 数据刷新审计状态: {'通过' if summary['data_refresh_audit_passed'] else '未通过'}",
        f"- 研究 workflow 审计状态: {'通过' if summary['workflow_audit_passed'] else '未通过'}",
        "",
        "## Stage Status",
        "",
        "| 阶段 | 名称 | 状态 | 警告 | 阻断 |",
        "|---|---|---|---:|---:|",
    ]
    for stage in stages:
        lines.append(f"| {stage['stage_id']} | {stage['stage_name']} | {stage['status']} | {len(stage.get('warnings', []))} | {len(stage.get('blocking_reasons', []))} |")
    lines.extend(
        [
            "",
            "## 关键产物路径",
            "",
        ]
    )
    for key, path in summary["key_artifacts"].items():
        lines.append(f"- {key}: {path}")
    lines.extend(
        [
            "",
            "## Warning Summary",
            "",
            f"- warning_count: {summary['warning_summary']['warning_count']}",
            f"- known_warnings_carried_forward: {summary['warning_summary']['known_warnings_carried_forward']}",
            f"- blocking_reasons: {summary['blocking_reasons']}",
            "",
            "## Boundary Summary",
            "",
            "- 仅运行 A 股当前交易日研究工作流。",
            "- 不连接券商，不读取真实账户，不下真实订单。",
            "- 不生成买卖信号，不生成订单预览。",
            "- 不调用旧 daily runner，不执行 official forward dry-run day2。",
            "- 研究输出不是交易指令，不代表可以实盘交易。",
            "",
            f"Recommended next version: {RECOMMENDED_NEXT_VERSION}",
            "",
        ]
    )
    return "\n".join(lines)


def render_readiness(payload: dict[str, Any]) -> str:
    readiness = payload["current_day_readiness"]
    lines = [
        "# Current Day Readiness",
        "",
        f"- overall_passed: {str(readiness['overall_passed']).lower()}",
        f"- data_refresh_audit_passed: {str(readiness['data_refresh_audit_passed']).lower()}",
        f"- critical_datasets_passed: {str(readiness['critical_datasets_passed']).lower()}",
        f"- schema_validation_passed: {str(readiness['schema_validation_passed']).lower()}",
        f"- freshness_validation_passed: {str(readiness['freshness_validation_passed']).lower()}",
        f"- coverage_validation_passed: {str(readiness['coverage_validation_passed']).lower()}",
        f"- workflow_cli_available: {str(readiness['workflow_cli_available']).lower()}",
        f"- workflow_mode_allowed: {str(readiness['workflow_mode_allowed']).lower()}",
        f"- blocking_reasons: {readiness['blocking_reasons']}",
        f"- warnings: {readiness['warnings']}",
        "",
    ]
    return "\n".join(lines)


def render_stage_report(payload: dict[str, Any]) -> str:
    lines = ["# Current Day Workflow Stage Report", "", "| order | stage_id | status | duration_seconds |", "|---:|---|---|---:|"]
    for stage in payload["current_day_stage_manifest"]["stages"]:
        lines.append(f"| {stage['stage_order']} | {stage['stage_id']} | {stage['status']} | {stage['duration_seconds']:.6f} |")
    lines.append("")
    return "\n".join(lines)


def render_warning_summary(payload: dict[str, Any]) -> str:
    warning_summary = payload["current_day_warning_summary"]
    lines = ["# Current Day Warning Summary", "", "| source | classification | warning |", "|---|---|---|"]
    for row in warning_summary["warnings"]:
        lines.append(f"| {row['source']} | {row['classification']} | {row['warning']} |")
    lines.append("")
    return "\n".join(lines)


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["current_day_source_trace"]
    lines = [
        "# Current Day Source Trace",
        "",
        f"- trace_id: {trace['trace_id']}",
        f"- source_trace_complete: {str(trace['source_trace_complete']).lower()}",
        f"- forbidden_path_hits: {trace['forbidden_path_hits']}",
        "",
        "| path | exists | sha256 |",
        "|---|---:|---|",
    ]
    for row in trace["source_artifacts"] + trace["output_artifacts"]:
        lines.append(f"| {row['path']} | {str(row['exists']).lower()} | {row['sha256'] or ''} |")
    lines.append("")
    return "\n".join(lines)


def render_current_day_audit(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Current-Day Research Run Audit",
            "",
            f"- target_version: {payload['target_version']}",
            f"- as_of_date: {payload['as_of_date']}",
            f"- resolved_as_of_date: {payload['resolved_as_of_date']}",
            f"- mode: {payload['mode']}",
            f"- workflow_mode: {payload['workflow_mode']}",
            f"- overall_passed: {str(payload['overall_passed']).lower()}",
            f"- blocking_reasons: {payload['blocking_reasons']}",
            f"- warnings: {len(payload['warnings'])}",
            "",
            "## Boundary",
            f"- run_daily_called: {str(payload['boundary']['run_daily_called']).lower()}",
            f"- old_run_daily_called: {str(payload['boundary']['old_run_daily_called']).lower()}",
            f"- day2_executed: {str(payload['boundary']['day2_executed']).lower()}",
            f"- broker_connected: {str(payload['boundary']['broker_connected']).lower()}",
            f"- real_orders_placed: {str(payload['boundary']['real_orders_placed']).lower()}",
            f"- buy_sell_signals_generated: {str(payload['boundary']['buy_sell_signals_generated']).lower()}",
            f"- order_preview_generated: {str(payload['boundary']['order_preview_generated']).lower()}",
            "",
            f"Recommended next version: {payload['recommended_next_version']}",
            "",
        ]
    )

