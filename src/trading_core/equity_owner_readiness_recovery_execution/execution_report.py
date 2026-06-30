"""Markdown reports for owner readiness recovery execution."""

from __future__ import annotations

from trading_core.equity_owner_readiness_recovery_execution.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_RECOVERY_EXECUTION_TRACKER.md": render_tracker(payloads),
        "A_SHARE_RECOVERY_TASK_EVIDENCE.md": render_evidence(payloads),
        "A_SHARE_GATE_REEVALUATION_PREP.md": render_prep(payloads),
        "A_SHARE_CONTROLLED_REEVALUATION_PLAN.md": render_controlled_plan(payloads),
        "A_SHARE_RECOVERY_EXECUTION_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_tracker(payloads: dict) -> str:
    summary = payloads["recovery_execution_summary"]
    return "\n".join(
        [
            "# A Share Recovery Execution Tracker",
            "",
            f"- source_gate_decision: {summary['source_gate_decision']}",
            f"- blocked_gate_decision_preserved: {summary['blocked_gate_decision_preserved']}",
            f"- task_count: {summary['task_count']}",
            f"- evidence_available_count: {summary['evidence_available_count']}",
            f"- verified_by_audit_only_count: {summary['verified_by_audit_only_count']}",
            f"- completed_count: {summary['completed_count']}",
            f"- tasks_marked_complete_by_default: {summary['tasks_marked_complete_by_default']}",
            "- No gate reevaluation occurred in this stage.",
            "- This report is not investment advice and not an order instruction.",
            "",
        ]
    )


def render_evidence(payloads: dict) -> str:
    registry = payloads["recovery_task_evidence_registry"]
    lines = [
        "# A Share Recovery Task Evidence",
        "",
        f"- evidence_record_count: {registry['evidence_record_count']}",
        f"- evidence_available_count: {registry['evidence_available_count']}",
        f"- forbidden_evidence_types_detected: {registry['forbidden_evidence_types_detected']}",
    ]
    for row in registry["records"]:
        lines.extend(["", f"## {row['source_task_id']}", f"- evidence_available: {row['evidence_available']}", f"- supports_task_status: {row['supports_task_status']}"])
    lines.append("")
    return "\n".join(lines)


def render_prep(payloads: dict) -> str:
    decision = payloads["gate_reevaluation_readiness_decision"]
    checklist = payloads["gate_reevaluation_prerequisite_checklist"]
    return "\n".join(
        [
            "# A Share Gate Reevaluation Prep",
            "",
            f"- gate_reevaluation_readiness_decision: {decision['gate_reevaluation_readiness_decision']}",
            f"- ready_for_future_gate_reevaluation: {decision['ready_for_future_gate_reevaluation']}",
            f"- blocking_reasons: {decision['blocking_reasons']}",
            f"- all_recovery_tasks_have_evidence: {checklist['all_recovery_tasks_have_evidence']}",
            "- No owner-readiness gate rerun was executed.",
            "",
        ]
    )


def render_controlled_plan(payloads: dict) -> str:
    plan = payloads["controlled_reevaluation_plan"]
    return "\n".join(
        [
            "# A Share Controlled Reevaluation Plan",
            "",
            f"- gate_reevaluation_executed: {plan['gate_reevaluation_executed']}",
            f"- rerun_owner_readiness_gate: {plan['rerun_owner_readiness_gate']}",
            f"- rerun_build_from_existing_data: {plan['rerun_build_from_existing_data']}",
            f"- rerun_daily_pack: {plan['rerun_daily_pack']}",
            f"- future_version: {plan['future_version']}",
            "",
        ]
    )


def render_source_trace(payloads: dict) -> str:
    trace = payloads["recovery_execution_source_trace"]
    return "\n".join(
        [
            "# A Share Recovery Execution Source Trace",
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
            "# A Share Owner Readiness Recovery Execution Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- source_gate_decision: {audit['input_checks']['source_gate_decision']}",
            f"- task_completion_not_fabricated: {audit['execution_checks']['task_completion_not_fabricated']}",
            f"- ready_for_future_gate_reevaluation: {audit['execution_checks']['ready_for_future_gate_reevaluation']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )
