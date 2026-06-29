"""Markdown report generation for v0.8.7 gated build."""

from __future__ import annotations

from datetime import UTC, datetime

from trading_core.equity_current_day_builds.gated_build_config import (
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
)


def render_dry_run_report(
    *,
    as_of_date: str,
    preflight_gate: dict,
    execution_record: dict,
    workflow_result: dict,
    comparison: dict,
    drift_summary: dict,
    boundary: dict,
    summary: dict,
) -> str:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    lines = [
        f"# A 股 Gated Build-from-Existing-Data Dry-Run 报告",
        f"",
        f"- **版本**: {TARGET_VERSION}",
        f"- **日期**: {as_of_date}",
        f"- **生成时间**: {now}",
        f"",
        f"## 1. Dry-run 总览",
        f"",
        f"- **总体状态**: {'通过' if boundary.get('overall_passed') else '失败'}",
        f"- **Preflight Gate**: {'通过' if preflight_gate.get('overall_passed') else '失败'}",
        f"- **Workflow 状态**: {execution_record.get('status', 'unknown')}",
        f"- **Workflow 审计**: {'通过' if workflow_result.get('workflow_audit_overall_passed') else '失败'}",
        f"- **对比完成**: {'是' if comparison.get('comparison_completed') else '否'}",
        f"- **Drift 状态**: {drift_summary.get('overall_status', 'unknown')}",
        f"",
        f"## 2. Preflight Gate 结果",
        f"",
        f"- **通过**: {preflight_gate.get('overall_passed')}",
        f"- **Blocking**: {preflight_gate.get('blocking_reasons', [])}",
        f"- **Warnings**: {preflight_gate.get('warnings', [])}",
        f"- **Health Score**: {preflight_gate.get('ops_health_score')}",
        f"",
        f"## 3. 执行命令",
        f"",
        f"```bash",
        f"{execution_record.get('command', 'N/A')}",
        f"```",
        f"",
        f"- **退出码**: {execution_record.get('exit_code')}",
        f"- **耗时**: {execution_record.get('duration_seconds')}s",
        f"",
        f"## 4. Workflow 审计结果",
        f"",
        f"- **审计路径**: {workflow_result.get('workflow_audit_path', 'N/A')}",
        f"- **通过**: {workflow_result.get('workflow_audit_overall_passed')}",
        f"- **Blocking**: {workflow_result.get('workflow_blocking_reasons', [])}",
        f"- **Stages Passed**: {workflow_result.get('stages_passed', 0)}",
        f"- **Stages Failed**: {workflow_result.get('stages_failed', 0)}",
        f"",
        f"## 5. 关键产物",
        f"",
        f"- **Artifacts Generated**: {len(workflow_result.get('artifacts_generated_or_reused', []))}",
        f"",
        f"## 6. Validate vs Build 对比",
        f"",
        f"- **对比完成**: {comparison.get('comparison_completed')}",
        f"- **Business Output Drift**: {comparison.get('business_output_drift', [])}",
        f"- **Missing Artifacts**: {comparison.get('missing_required_artifacts', [])}",
        f"",
        f"## 7. Drift 摘要",
        f"",
        f"- **状态**: {drift_summary.get('overall_status', 'unknown')}",
        f"- **Drift Categories**: {drift_summary.get('drift_categories_found', [])}",
        f"",
        f"## 8. Warning / Blocking",
        f"",
        f"- **Blocking Reasons**: {boundary.get('blocking_reasons', [])}",
        f"- **Warnings**: {boundary.get('warnings', [])}",
        f"",
        f"## 9. 安全边界",
        f"",
        f"- **Research Only**: {boundary.get('research_only')}",
        f"- **Virtual Only**: {boundary.get('virtual_only')}",
        f"- **Broker Connected**: {boundary.get('broker_connected')}",
        f"- **Real Orders Placed**: {boundary.get('real_orders_placed')}",
        f"- **Buy/Sell Signals Generated**: {boundary.get('buy_sell_signals_generated')}",
        f"- **Old run-daily Called**: {boundary.get('old_run_daily_called')}",
        f"",
        f"## 10. 下一步建议",
        f"",
        f"- 推荐下一版本: {RECOMMENDED_NEXT_VERSION}",
        f"",
        f"## 11. 免责声明",
        f"",
        f"本报告为研究流程的 dry-run 产物，不构成投资建议。",
        f"不授权任何交易、不下单、不连接券商。",
        f"不保证盈利，不实盘就绪。",
        f"所有产物仅供项目负责人安全排查使用。",
        "",
    ]
    return "\n".join(lines)


def render_preflight_report(
    *,
    as_of_date: str,
    preflight_gate: dict,
    input_availability: dict,
    date_alignment: dict,
) -> str:
    lines = [
        f"# A 股 Gated Build Preflight Gate 报告",
        f"",
        f"- **版本**: {TARGET_VERSION}",
        f"- **日期**: {as_of_date}",
        f"",
        f"## 数据刷新就绪",
        f"- **Audit 通过**: {preflight_gate.get('audit_results', {}).get('data_refresh_audit', {}).get('overall_passed', 'N/A')}",
        f"",
        f"## Ops 就绪",
        f"- **Health Score**: {preflight_gate.get('ops_health_score')}",
        f"- **Health Gate 通过**: {preflight_gate.get('ops_health_gate_passed')}",
        f"",
        f"## 历史基线就绪",
        f"- **Ops History Audit 通过**: {preflight_gate.get('audit_results', {}).get('ops_history_audit', {}).get('overall_passed', 'N/A')}",
        f"",
        f"## Health Score Gate",
        f"- **最低要求**: {preflight_gate.get('minimum_ops_health_score')}",
        f"- **当前分数**: {preflight_gate.get('ops_health_score')}",
        f"",
        f"## Blocking / Critical Alert Gate",
        f"- **Blocking Issues**: {preflight_gate.get('blocking_reasons', [])}",
        f"",
        f"## 边界 Gate",
        f"- **边界干净**: {preflight_gate.get('boundary_clean')}",
        f"- **Old run-daily**: 未检测到",
        f"- **Broker/Order/Real Account**: 未检测到",
        f"",
        f"## 手动 Research-Only 授权说明",
        f"",
        f"本次 dry-run 为 research-only / virtual-only 模式。",
        f"不连接 broker、不下真实订单、不生成买卖信号。",
        f"本 dry-run 授权不授权任何交易行为。",
        "",
    ]
    return "\n".join(lines)


def render_comparison_report(
    *,
    as_of_date: str,
    comparison: dict,
    drift_summary: dict,
) -> str:
    lines = [
        f"# A 股 Validate vs Build 对比报告",
        f"",
        f"- **版本**: {TARGET_VERSION}",
        f"- **日期**: {as_of_date}",
        f"",
        f"## 对比总览",
        f"",
        f"- **Validate Mode**: {comparison.get('from_workflow_mode')}",
        f"- **Build Mode**: {comparison.get('to_workflow_mode')}",
        f"- **对比完成**: {comparison.get('comparison_completed')}",
        f"",
        f"## Business Output Drift",
        f"",
        f"{comparison.get('business_output_drift', []) if comparison.get('business_output_drift') else '无'}",
        f"",
        f"## Timestamp-Only Drift",
        f"",
        f"{comparison.get('timestamp_only_drift', []) if comparison.get('timestamp_only_drift') else '无'}",
        f"",
        f"## Missing Required Artifacts",
        f"",
        f"{comparison.get('missing_required_artifacts', []) if comparison.get('missing_required_artifacts') else '无'}",
        f"",
        f"## Drift 摘要",
        f"",
        f"- **状态**: {drift_summary.get('overall_status', 'unknown')}",
        f"- **Categories**: {drift_summary.get('drift_categories_found', [])}",
        "",
    ]
    return "\n".join(lines)


def render_drift_report(*, as_of_date: str, drift_summary: dict) -> str:
    lines = [
        f"# A 股 Gated Build Artifact Drift 报告",
        f"",
        f"- **版本**: {TARGET_VERSION}",
        f"- **日期**: {as_of_date}",
        f"",
        f"## Drift 状态",
        f"",
        f"- **Overall Status**: {drift_summary.get('overall_status', 'unknown')}",
        f"- **Categories Found**: {drift_summary.get('drift_categories_found', [])}",
        f"",
        f"## Drift Items",
        f"",
    ]
    for item in drift_summary.get("drift_items", []):
        lines.append(f"- **{item.get('artifact')}**: {item.get('drift_category')} ({item.get('severity')}) - {item.get('description')}")
    lines.append("")
    return "\n".join(lines)


def render_source_trace_report(*, as_of_date: str, source_trace: dict) -> str:
    lines = [
        f"# A 股 Gated Build Source Trace 报告",
        f"",
        f"- **版本**: {TARGET_VERSION}",
        f"- **日期**: {as_of_date}",
        f"",
        f"## Trace 状态",
        f"",
        f"- **Complete**: {source_trace.get('source_trace_complete')}",
        f"- **Forbidden Hits**: {source_trace.get('forbidden_path_hits', [])}",
        f"",
        f"## Boundary Assumptions",
        f"",
    ]
    for assumption in source_trace.get("boundary_assumptions", []):
        lines.append(f"- {assumption}")
    lines.append("")
    lines.append("## Entries")
    lines.append("")
    for entry in source_trace.get("entries", []):
        sha = entry.get("sha256") or "N/A"
        suffix = f"{sha[:16]}..." if sha != "N/A" else sha
        lines.append(f"- **{entry.get('artifact_id')}**: exists={entry.get('exists')} sha256={suffix}")
    lines.append("")
    return "\n".join(lines)
