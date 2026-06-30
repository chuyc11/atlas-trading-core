"""Markdown reports for owner readiness recovery."""

from __future__ import annotations

from trading_core.equity_owner_readiness_recovery.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_OWNER_READINESS_RECOVERY_PLAN.md": render_recovery_plan(payloads),
        "A_SHARE_READINESS_GAP_SUMMARY.md": render_gap(payloads),
        "A_SHARE_QUALITY_IMPROVEMENT_TASK_BACKLOG.md": render_backlog(payloads),
        "A_SHARE_DEVELOPER_RECOVERY_FOLLOW_UP.md": render_developer(payloads),
        "A_SHARE_GATE_REEVALUATION_READINESS_CHECKLIST.md": render_checklist(payloads),
        "A_SHARE_RECOVERY_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_recovery_plan(payloads: dict) -> str:
    gap = payloads["readiness_gap_summary"]
    backlog = payloads["recovery_task_backlog"]
    return "\n".join(
        [
            "# A Share Owner Readiness Recovery Plan",
            "",
            "## Current State",
            f"- source_gate_decision: {gap['source_gate_decision']}",
            f"- blocked_state_preserved: {gap['blocked_state_preserved']}",
            f"- score: {gap['actual_owner_readiness_score']} / threshold {gap['minimum_owner_readiness_score']}",
            f"- score_gap: {gap['readiness_score_gap']}",
            "## Recovery Scope",
            "- This is a research-only and virtual-only owner readiness quality plan.",
            "- It keeps recovery tasks planned until evidence exists.",
            "- It keeps the prior blocked gate decision unchanged.",
            "## Task Backlog",
            f"- task_count: {backlog['task_count']}",
            f"- tasks_marked_complete_by_default: {backlog['tasks_marked_complete_by_default']}",
            "## Next Version",
            f"- recommended_next_version: {payloads['recovery_summary']['recommended_next_version']}",
            "## Boundaries",
            "- No broker connection, real account read, order preview, external notification, or gate threshold lowering is performed.",
            "- This report is not investment advice and not an order instruction.",
            "",
        ]
    )


def render_gap(payloads: dict) -> str:
    gap = payloads["readiness_gap_summary"]
    drivers = payloads["score_driver_analysis"]
    return "\n".join(
        [
            "# A Share Readiness Gap Summary",
            "",
            f"- minimum_owner_readiness_score: {gap['minimum_owner_readiness_score']}",
            f"- actual_owner_readiness_score: {gap['actual_owner_readiness_score']}",
            f"- actual_owner_readiness_grade: {gap['actual_owner_readiness_grade']}",
            f"- readiness_score_gap: {gap['readiness_score_gap']}",
            f"- quality_exception_count: {gap['quality_exception_count']}",
            f"- developer_follow_up_count: {gap['developer_follow_up_count']}",
            f"- score_penalty_components: {drivers['score_penalty_components']}",
            "",
        ]
    )


def render_backlog(payloads: dict) -> str:
    backlog = payloads["recovery_task_backlog"]
    lines = [
        "# A Share Quality Improvement Task Backlog",
        "",
        f"- task_count: {backlog['task_count']}",
        f"- forbidden_recovery_task_categories_detected: {backlog['forbidden_recovery_task_categories_detected']}",
    ]
    for task in backlog["tasks"]:
        lines.extend(
            [
                "",
                f"## {task['task_id']}",
                f"- category: {task['category']}",
                f"- priority: {task['priority']}",
                f"- expected_score_impact: {task['expected_score_impact']}",
                f"- status: {task['status']}",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def render_developer(payloads: dict) -> str:
    plan = payloads["developer_follow_up_recovery_plan"]
    return "\n".join(
        [
            "# A Share Developer Recovery Follow Up",
            "",
            f"- follow_up_count: {plan['follow_up_count']}",
            "- all commands listed here are audit-only verification commands.",
            "- completion requires evidence before any future gate reevaluation.",
            "",
        ]
    )


def render_checklist(payloads: dict) -> str:
    checklist = payloads["gate_reevaluation_readiness_checklist"]
    return "\n".join(
        [
            "# A Share Gate Reevaluation Readiness Checklist",
            "",
            f"- ready_for_future_gate_reevaluation: {checklist['ready_for_future_gate_reevaluation']}",
            f"- required_artifacts_fixed: {checklist['required_artifacts_fixed']}",
            f"- developer_follow_up_resolved: {checklist['developer_follow_up_resolved']}",
            f"- owner_follow_up_completed: {checklist['owner_follow_up_completed']}",
            f"- no_threshold_lowering: {checklist['no_threshold_lowering']}",
            f"- no_auto_waiver: {checklist['no_auto_waiver']}",
            "",
        ]
    )


def render_source_trace(payloads: dict) -> str:
    trace = payloads["recovery_source_trace"]
    return "\n".join(
        [
            "# A Share Recovery Source Trace",
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
            "# A Share Owner Readiness Recovery Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- source_gate_decision: {audit['input_checks']['source_gate_decision']}",
            f"- readiness_score_gap: {audit['recovery_checks']['readiness_score_gap']}",
            f"- recovery_tasks_generated: {audit['recovery_checks']['recovery_tasks_generated']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )
