"""Markdown reports for v0.8.21 closeout review."""

from __future__ import annotations

from trading_core.equity_owner_closeout_review.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_OWNER_READINESS_CLOSEOUT_REVIEW.md": render_closeout_review(payloads),
        "A_SHARE_V0813_TO_V0820_LINEAGE_REVIEW.md": render_lineage_review(payloads),
        "A_SHARE_V090_RC_SCOPE_PROPOSAL.md": render_rc_scope(payloads),
        "A_SHARE_V090_FULL_REGRESSION_PLAN.md": render_full_regression_plan(payloads),
        "A_SHARE_V090_RELEASE_RISK_REGISTER.md": render_risk_register(payloads),
        "A_SHARE_CLOSEOUT_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_closeout_review(payloads: dict) -> str:
    summary = payloads["closeout_summary"]
    blockers = payloads["unresolved_blocker_register"]
    decision = payloads["v090_release_candidate_readiness_decision"]
    return "\n".join(
        [
            "# A 股 Owner-Readiness Closeout Review",
            "",
            "## 1. Closeout Review 总览",
            f"- as_of_date: {summary['as_of_date']}",
            f"- selected_v0820_branch: {summary['selected_v0820_branch']}",
            "## 2. 当前最终状态",
            f"- source_gate_decision: {summary['source_gate_decision']}",
            f"- owner_operationally_acceptable: {summary['owner_operationally_acceptable']}",
            "## 3. v0.8.13 到 v0.8.20 Lineage",
            "- blocked 状态、54/75 分数差距、无 waiver、无新 gate score/decision 均已进入 lineage review。",
            "## 4. 为什么最终仍然 Blocked",
            f"- readiness_score: {summary['previous_readiness_score']}",
            f"- minimum_owner_readiness_score: {summary['minimum_owner_readiness_score']}",
            f"- score_gap: {summary['score_gap']}",
            f"- unresolved_blocker_count: {blockers['unresolved_blocker_count']}",
            "## 5. 为什么这不是系统失败",
            "- v0.8.20 的 blocked closeout 是审计通过后的保守结果，表示证据不足时系统保持 fail-close。",
            "## 6. v0.9.0 RC Scope",
            f"- decision: {decision['decision']}",
            "- v0.9.0 可以作为研究系统收口 RC，但不能描述为 owner-readiness 已通过。",
            "## 7. v0.9.0 Full Regression Plan",
            "- v0.8.21 只生成 full regression plan；full pytest 留到 v0.9.0 执行。",
            "## 8. 已知风险",
            "- blocked 状态误读、证据缺口、文档漂移、边界回归均进入风险登记。",
            "## 9. 下一步建议",
            f"- recommended_next_version: {summary['recommended_next_version']}",
            "## 10. 免责声明",
            "- 本报告仅为 research-only / virtual-only closeout review，不是投资建议、不是订单指令、不代表实盘放行。",
            "",
        ]
    )


def render_lineage_review(payloads: dict) -> str:
    lineage = payloads["v0813_to_v0820_lineage_review"]
    lines = [
        "# A Share v0.8.13 to v0.8.20 Lineage Review",
        "",
        f"- stage_count: {lineage['stage_count']}",
        f"- blocked_state_visible: {lineage['blocked_state_visible']}",
        f"- readiness_score_54_visible: {lineage['readiness_score_54_visible']}",
        f"- minimum_threshold_75_visible: {lineage['minimum_threshold_75_visible']}",
        "",
    ]
    for row in lineage["stages"]:
        lines.append(f"- {row['version']} {row['stage']}: source_gate_decision={row['source_gate_decision']}, audit_overall_passed={row['audit_overall_passed']}")
    lines.append("")
    return "\n".join(lines)


def render_rc_scope(payloads: dict) -> str:
    proposal = payloads["v090_rc_scope_proposal"]
    return "\n".join(
        [
            "# A Share v0.9.0 RC Scope Proposal",
            "",
            "- v0.9.0 可以作为研究系统收口 RC，但不能被描述为 owner-readiness 已通过。",
            "- blocked owner-readiness state 是已知状态。",
            "- v0.9.0 不代表实盘放行。",
            f"- proposed_rc_version: {proposal['proposed_rc_version']}",
            f"- blocked_owner_readiness_state_acceptable_for_rc: {proposal['blocked_owner_readiness_state_acceptable_for_rc']}",
            "",
        ]
    )


def render_full_regression_plan(payloads: dict) -> str:
    plan = payloads["v090_full_regression_plan"]
    lines = [
        "# A Share v0.9.0 Full Regression Plan",
        "",
        f"- full_pytest_command: `{plan['full_pytest_command']}`",
        f"- full_pytest_run: {plan['full_pytest_run']}",
        f"- full_pytest_required_in_v090: {plan['full_pytest_required_in_v090']}",
        "",
        "## Audit Sweep",
    ]
    lines.extend(f"- `{command}`" for command in plan["audit_sweep_commands"])
    lines.append("")
    return "\n".join(lines)


def render_risk_register(payloads: dict) -> str:
    register = payloads["v090_release_risk_register"]
    lines = ["# A Share v0.9.0 Release Risk Register", "", f"- risk_count: {register['risk_count']}", ""]
    lines.extend(f"- {risk['risk_id']} {risk['category']}: severity={risk['severity']}, blocks_v090_rc={risk['blocks_v090_rc']}" for risk in register["risks"])
    lines.append("")
    return "\n".join(lines)


def render_source_trace(payloads: dict) -> str:
    trace = payloads["closeout_source_trace"]
    return "\n".join(
        [
            "# A Share Closeout Source Trace",
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
            "# A Share Owner Closeout Review Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- selected_v0820_branch: {audit['input_checks']['selected_v0820_branch']}",
            f"- source_gate_decision: {audit['input_checks']['source_gate_decision']}",
            f"- v090_rc_decision_consistent: {audit['closeout_checks']['v090_rc_decision_consistent']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )
