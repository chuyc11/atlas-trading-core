"""Markdown reports for owner daily pack."""

from __future__ import annotations


def render_decision_pack_report(*, as_of_date: str, payloads: dict, summary: dict) -> str:
    status = payloads["owner_daily_status_brief"]
    decision = payloads["owner_operations_decision_pack"]
    lines = [
        "# A 股 Owner Daily Decision Pack",
        "",
        "## 1. 今日 Owner Operations Decision Pack 总览",
        "",
        "这是 owner operations decision pack，不是投资决策包。",
        f"- 日期: {as_of_date}",
        f"- source_workflow_mode: {summary.get('source_workflow_mode')}",
        f"- overall_status: {summary.get('overall_status')}",
        "",
        "## 2. 今日系统状态",
        "",
        f"- ops_health_score: {status.get('ops_health_score')}",
        f"- ops_health_grade: {status.get('ops_health_grade')}",
        f"- business_output_drift_count: {status.get('business_output_drift_count')}",
        "",
        "## 3. 今日需要优先查看的事项",
        "",
        f"- {status.get('top_next_step_zh')}",
        "",
        "## 4. Build-output 研究产物摘要",
        "",
        f"- build_output_research_status: {payloads['research_output_digest'].get('build_output_research_status')}",
        "",
        "## 5. 候选跟踪摘要",
        "",
        f"- candidate_tracking_available: {payloads['candidate_tracking_digest'].get('candidate_tracking_available')}",
        "",
        "## 6. 虚拟组合 / 纸面账本摘要",
        "",
        f"- virtual_portfolio_available: {payloads['virtual_portfolio_digest'].get('virtual_portfolio_available')}",
        "",
        "## 7. Warning / Issue / Safe Action",
        "",
        f"- warning_count: {payloads['warning_issue_digest'].get('warning_count')}",
        f"- safe_action_count: {payloads['safe_action_digest'].get('safe_action_count')}",
        f"- automatic_action_count: {payloads['safe_action_digest'].get('automatic_action_count')}",
        "",
        "## 8. Protected Path 状态",
        "",
        f"- protected_path_modifications_detected: {payloads['protected_path_digest'].get('protected_path_modifications_detected')}",
        "",
        "## 9. Source Trace / Boundary 状态",
        "",
        f"- source_trace_complete: {payloads['source_trace_digest'].get('ops_source_trace_complete')}",
        f"- boundary_clean: {payloads['boundary_digest'].get('daily_pack_only')}",
        "",
        "## 10. Owner 下一步运维决策",
        "",
        f"- next_operational_decision: {decision.get('next_operational_decision')}",
        "",
        "## 11. 明确的非交易边界",
        "",
        "- research-only / virtual-only",
        "- no broker connection",
        "- no real account read",
        "- no real orders",
        "- no order preview",
        "- no public network refresh",
        "- no full_research_run",
        "- no build_from_existing_data rerun",
        "- no old run-daily",
        "- daily pack output is not a trade instruction",
        "",
        "## 12. 免责声明",
        "",
        "本报告不包含买入建议、卖出建议、下单建议或实盘调仓建议，不承诺收益，也不代表 live trading ready。",
        "",
    ]
    return "\n".join(lines)


def render_runbook_report(*, runbook: dict) -> str:
    lines = ["# A 股 Owner Daily Runbook", "", "## Daily Review Sequence", ""]
    for index, section in enumerate(runbook.get("sections", []), start=1):
        lines.append(f"{index}. {section}")
    lines.extend(["", "## Safe Audit-only Commands", ""])
    for command in runbook.get("safe_audit_only_commands", []):
        lines.append(f"- `{command}`")
    lines.extend(["", "## Manual Review Checklist", ""])
    for item in runbook.get("manual_review_checklist", []):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Developer Escalation Conditions",
        "",
        *[f"- {item}" for item in runbook.get("developer_escalation_conditions", [])],
        "",
        "## Known Non-blocking Items",
        "",
        *[f"- {item}" for item in runbook.get("known_non_blocking_items", [])],
        "",
        "## What Not To Do",
        "",
        *[f"- {item}" for item in runbook.get("what_not_to_do", [])],
        "",
    ])
    return "\n".join(lines)


def render_status_brief_report(*, status: dict) -> str:
    return "\n".join([
        "# A 股 Owner Daily Status Brief",
        "",
        f"- overall_status: {status.get('overall_status')}",
        f"- ops_health_score: {status.get('ops_health_score')}",
        f"- ops_health_grade: {status.get('ops_health_grade')}",
        f"- blocking_count: {status.get('blocking_count')}",
        f"- warning_count: {status.get('warning_count')}",
        f"- automatic_action_count: {status.get('automatic_action_count')}",
        f"- top_next_step_zh: {status.get('top_next_step_zh')}",
        "- not_trade_instruction: true",
        "",
    ])


def render_next_step_report(*, checklist: dict) -> str:
    lines = ["# A 股 Owner Next Step Checklist", ""]
    for key in ["do_now", "review_today", "wait_for_more_history", "developer_follow_up", "no_action_required"]:
        lines.extend([f"## {key}", ""])
        for item in checklist.get(key, []):
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def render_research_digest_report(*, digest: dict) -> str:
    return "\n".join([
        "# A 股 Research Output Digest",
        "",
        f"- source_workflow_mode: {digest.get('source_workflow_mode')}",
        f"- build_output_research_status: {digest.get('build_output_research_status')}",
        f"- candidate_summary_available: {digest.get('candidate_summary_available')}",
        f"- virtual_portfolio_summary_available: {digest.get('virtual_portfolio_summary_available')}",
        f"- business_output_drift_count: {digest.get('business_output_drift_count')}",
        "- research digest is not a trade instruction",
        "",
    ])


def render_source_trace_report(*, source_trace: dict) -> str:
    lines = [
        "# A 股 Owner Daily Pack Source Trace",
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
        "# A 股 Owner Daily Pack Audit",
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
    lines.extend(["", "## Daily Pack Checks", ""])
    for key, value in audit.get("daily_pack_checks", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Boundary", ""])
    for key, value in audit.get("boundary", {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)

