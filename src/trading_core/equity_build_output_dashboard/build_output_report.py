"""Markdown reports for build-output owner dashboard."""

from __future__ import annotations


def render_owner_dashboard(*, as_of_date: str, cards: dict, comparison: dict, summary: dict) -> str:
    executive = cards["build_output_executive_status_card"]
    repeat = cards["build_output_repeatability_card"]
    protected = cards["build_output_protected_path_card"]
    warning = cards["build_output_warning_and_blocker_card"]
    navigation = cards["build_output_artifact_navigation"]
    lines = [
        "# A 股 Build Output Owner Dashboard",
        "",
        "## 1. 今日 Build Output 总览",
        "",
        f"- 日期: {as_of_date}",
        f"- source_workflow_mode: {executive.get('source_workflow_mode')}",
        f"- overall_status: {executive.get('overall_status')}",
        f"- build_output_available: {executive.get('build_output_available')}",
        "",
        "## 2. 数据刷新状态",
        "",
        f"- data_refresh_audit_passed: {cards['build_output_data_freshness_card'].get('data_refresh_audit_passed')}",
        "",
        "## 3. Build-from-existing-data Workflow 状态",
        "",
        f"- repeat_build_status: {cards['build_output_workflow_status_card'].get('repeat_build_status')}",
        f"- repeat_build_audit_passed: {cards['build_output_workflow_status_card'].get('repeat_build_audit_passed')}",
        "",
        "## 4. Repeatability 状态",
        "",
        f"- repeatability_audit_passed: {repeat.get('repeatability_audit_passed')}",
        f"- business_output_drift_count: {repeat.get('business_output_drift_count')}",
        f"- timestamp_only_drift_count: {repeat.get('timestamp_only_drift_count')}",
        f"- metadata_hash_drift_count: {repeat.get('metadata_hash_drift_count')}",
        "",
        "## 5. Protected Path 状态",
        "",
        f"- preexisting_protected_paths: {protected.get('preexisting_protected_paths')}",
        f"- protected_path_modifications_detected: {protected.get('protected_path_modifications_detected')}",
        "",
        "## 6. 研究产物导航",
        "",
    ]
    for entry in navigation.get("entries", []):
        lines.append(f"- {entry.get('artifact_id')}: {entry.get('path')} exists={entry.get('exists')}")
    lines.extend([
        "",
        "## 7. 候选 / 虚拟组合 / Benchmark / Performance / Attribution 摘要",
        "",
        f"- candidate_available: {cards['build_output_candidate_summary_card'].get('available')}",
        f"- portfolio_available: {cards['build_output_portfolio_summary_card'].get('available')}",
        f"- benchmark_available: {cards['build_output_benchmark_summary_card'].get('available')}",
        f"- performance_available: {cards['build_output_performance_summary_card'].get('available')}",
        f"- attribution_available: {cards['build_output_attribution_summary_card'].get('available')}",
        "",
        "## 8. Warning / Blocking",
        "",
        f"- blocking_count: {warning.get('blocking_count')}",
        f"- warning_count: {warning.get('warning_count')}",
        f"- blocking_reasons: {warning.get('blocking_reasons')}",
        "",
        "## 9. Validate Dashboard vs Build Dashboard 对比",
        "",
        f"- comparison_completed: {comparison.get('comparison_completed')}",
        f"- expected_source_mode_difference: {comparison.get('expected_source_mode_difference')}",
        "",
        "## 10. 安全边界",
        "",
        "- research-only / virtual-only",
        "- no broker connection",
        "- no real account read",
        "- no real orders",
        "- no order preview",
        "- no public network refresh",
        "- no full_research_run",
        "- no old run-daily",
        "- dashboard output is not a trade instruction",
        "",
        "## 11. 下一步建议",
        "",
        f"- recommended_next_version: {summary.get('recommended_next_version')}",
        "",
        "## 12. 免责声明",
        "",
        "本 dashboard 只用于研究流程可视化和边界检查，不构成投资建议，不授权任何交易动作，不承诺收益，也不代表 live trading ready。",
        "",
    ])
    return "\n".join(lines)


def render_compact_dashboard(*, as_of_date: str, summary: dict) -> str:
    text = (
        f"Build-output dashboard 日期 {as_of_date}。"
        f"source_workflow_mode={summary.get('source_workflow_mode')}，"
        f"overall_status={summary.get('overall_status')}。"
        f"gated_build_audit_passed={summary.get('gated_build_audit_passed')}，"
        f"repeatability_audit_passed={summary.get('repeatability_audit_passed')}，"
        f"business_output_drift_count={summary.get('business_output_drift_count')}。"
        f"protected_path_modifications_detected={summary.get('protected_path_modifications_detected')}，"
        f"blocking_reasons={summary.get('blocking_reasons')}，warnings={len(summary.get('warnings', []))}。"
        f"下一步：{summary.get('recommended_next_version')}。"
        "边界：research-only、virtual-only、no broker、no real orders、no order preview、no old run-daily、dashboard is not a trade instruction。"
    )
    return text[:1200]


def render_navigation_report(*, navigation: dict) -> str:
    lines = ["# A 股 Build Output Artifact Navigation", ""]
    for entry in navigation.get("entries", []):
        lines.append(f"- {entry.get('artifact_id')}: {entry.get('path')} exists={entry.get('exists')}")
    lines.append("")
    return "\n".join(lines)


def render_repeatability_card_report(*, repeatability_card: dict) -> str:
    return "\n".join([
        "# A 股 Build Output Repeatability Card",
        "",
        f"- repeatability_audit_passed: {repeatability_card.get('repeatability_audit_passed')}",
        f"- business_output_drift_count: {repeatability_card.get('business_output_drift_count')}",
        f"- timestamp_only_drift_count: {repeatability_card.get('timestamp_only_drift_count')}",
        f"- metadata_hash_drift_count: {repeatability_card.get('metadata_hash_drift_count')}",
        "",
    ])


def render_dashboard_comparison_report(*, comparison: dict) -> str:
    return "\n".join([
        "# A 股 Validate Dashboard vs Build Dashboard",
        "",
        f"- comparison_completed: {comparison.get('comparison_completed')}",
        f"- expected_source_mode_difference: {comparison.get('expected_source_mode_difference')}",
        f"- unexpected_business_output_differences: {comparison.get('unexpected_business_output_differences')}",
        f"- blocking_reasons: {comparison.get('blocking_reasons')}",
        "",
    ])


def render_source_trace_report(*, source_trace: dict) -> str:
    lines = [
        "# A 股 Build Output Dashboard Source Trace",
        "",
        f"- source_trace_complete: {source_trace.get('source_trace_complete')}",
        f"- fallback_decisions: {source_trace.get('fallback_decisions')}",
        "",
    ]
    for entry in source_trace.get("entries", []):
        sha = entry.get("sha256") or "N/A"
        lines.append(f"- {entry.get('artifact_id')}: exists={entry.get('exists')} sha256={sha[-12:]}")
    lines.append("")
    return "\n".join(lines)


def render_audit_report(audit: dict) -> str:
    lines = [
        "# A 股 Build Output Owner Dashboard Audit",
        "",
        f"- audit_id: {audit.get('audit_id')}",
        f"- overall_passed: {audit.get('overall_passed')}",
        f"- blocking_reasons: {audit.get('blocking_reasons')}",
        "",
        "## Input Checks",
        "",
    ]
    for key, value in audit.get("input_checks", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Dashboard Checks", ""])
    for key, value in audit.get("dashboard_checks", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Boundary", ""])
    for key, value in audit.get("boundary", {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)

