"""Markdown reports for owner quality exception workflow."""

from __future__ import annotations

from trading_core.equity_owner_quality_exceptions.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_OWNER_QUALITY_EXCEPTION_WORKFLOW.md": render_workflow(payloads),
        "A_SHARE_BLOCKED_DAILY_PACK_OWNER_NOTICE.md": render_notice(payloads),
        "A_SHARE_OWNER_READINESS_GAP_ANALYSIS.md": render_gap(payloads),
        "A_SHARE_ESCALATION_WORKFLOW.md": render_escalation(payloads),
        "A_SHARE_MANUAL_WAIVER_POLICY.md": render_waiver(payloads),
        "A_SHARE_DEVELOPER_FOLLOW_UP_TRACKER.md": render_developer(payloads),
        "A_SHARE_QUALITY_EXCEPTION_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_workflow(payloads: dict) -> str:
    intake = payloads["blocked_gate_intake"]
    registry = payloads["quality_exception_registry"]
    return "\n".join(
        [
            "# A Share Owner Quality Exception Workflow",
            "",
            "## 1. Quality Exception Workflow 总览",
            f"- source_gate_decision: {intake['source_gate_decision']}",
            f"- quality_exception_count: {registry['exception_count']}",
            "## 2. Blocked Gate Intake",
            f"- owner_operationally_acceptable: {intake['owner_operationally_acceptable']}",
            "## 3. Readiness Score Gap",
            f"- score_gap: {intake['readiness_score_gap']}",
            "## 4. Exception Classification",
            f"- classified_count: {payloads['quality_exception_classification']['classified_count']}",
            "## 5. Waiver Candidate Evaluation",
            "- auto_waiver_allowed: False",
            "- waiver_changes_gate_decision: False",
            "## 6. Escalation Workflow",
            f"- step_count: {payloads['escalation_workflow']['step_count']}",
            "## 7. Developer Follow-up",
            f"- follow_up_count: {payloads['developer_follow_up_tracker']['follow_up_count']}",
            "## 8. Owner Follow-up Checklist",
            f"- owner_follow_up_count: {payloads['owner_follow_up_checklist']['owner_follow_up_count']}",
            "## 9. Boundary 状态",
            f"- overall_passed: {payloads['quality_exception_boundary_check']['overall_passed']}",
            "## 10. 下一步建议",
            "- 保留 blocked 状态，按 developer follow-up 与 owner checklist 处理。",
            "## 11. 免责声明",
            "- 本报告仅用于 owner operations；不是投资建议、交易建议或订单指令。",
            "",
        ]
    )


def render_notice(payloads: dict) -> str:
    notice = payloads["blocked_daily_pack_owner_notice"]
    intake = payloads["blocked_gate_intake"]
    return "\n".join(
        [
            "# A Share Blocked Daily Pack Owner Notice",
            "",
            "- 当前 daily pack 未达到 owner-operationally-acceptable。",
            "- 这是运维可接受性阻塞，不是交易信号。",
            "- audit passed 代表阻塞状态被正确表达，不代表 gate 放行。",
            f"- score {intake['actual_owner_readiness_score']} is below threshold {intake['minimum_owner_readiness_score']}.",
            f"- message: {notice['message_zh']}",
            "- not investment advice",
            "- not order instruction",
            "- not live trading ready",
            "",
        ]
    )


def render_gap(payloads: dict) -> str:
    gap = payloads["owner_readiness_gap_analysis"]
    return "\n".join(
        [
            "# A Share Owner Readiness Gap Analysis",
            "",
            f"- minimum_owner_readiness_score: {gap['minimum_owner_readiness_score']}",
            f"- actual_owner_readiness_score: {gap['actual_owner_readiness_score']}",
            f"- score_gap: {gap['score_gap']}",
            f"- grade: {gap['grade']}",
            f"- score_drivers: {gap['score_drivers']}",
            "- owner readiness is operations readiness only.",
            "- It is not strategy performance.",
            "- It is not a trading signal.",
            "",
        ]
    )


def render_escalation(payloads: dict) -> str:
    workflow = payloads["escalation_workflow"]
    return "\n".join(["# A Share Escalation Workflow", "", f"- step_count: {workflow['step_count']}", "- forbidden routes are disabled.", ""])


def render_waiver(payloads: dict) -> str:
    return "\n".join(
        [
            "# A Share Manual Waiver Policy",
            "",
            "- v0.8.14 不自动批准 waiver。",
            "- v0.8.14 的 waiver 只允许 owner-review-only 范围。",
            "- waiver 不改变原始 gate decision。",
            "- waiver 不允许任何交易动作。",
            "",
        ]
    )


def render_developer(payloads: dict) -> str:
    tracker = payloads["developer_follow_up_tracker"]
    return "\n".join(["# A Share Developer Follow Up Tracker", "", f"- follow_up_count: {tracker['follow_up_count']}", "- safe commands are audit-only.", ""])


def render_source_trace(payloads: dict) -> str:
    trace = payloads["quality_exception_source_trace"]
    return "\n".join(["# A Share Quality Exception Source Trace", "", f"- source_trace_complete: {trace['source_trace_complete']}", f"- source_artifacts: {len(trace['source_artifacts'])}", ""])


def render_audit(audit: dict) -> str:
    return "\n".join(
        [
            "# A Share Owner Quality Exception Workflow Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- source_gate_decision: {audit['input_checks']['source_gate_decision']}",
            f"- readiness_score_gap: {audit['exception_checks']['readiness_score_gap']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )
