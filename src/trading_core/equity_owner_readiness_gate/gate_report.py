"""Markdown reports for owner readiness gate."""

from __future__ import annotations

from trading_core.equity_owner_readiness_gate.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_OWNER_READINESS_GATE.md": render_gate(payloads),
        "A_SHARE_DAILY_PACK_QUALITY_THRESHOLDS.md": render_thresholds(payloads),
        "A_SHARE_OWNER_RELEASE_RECOMMENDATION.md": render_recommendation(payloads),
        "A_SHARE_QUALITY_EXCEPTION_CANDIDATES.md": render_exceptions(payloads),
        "A_SHARE_OWNER_READINESS_GATE_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_gate(payloads: dict) -> str:
    decision = payloads["owner_readiness_gate_decision"]
    score = payloads["owner_readiness_score_gate"]
    return "\n".join(
        [
            "# A Share Owner Readiness Gate",
            "",
            "## 1. Owner Readiness Gate 总览",
            f"- decision: {decision['decision']}",
            f"- owner_operationally_acceptable: {decision['owner_operationally_acceptable']}",
            "## 2. 输入审计状态",
            f"- source_workflow_mode: {decision['source_workflow_mode']}",
            "## 3. Owner Readiness Score Gate",
            f"- actual: {score['actual_value']}",
            f"- threshold: {score['threshold']}",
            f"- passed: {score['passed']}",
            "## 4. Daily Pack Completeness Gate",
            f"- passed: {payloads['daily_pack_completeness_gate']['passed']}",
            "## 5. Warning / Issue Gate",
            f"- passed: {payloads['warning_issue_quality_gate']['passed']}",
            "## 6. Safe Action Gate",
            f"- passed: {payloads['safe_action_quality_gate']['passed']}",
            "## 7. Protected Path Gate",
            f"- passed: {payloads['protected_path_quality_gate']['passed']}",
            "## 8. Boundary Gate",
            f"- passed: {payloads['boundary_quality_gate']['passed']}",
            "## 9. Source Trace Gate",
            f"- passed: {payloads['source_trace_quality_gate']['passed']}",
            "## 10. Trend Sufficiency Gate",
            f"- passed: {payloads['trend_sufficiency_quality_gate']['passed']}",
            "## 11. Gate Decision",
            f"- blocking_reasons: {decision['blocking_reasons']}",
            f"- warnings: {decision['warnings']}",
            "## 12. Owner Release Recommendation",
            f"- recommendation: {payloads['owner_release_recommendation']['recommendation']}",
            "## 13. 下一步建议",
            "- 如 decision 为 blocked，先处理 developer_follow_up_items，再重新审计 gate artifacts。",
            "## 14. 免责声明",
            "- 这是 owner operations release gate，不是投资建议、交易建议或订单指令。",
            "",
        ]
    )


def render_thresholds(payloads: dict) -> str:
    evaluation = payloads["quality_threshold_evaluation"]
    policy = payloads["owner_readiness_threshold_policy"]
    return "\n".join(
        [
            "# A Share Daily Pack Quality Thresholds",
            "",
            f"- minimum_owner_readiness_score: {policy['minimum_owner_readiness_score']}",
            f"- minimum_required_artifact_completeness: {policy['minimum_required_artifact_completeness']}",
            f"- minimum_markdown_report_completeness: {policy['minimum_markdown_report_completeness']}",
            f"- passed_gates: {evaluation['passed_gates']}",
            f"- failed_gates: {evaluation['failed_gates']}",
            f"- warnings: {evaluation['warnings']}",
            "- interpretation: daily pack quality thresholds are owner operations checks only, not investment quality thresholds.",
            "",
        ]
    )


def render_recommendation(payloads: dict) -> str:
    recommendation = payloads["owner_release_recommendation"]
    return "\n".join(
        [
            "# A Share Owner Release Recommendation",
            "",
            "- 这是 owner operations release recommendation，不是投资建议或交易建议。",
            f"- recommendation: {recommendation['recommendation']}",
            f"- reasoning_summary: {recommendation['reasoning_summary']}",
            f"- required_owner_actions: {recommendation['required_owner_actions']}",
            f"- developer_follow_up_items: {recommendation['developer_follow_up_items']}",
            "",
        ]
    )


def render_exceptions(payloads: dict) -> str:
    exception_list = payloads["quality_exception_candidate_list"]
    lines = [
        "# A Share Quality Exception Candidates",
        "",
        "- Candidate exceptions are not approvals or waivers.",
        f"- candidate_count: {exception_list['candidate_count']}",
        "- auto_waiver_allowed: False",
        "",
    ]
    for item in exception_list["candidates"]:
        lines.append(f"- {item['source_gate']}: {item['severity']} / {item['description']} / auto_waiver_allowed={item['auto_waiver_allowed']}")
    lines.append("")
    return "\n".join(lines)


def render_source_trace(payloads: dict) -> str:
    trace = payloads["owner_readiness_gate_source_trace"]
    return "\n".join(
        [
            "# A Share Owner Readiness Gate Source Trace",
            "",
            f"- source_trace_complete: {trace['source_trace_complete']}",
            f"- source_artifacts: {len(trace['source_artifacts'])}",
            f"- output_artifacts: {len(trace['output_artifacts'])}",
            "- No broker, order, or real-account source is used.",
            "",
        ]
    )


def render_audit(audit: dict) -> str:
    return "\n".join(
        [
            "# A Share Owner Readiness Gate Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- decision: {audit['gate_checks']['decision']}",
            f"- actual_owner_readiness_score: {audit['gate_checks']['actual_owner_readiness_score']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )
