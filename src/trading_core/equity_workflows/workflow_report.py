"""Markdown reports for A-share daily research workflow orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_workflows.workflow_config import RECOMMENDED_NEXT_VERSION, WORKFLOW_REPORTS


def write_workflow_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "workflow_summary_report": output_dir / WORKFLOW_REPORTS["workflow_summary_report"],
        "workflow_stage_report": output_dir / WORKFLOW_REPORTS["workflow_stage_report"],
        "workflow_source_trace_report": output_dir / WORKFLOW_REPORTS["workflow_source_trace_report"],
    }
    reports["workflow_summary_report"].write_text(render_workflow_summary(payload), encoding="utf-8")
    reports["workflow_stage_report"].write_text(render_stage_report(payload), encoding="utf-8")
    reports["workflow_source_trace_report"].write_text(render_source_trace_report(payload), encoding="utf-8")
    return {key: str(path) for key, path in reports.items()}


def render_workflow_summary(payload: dict[str, Any]) -> str:
    summary = payload["workflow_summary"]
    run_manifest = payload["workflow_run_manifest"]
    lines = [
        "# A 股每日研究工作流汇总",
        "",
        f"- 日期: {summary['as_of_date']}",
        f"- 模式: {summary['mode']}",
        f"- 总体状态: {'通过' if summary['overall_passed'] else '未通过'}",
        f"- research_only: {str(summary['research_only']).lower()}",
        f"- virtual_only: {str(summary['virtual_only']).lower()}",
        f"- not_order_instruction: {str(summary['not_order_instruction']).lower()}",
        f"- not_real_trade: {str(summary['not_real_trade']).lower()}",
        f"- not_profit_guarantee: {str(summary['not_profit_guarantee']).lower()}",
        f"- not_live_trading_ready: {str(summary['not_live_trading_ready']).lower()}",
        "",
        "## 阶段状态",
        "",
        "| 阶段 | 名称 | 状态 | 警告 | 阻断 |",
        "|---|---|---|---:|---:|",
    ]
    for stage in run_manifest["stages"]:
        lines.append(
            f"| {stage['stage_id']} | {stage['stage_name']} | {stage['status']} | {len(stage.get('warnings', []))} | {len(stage.get('blocking_reasons', []))} |"
        )
    lines.extend(
        [
            "",
            "## 关键产物",
            "",
            f"- briefing: {summary['briefing_path']}",
            f"- tracking: {summary['tracking_path']}",
            f"- workflow source trace complete: {str(summary['source_trace_complete']).lower()}",
            f"- upstream audits passed: {str(summary['upstream_audits_passed']).lower()}",
            "",
            "## 候选池与组合",
            "",
            f"- candidate_counts: {summary['candidate_counts']}",
            f"- portfolio_navs: {summary['portfolio_navs']}",
            "",
            "## 警告与阻断",
            "",
            f"- warnings: {summary['warnings']}",
            f"- blocking_reasons: {summary['blocking_reasons']}",
            "",
            "## 边界摘要",
            "",
            "- 本阶段只做 A 股研究工作流编排。",
            "- 不调用旧 run-daily。",
            "- official forward dry-run 状态保持不变。",
            "- day2_executed: false。",
            "- broker_connected: false。",
            "- real_orders_placed: false。",
            "- buy_sell_signals_generated: false。",
            "- order_preview_generated: false。",
            "- model_profit_guaranteed: false。",
            "- live_trading_ready: false。",
            "",
            f"下一建议版本: {RECOMMENDED_NEXT_VERSION}",
            "",
        ]
    )
    return "\n".join(lines)


def render_stage_report(payload: dict[str, Any]) -> str:
    lines = [
        "# A-Share Daily Workflow Stage Report",
        "",
        "| order | stage_id | status | command | duration_seconds |",
        "|---:|---|---|---|---:|",
    ]
    for stage in payload["workflow_run_manifest"]["stages"]:
        command = str(stage["command"]).replace("|", "\\|")
        lines.append(f"| {stage['stage_order']} | {stage['stage_id']} | {stage['status']} | {command} | {stage['duration_seconds']:.6f} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "- Workflow orchestration only.",
            "- Old run-daily was not called.",
            "- No broker connection was made.",
            "- No real orders were placed.",
            "- No order preview was generated.",
            "- Not live trading ready.",
            "",
        ]
    )
    return "\n".join(lines)


def render_source_trace_report(payload: dict[str, Any]) -> str:
    trace = payload["workflow_source_trace"]
    lines = [
        "# A-Share Daily Workflow Source Trace",
        "",
        f"- trace_id: {trace['trace_id']}",
        f"- as_of_date: {trace['as_of_date']}",
        f"- mode: {trace['mode']}",
        f"- source_trace_complete: {str(trace['source_trace_complete']).lower()}",
        f"- forbidden_path_hits: {trace['forbidden_path_hits']}",
        "",
        "| path | exists | sha256 |",
        "|---|---:|---|",
    ]
    for record in trace["sources"]:
        lines.append(f"| {record['path']} | {str(record['exists']).lower()} | {record['sha256'] or ''} |")
    lines.extend(
        [
            "",
            "## Stage Commands",
            "",
            "| stage | status | command |",
            "|---|---|---|",
        ]
    )
    for command in trace["stage_commands"]:
        text = str(command["command"]).replace("|", "\\|")
        lines.append(f"| {command['stage_id']} | {command['status']} | {text} |")
    lines.append("")
    return "\n".join(lines)


def render_workflow_audit(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Daily Workflow Audit",
            "",
            f"- target_version: {payload['target_version']}",
            f"- as_of_date: {payload['as_of_date']}",
            f"- mode: {payload['mode']}",
            f"- overall_passed: {str(payload['overall_passed']).lower()}",
            f"- blocking_reasons: {payload['blocking_reasons']}",
            f"- warnings: {len(payload['warnings'])}",
            f"- stage_counts: {payload['stage_counts']}",
            f"- required_stage_status: {payload['required_stage_status']}",
            "",
            "## Boundary",
            "- Workflow orchestration only.",
            "- call_old_run_daily: false.",
            "- official_forward_dry_run_status_unchanged: true.",
            "- day2_executed: false.",
            "- run_daily_called: false.",
            "- broker_connected: false.",
            "- real_orders_placed: false.",
            "- buy_sell_signals_generated: false.",
            "- order_preview_generated: false.",
            "- model_profit_guaranteed: false.",
            "- live_trading_ready: false.",
            "",
            f"Recommended next version: {payload['recommended_next_version']}",
            "",
        ]
    )
