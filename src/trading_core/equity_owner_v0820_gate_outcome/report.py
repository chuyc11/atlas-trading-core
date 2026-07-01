"""Markdown reports for v0.8.20 owner gate outcome."""

from __future__ import annotations

from trading_core.equity_owner_v0820_gate_outcome.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_V0820_OWNER_GATE_OUTCOME.md": render_owner_outcome(payloads),
        "A_SHARE_V0820_BRANCH_DECISION.md": render_branch(payloads),
        "A_SHARE_CONTROLLED_GATE_REEVALUATION_OUTCOME.md": render_controlled(payloads),
        "A_SHARE_FINAL_BLOCKED_CLOSEOUT.md": render_closeout(payloads),
        "A_SHARE_V0820_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_owner_outcome(payloads: dict) -> str:
    summary = payloads["v0820_owner_outcome_summary"]
    return "\n".join(
        [
            "# A 股 v0.8.20 Owner Gate Outcome",
            "",
            "## 1. v0.8.20 Gate Outcome 总览",
            f"- selected_branch: {summary['selected_branch']}",
            f"- controlled_reevaluation_executed: {summary['controlled_reevaluation_executed']}",
            f"- final_blocked_closeout_generated: {summary['final_blocked_closeout_generated']}",
            "## 2. v0.8.19 Evidence Prep 状态",
            f"- source_gate_decision: {summary['source_gate_decision']}",
            f"- previous_readiness_score: {summary['previous_readiness_score']}",
            f"- minimum_owner_readiness_score: {summary['minimum_owner_readiness_score']}",
            "## 3. Branch Decision",
            f"- branch_decision_consistent: {summary['branch_decision_consistent']}",
            "## 4. Controlled Reevaluation Outcome 或 Final Blocked Closeout",
            f"- owner_operationally_acceptable: {summary['owner_operationally_acceptable']}",
            f"- new_controlled_gate_decision_generated: {summary['new_controlled_gate_decision_generated']}",
            "## 5. Threshold Preservation",
            f"- threshold_lowered: {summary['threshold_lowered']}",
            "## 6. Waiver Exclusion",
            f"- auto_waiver_allowed: {summary['auto_waiver_allowed']}",
            f"- waiver_used_for_outcome: {summary['waiver_used_for_outcome']}",
            "## 7. Boundary 状态",
            "- 非交易动作；未连接 broker；未生成订单、订单预览或买卖信号；未调用旧 run-daily。",
            "## 8. 下一步建议",
            f"- recommended_next_version: {summary['recommended_next_version']}",
            "## 9. 免责声明",
            "- 本报告仅用于 owner-readiness 运维状态收口，不是投资建议，也不是订单指令。",
            "",
        ]
    )


def render_branch(payloads: dict) -> str:
    branch = payloads["v0820_branch_decision"]
    return "\n".join(
        [
            "# A Share v0.8.20 Branch Decision",
            "",
            f"- selected_branch: {branch['selected_branch']}",
            f"- controlled_reevaluation_allowed: {branch['controlled_reevaluation_allowed']}",
            f"- final_blocked_closeout_required: {branch['final_blocked_closeout_required']}",
            f"- branch_reasons: {branch['branch_reasons']}",
            "",
        ]
    )


def render_controlled(payloads: dict) -> str:
    controlled = payloads["controlled_gate_reevaluation_outcome"]
    return "\n".join(
        [
            "# A Share Controlled Gate Reevaluation Outcome",
            "",
            f"- branch_not_selected: {controlled['branch_not_selected']}",
            f"- controlled_reevaluation_executed: {controlled['controlled_reevaluation_executed']}",
            f"- new_controlled_readiness_score_generated: {controlled['new_controlled_readiness_score_generated']}",
            f"- new_controlled_gate_decision_generated: {controlled['new_controlled_gate_decision_generated']}",
            "- This artifact is not a trade instruction.",
            "",
        ]
    )


def render_closeout(payloads: dict) -> str:
    closeout = payloads["final_blocked_closeout"]
    return "\n".join(
        [
            "# A Share Final Blocked Closeout",
            "",
            f"- final_blocked_closeout_generated: {closeout['final_blocked_closeout_generated']}",
            f"- source_gate_decision: {closeout['source_gate_decision']}",
            f"- evidence_insufficient: {closeout['evidence_insufficient']}",
            f"- remaining_gap_count: {closeout['remaining_gap_count']}",
            f"- blocking_gap_count: {closeout['blocking_gap_count']}",
            "- Controlled reevaluation was not executed; no new gate score or gate decision was generated.",
            "- Next step is closeout review and v0.9.0 RC prep.",
            "",
        ]
    )


def render_source_trace(payloads: dict) -> str:
    trace = payloads["v0820_source_trace"]
    return "\n".join(
        [
            "# A Share v0.8.20 Source Trace",
            "",
            f"- source_trace_complete: {trace['source_trace_complete']}",
            f"- source_artifacts: {len(trace['source_artifacts'])}",
            f"- output_artifacts: {len(trace['output_artifacts'])}",
            "",
        ]
    )


def render_audit(audit: dict) -> str:
    return "\n".join(
        [
            "# A Share Owner v0.8.20 Gate Outcome Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- selected_branch: {audit['outcome_checks']['selected_branch']}",
            f"- controlled_reevaluation_executed: {audit['outcome_checks']['controlled_reevaluation_executed']}",
            f"- final_blocked_closeout_generated: {audit['outcome_checks']['final_blocked_closeout_generated']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )

