"""Markdown reports for build-output ops refresh."""

from __future__ import annotations


def render_ops_refresh_report(*, as_of_date: str, payloads: dict, summary: dict) -> str:
    monitoring = payloads["build_output_monitoring_refresh"]
    remediation = payloads["build_output_remediation_refresh"]
    ops_center = payloads["build_output_ops_center_refresh"]
    history = payloads["build_output_ops_history_refresh"]
    comparison = payloads["original_ops_vs_build_output_ops_comparison"]
    navigation = payloads["build_output_ops_artifact_navigation"]
    lines = [
        "# A 股 Build Output Ops Refresh",
        "",
        "## 1. Build Output Ops Refresh 总览",
        "",
        f"- 日期: {as_of_date}",
        f"- source_workflow_mode: {summary.get('source_workflow_mode')}",
        f"- overall_status: {summary.get('overall_status')}",
        f"- overall_passed: {summary.get('overall_passed')}",
        "",
        "## 2. 输入审计状态",
        "",
        f"- build_output_dashboard_audit_passed: {summary.get('build_output_dashboard_audit_passed')}",
        f"- repeatability_audit_passed: {summary.get('repeatability_audit_passed')}",
        f"- gated_build_audit_passed: {summary.get('gated_build_audit_passed')}",
        f"- original_monitoring_audit_passed: {summary.get('original_monitoring_audit_passed')}",
        f"- original_remediation_audit_passed: {summary.get('original_remediation_audit_passed')}",
        f"- original_ops_center_audit_passed: {summary.get('original_ops_center_audit_passed')}",
        "",
        "## 3. Build-output dashboard 状态",
        "",
        f"- business_output_drift_count: {summary.get('business_output_drift_count')}",
        f"- protected_path_modifications_detected: {summary.get('protected_path_modifications_detected')}",
        "",
        "## 4. Monitoring Refresh",
        "",
        f"- monitoring_refresh_performed: {monitoring.get('monitoring_refresh_performed')}",
        f"- warning_alert_count: {monitoring.get('warning_alert_count')}",
        f"- external_notifications_sent: {monitoring.get('external_notifications_sent')}",
        "",
        "## 5. Remediation Refresh",
        "",
        f"- remediation_refresh_performed: {remediation.get('remediation_refresh_performed')}",
        f"- execute_remediation_actions: {remediation.get('execute_remediation_actions')}",
        "",
        "## 6. Ops Center Refresh",
        "",
        f"- health_score: {ops_center.get('health_score')}",
        f"- health_grade: {ops_center.get('health_grade')}",
        f"- automatic_action_count: {ops_center.get('automatic_action_count')}",
        "",
        "## 7. Ops History Refresh",
        "",
        f"- ops_history_refresh_performed: {history.get('ops_history_refresh_performed')}",
        f"- synthetic_history_used: {history.get('synthetic_history_used')}",
        f"- future_dates_used: {history.get('future_dates_used')}",
        "",
        "## 8. Issue / Warning / Safe Action 摘要",
        "",
        f"- blocking_reasons: {summary.get('blocking_reasons')}",
        f"- warnings: {summary.get('warnings')}",
        f"- automatic_action_count: {summary.get('automatic_action_count')}",
        "",
        "## 9. Original Ops vs Build-output Ops 对比",
        "",
        f"- comparison_completed: {comparison.get('comparison_completed')}",
        f"- expected_source_mode_differences: {comparison.get('expected_source_mode_differences')}",
        f"- unexpected_business_output_or_boundary_differences: {comparison.get('unexpected_business_output_or_boundary_differences')}",
        "",
        "## 10. Artifact Navigation",
        "",
    ]
    for entry in navigation.get("entries", []):
        lines.append(f"- {entry.get('artifact_id')}: {entry.get('path')} exists={entry.get('exists')}")
    lines.extend([
        "",
        "## 11. 安全边界",
        "",
        "- research-only / virtual-only",
        "- no broker connection",
        "- no real account read",
        "- no real orders",
        "- no order preview",
        "- no public network refresh",
        "- no full_research_run",
        "- no build_from_existing_data rerun",
        "- no remediation action execution",
        "- no external notifications",
        "- no old run-daily",
        "- ops refresh output is not a trade instruction",
        "",
        "## 12. 下一步建议",
        "",
        f"- recommended_next_version: {summary.get('recommended_next_version')}",
        "",
        "## 13. 免责声明",
        "",
        "本 build-output ops refresh 仅用于研究型虚拟流程的运维刷新和边界检查，不构成投资建议，不授权任何交易动作，不承诺收益，也不代表 live trading ready。",
        "",
    ])
    return "\n".join(lines)


def render_monitoring_report(*, monitoring: dict, alert: dict) -> str:
    return "\n".join([
        "# A 股 Build Output Monitoring Refresh",
        "",
        "## Build-output warning context",
        f"- build_output_warning_count: {monitoring.get('build_output_warning_count')}",
        "",
        "## Alert Summary",
        f"- critical_alert_count: {alert.get('critical_alert_count')}",
        f"- warning_alert_count: {alert.get('warning_alert_count')}",
        f"- known_non_blocking_alert_count: {alert.get('known_non_blocking_alert_count')}",
        f"- external_notifications_sent: {alert.get('external_notifications_sent')}",
        "",
        "## Boundary",
        "- local monitoring refresh only",
        "- non-trading interpretation",
        "",
    ])


def render_remediation_report(*, remediation: dict, safe_action: dict) -> str:
    return "\n".join([
        "# A 股 Build Output Remediation Refresh",
        "",
        "## Safe Owner Actions",
        f"- safe_action_count: {safe_action.get('safe_action_count')}",
        f"- automatic_action_count: {safe_action.get('automatic_action_count')}",
        "",
        "## Manual Review Items",
        f"- manual_review_count: {safe_action.get('manual_review_count')}",
        "",
        "## Non-actionable Items",
        f"- status: {remediation.get('status')}",
        "",
        "## Protected Path Interpretation",
        f"- protected_path_modifications_detected: {remediation.get('protected_path_modifications_detected')}",
        "",
        "## Boundary",
        "- no remediation action executed",
        "- no external notifications",
        "",
    ])


def render_ops_center_report(*, ops_center: dict, module_matrix: dict, issue: dict, action: dict, next_steps: dict) -> str:
    return "\n".join([
        "# A 股 Build Output Ops Center Refresh",
        "",
        "## Health Score",
        f"- score: {ops_center.get('health_score')}",
        f"- grade: {ops_center.get('health_grade')}",
        "",
        "## Module Status",
        f"- module_count: {len(module_matrix.get('rows', []))}",
        "",
        "## Issue Summary",
        f"- blocking_issue_count: {issue.get('blocking_issue_count')}",
        f"- warning_issue_count: {issue.get('warning_issue_count')}",
        "",
        "## Action Summary",
        f"- safe_action_count: {action.get('safe_action_count')}",
        f"- automatic_action_count: {action.get('automatic_action_count')}",
        "",
        "## Owner Next Steps",
        f"- review_today: {next_steps.get('review_today')}",
        "",
        "## Boundary State",
        "- research-only / virtual-only",
        "- no broker",
        "- no real orders",
        "",
    ])


def render_comparison_report(*, comparison: dict) -> str:
    return "\n".join([
        "# A 股 Original Ops vs Build Output Ops",
        "",
        f"- comparison_completed: {comparison.get('comparison_completed')}",
        f"- original_source_workflow_mode: {comparison.get('original_source_workflow_mode')}",
        f"- build_output_source_workflow_mode: {comparison.get('build_output_source_workflow_mode')}",
        f"- expected_source_mode_differences: {comparison.get('expected_source_mode_differences')}",
        f"- unexpected_business_output_or_boundary_differences: {comparison.get('unexpected_business_output_or_boundary_differences')}",
        "",
    ])


def render_source_trace_report(*, source_trace: dict) -> str:
    lines = [
        "# A 股 Build Output Ops Source Trace",
        "",
        f"- source_trace_complete: {source_trace.get('source_trace_complete')}",
        f"- source_trace_hashes_match: {source_trace.get('source_trace_hashes_match')}",
        "",
    ]
    for entry in source_trace.get("entries", []):
        sha = entry.get("sha256") or "N/A"
        lines.append(f"- {entry.get('artifact_id')}: exists={entry.get('exists')} sha256={sha[-12:]}")
    lines.append("")
    return "\n".join(lines)


def render_audit_report(audit: dict) -> str:
    lines = [
        "# A 股 Build Output Ops Refresh Audit",
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
    lines.extend(["", "## Refresh Checks", ""])
    for key, value in audit.get("refresh_checks", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Boundary", ""])
    for key, value in audit.get("boundary", {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)

