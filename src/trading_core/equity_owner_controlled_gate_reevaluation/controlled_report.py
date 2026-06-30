"""Markdown reports for controlled gate reevaluation."""

from __future__ import annotations

from trading_core.equity_owner_controlled_gate_reevaluation.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_CONTROLLED_GATE_REEVALUATION.md": render_controlled_reevaluation(payloads),
        "A_SHARE_REEVALUATION_SKIPPED_NOT_READY.md": render_skipped(payloads),
        "A_SHARE_REEVALUATION_READINESS_GUARD.md": render_guard(payloads),
        "A_SHARE_CONTROLLED_REEVALUATION_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_controlled_reevaluation(payloads: dict) -> str:
    summary = payloads["controlled_reevaluation_summary"]
    return "\n".join(
        [
            "# A Share Controlled Gate Reevaluation",
            "",
            f"- source_gate_decision: {summary['source_gate_decision']}",
            f"- blocked_gate_decision_preserved: {summary['blocked_gate_decision_preserved']}",
            f"- readiness_guard_passed: {summary['readiness_guard_passed']}",
            f"- reevaluation_allowed: {summary['reevaluation_allowed']}",
            f"- reevaluation_skipped: {summary['reevaluation_skipped']}",
            f"- controlled_reevaluation_decision: {summary['controlled_reevaluation_decision']}",
            f"- gate_reevaluation_executed: {summary['gate_reevaluation_executed']}",
            f"- recommended_next_version: {summary['recommended_next_version']}",
            "- This adapter records the controlled skip state only.",
            "- This report is not investment advice and not an order instruction.",
            "",
        ]
    )


def render_skipped(payloads: dict) -> str:
    skip = payloads["reevaluation_skip_decision"]
    not_ready = payloads["not_ready_reason_summary"]
    lines = [
        "# A Share Reevaluation Skipped Not Ready",
        "",
        f"- reevaluation_skipped: {skip['reevaluation_skipped']}",
        f"- reevaluation_skip_reason: {skip['reevaluation_skip_reason']}",
        f"- owner_operationally_acceptable: {skip['owner_operationally_acceptable']}",
        f"- new_gate_score_generated: {skip['new_gate_score_generated']}",
        f"- new_gate_decision_generated: {skip['new_gate_decision_generated']}",
        f"- reason_count: {not_ready['reason_count']}",
    ]
    for reason in not_ready["reasons"]:
        lines.append(f"- reason: {reason}")
    lines.append("")
    return "\n".join(lines)


def render_guard(payloads: dict) -> str:
    guard = payloads["reevaluation_readiness_guard"]
    return "\n".join(
        [
            "# A Share Reevaluation Readiness Guard",
            "",
            f"- readiness_guard_passed: {guard['readiness_guard_passed']}",
            f"- reevaluation_allowed: {guard['reevaluation_allowed']}",
            f"- reevaluation_block_reason: {guard['reevaluation_block_reason']}",
            f"- block_reasons: {guard['block_reasons']}",
            f"- evidence_available_count: {guard['evidence_available_count']}",
            f"- verified_by_audit_only_count: {guard['verified_by_audit_only_count']}",
            f"- completed_count: {guard['completed_count']}",
            "- No owner-readiness gate rerun was executed.",
            "",
        ]
    )


def render_source_trace(payloads: dict) -> str:
    trace = payloads["controlled_reevaluation_source_trace"]
    return "\n".join(
        [
            "# A Share Controlled Reevaluation Source Trace",
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
            "# A Share Owner Controlled Gate Reevaluation Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- source_gate_decision: {audit['input_checks']['source_gate_decision']}",
            f"- readiness_guard_passed: {audit['reevaluation_checks']['readiness_guard_passed']}",
            f"- reevaluation_skipped: {audit['reevaluation_checks']['reevaluation_skipped']}",
            f"- controlled_reevaluation_decision: {audit['reevaluation_checks']['controlled_reevaluation_decision']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )

