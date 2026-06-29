"""Markdown reports for build repeatability."""

from __future__ import annotations


def render_repeatability_report(
    *,
    as_of_date: str,
    execution_record: dict,
    comparison: dict,
    drift_summary: dict,
    protected_check: dict,
    warning_comparison: dict,
    source_trace: dict,
    boundary: dict,
    summary: dict,
) -> str:
    lines = [
        "# A 股 build_from_existing_data 重复性验证报告",
        "",
        "## 1. Repeatability 总览",
        "",
        f"- 日期: {as_of_date}",
        f"- workflow mode: {summary.get('workflow_mode')}",
        f"- overall_passed: {summary.get('overall_passed')}",
        f"- blocking_reasons: {summary.get('blocking_reasons')}",
        "",
        "## 2. 重复 build 执行结果",
        "",
        f"- command_executed: {execution_record.get('command_executed')}",
        f"- exit_code: {execution_record.get('exit_code')}",
        f"- status: {execution_record.get('status')}",
        f"- workflow_audit_overall_passed: {execution_record.get('workflow_audit_overall_passed')}",
        "",
        "## 3. Build-vs-Build 对比",
        "",
        f"- comparison_completed: {comparison.get('comparison_completed')}",
        f"- first_artifact_count: {comparison.get('first_artifact_count')}",
        f"- second_artifact_count: {comparison.get('second_artifact_count')}",
        f"- missing_required_artifact_count: {comparison.get('missing_required_artifact_count')}",
        "",
        "## 4. Drift 分类",
        "",
        f"- timestamp_only_drift_count: {comparison.get('timestamp_only_drift_count')}",
        f"- metadata_hash_drift_count: {comparison.get('metadata_hash_drift_count')}",
        f"- business_output_drift_count: {comparison.get('business_output_drift_count')}",
        f"- drift_categories_found: {drift_summary.get('drift_categories_found')}",
        "",
        "## 5. 受保护路径检查",
        "",
        f"- preexisting_protected_paths: {protected_check.get('preexisting_protected_paths')}",
        f"- protected_path_modifications_detected: {protected_check.get('protected_path_modifications_detected')}",
        f"- protected_files_modified: {protected_check.get('protected_files_modified')}",
        f"- protected_files_created: {protected_check.get('protected_files_created')}",
        f"- protected_files_deleted: {protected_check.get('protected_files_deleted')}",
        "",
        "## 6. Warning 对比",
        "",
        f"- first_warning_count: {warning_comparison.get('first_warning_count')}",
        f"- second_warning_count: {warning_comparison.get('second_warning_count')}",
        f"- new_warnings: {warning_comparison.get('new_warnings')}",
        "",
        "## 7. Source Trace 稳定性",
        "",
        f"- source_trace_complete: {source_trace.get('source_trace_complete')}",
        f"- forbidden_generated_sources: {source_trace.get('forbidden_generated_sources')}",
        "",
        "## 8. Boundary 稳定性",
        "",
        f"- old_run_daily_called: {boundary.get('old_run_daily_called')}",
        f"- broker_connected: {boundary.get('broker_connected')}",
        f"- real_orders_placed: {boundary.get('real_orders_placed')}",
        f"- order_preview_generated: {boundary.get('order_preview_generated')}",
        f"- buy_sell_signals_generated: {boundary.get('buy_sell_signals_generated')}",
        "",
        "## 9. 下一步建议",
        "",
        f"- recommended_next_version: {summary.get('recommended_next_version')}",
        "",
        "## 10. 免责声明",
        "",
        "本报告只用于研究流程重复性验证和差异稳定性检查。",
        "本阶段不是实盘，不连接券商，不读取真实账户，不下单，不生成订单预览，不把重复性验证解释为交易动作。",
        "本报告不构成投资建议，不声称保证盈利，不声称 live trading ready。",
        "",
    ]
    return "\n".join(lines)


def render_build_vs_build_report(*, as_of_date: str, comparison: dict) -> str:
    return "\n".join([
        "# A 股 Build-vs-Build 对比",
        "",
        f"- 日期: {as_of_date}",
        f"- comparison_completed: {comparison.get('comparison_completed')}",
        f"- timestamp_only_drift_count: {comparison.get('timestamp_only_drift_count')}",
        f"- metadata_hash_drift_count: {comparison.get('metadata_hash_drift_count')}",
        f"- business_output_drift_count: {comparison.get('business_output_drift_count')}",
        f"- missing_required_artifact_count: {comparison.get('missing_required_artifact_count')}",
        f"- boundary_drift: {comparison.get('boundary_drift')}",
        f"- protected_path_drift: {comparison.get('protected_path_drift')}",
        f"- source_trace_drift: {comparison.get('source_trace_drift')}",
        f"- blocking_reasons: {comparison.get('blocking_reasons')}",
        "",
        "时间戳类 drift 允许作为非 blocking 解释项；业务输出 drift 默认 blocking。",
        "",
    ])


def render_drift_summary_report(*, as_of_date: str, drift_summary: dict) -> str:
    return "\n".join([
        "# A 股 Repeatability Drift Summary",
        "",
        f"- 日期: {as_of_date}",
        f"- overall_status: {drift_summary.get('overall_status')}",
        f"- drift_categories_found: {drift_summary.get('drift_categories_found')}",
        f"- timestamp_only_drift_count: {drift_summary.get('timestamp_only_drift_count')}",
        f"- metadata_hash_drift_count: {drift_summary.get('metadata_hash_drift_count')}",
        f"- business_output_drift_count: {drift_summary.get('business_output_drift_count')}",
        f"- blocking_reasons: {drift_summary.get('blocking_reasons')}",
        "",
    ])


def render_protected_path_report(*, as_of_date: str, protected_check: dict) -> str:
    return "\n".join([
        "# A 股受保护路径修改检查",
        "",
        f"- 日期: {as_of_date}",
        f"- preexisting_protected_paths_allowed: {protected_check.get('preexisting_protected_paths_allowed')}",
        f"- protected_path_modifications_detected: {protected_check.get('protected_path_modifications_detected')}",
        f"- preexisting_protected_paths: {protected_check.get('preexisting_protected_paths')}",
        f"- new_protected_paths_created: {protected_check.get('new_protected_paths_created')}",
        f"- protected_files_modified: {protected_check.get('protected_files_modified')}",
        f"- protected_files_created: {protected_check.get('protected_files_created')}",
        f"- protected_files_deleted: {protected_check.get('protected_files_deleted')}",
        "",
        "data/orders 或 data/trades 预先存在不等于本次生成或修改。",
        "本阶段只把本次新增、修改、删除受保护路径内容视为 blocking。",
        "",
    ])


def render_source_trace_report(*, as_of_date: str, source_trace: dict) -> str:
    lines = [
        "# A 股 Repeatability Source Trace",
        "",
        f"- 日期: {as_of_date}",
        f"- source_trace_complete: {source_trace.get('source_trace_complete')}",
        f"- forbidden_generated_sources: {source_trace.get('forbidden_generated_sources')}",
        "",
        "## Boundary Assumptions",
        "",
    ]
    for item in source_trace.get("boundary_assumptions", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Entries", ""])
    for entry in source_trace.get("entries", []):
        sha = entry.get("sha256") or "N/A"
        lines.append(f"- {entry.get('artifact_id')}: exists={entry.get('exists')} sha256={sha[-12:]}")
    lines.append("")
    return "\n".join(lines)

