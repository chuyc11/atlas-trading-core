"""Markdown reports for daily pack history."""

from __future__ import annotations



def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_OWNER_DAILY_PACK_HISTORY.md": render_history(payloads),
        "A_SHARE_OWNER_READINESS_TRENDS.md": render_readiness(payloads),
        "A_SHARE_DAILY_PACK_QUALITY_BASELINE.md": render_quality(payloads),
        "A_SHARE_DAILY_PACK_WARNING_SAFE_ACTION_TRENDS.md": render_warning_safe(payloads),
        "A_SHARE_DAILY_PACK_HISTORY_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        (output_dir / name).write_text(text, encoding="utf-8")


def render_history(payloads: dict) -> str:
    snapshot = payloads["daily_pack_history_snapshot"]
    append = payloads["daily_pack_history_append_result"]
    return "\n".join(
        [
            "# A-Share Owner Daily Pack History",
            "",
            f"- observation_count: {snapshot['daily_pack_history_observation_count']}",
            f"- append_completed: {append['append_completed']}",
            f"- idempotent_append: {append['idempotent_append']}",
            "- append-only history is used by default.",
            "- No synthetic daily pack history is created.",
            "",
        ]
    )


def render_readiness(payloads: dict) -> str:
    score = payloads["owner_readiness_score"]
    suff = payloads["owner_readiness_trend_sufficiency"]
    return "\n".join(
        [
            "# A-Share Owner Readiness Trends",
            "",
            f"- owner_readiness_score: {score['score']}",
            f"- owner_readiness_grade: {score['grade']}",
            f"- trend_analysis_available: {suff['trend_analysis_available']}",
            f"- readiness_trend_status: {suff['readiness_trend_status']}",
            "- Owner readiness is operational readiness only, not strategy performance.",
            "- The report is not a trade instruction.",
            "",
        ]
    )


def render_quality(payloads: dict) -> str:
    quality = payloads["daily_pack_quality_baseline"]
    return "\n".join(
        [
            "# A-Share Daily Pack Quality Baseline",
            "",
            f"- required_artifacts_complete: {quality['required_artifacts_complete']}",
            f"- markdown_reports_complete: {quality['markdown_reports_complete']}",
            f"- source_trace_complete: {quality['source_trace_complete']}",
            f"- boundary_clean: {quality['boundary_clean']}",
            f"- baseline_status: {quality['baseline_status']}",
            "- Insufficient history is not treated as a blocker for this release.",
            "",
        ]
    )


def render_warning_safe(payloads: dict) -> str:
    warning = payloads["warning_issue_trend_baseline"]
    safe = payloads["safe_action_trend_baseline"]
    return "\n".join(
        [
            "# A-Share Daily Pack Warning and Safe Action Trends",
            "",
            f"- warning_count: {warning['warning_count']}",
            f"- blocking_count: {warning['blocking_count']}",
            f"- safe_action_count: {safe['safe_action_count']}",
            f"- safe_actions_not_trade_related: {safe['safe_actions_not_trade_related']}",
            f"- trend_analysis_available: {warning['trend_analysis_available']}",
            "- Repeated and resolved items are reported only when enough real observations exist.",
            "",
        ]
    )


def render_source_trace(payloads: dict) -> str:
    trace = payloads["daily_pack_history_source_trace"]
    return "\n".join(
        [
            "# A-Share Daily Pack History Source Trace",
            "",
            f"- source_trace_complete: {trace['source_trace_complete']}",
            f"- source_artifacts: {len(trace['source_artifacts'])}",
            f"- output_artifacts: {len(trace['output_artifacts'])}",
            "- No broker, order, or real-account source is required.",
            "",
        ]
    )


def render_audit(audit: dict) -> str:
    return "\n".join(
        [
            "# A-Share Owner Daily Pack History Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- daily_pack_history_observation_count: {audit['history_checks']['daily_pack_history_observation_count']}",
            f"- trend_analysis_available: {audit['history_checks']['trend_analysis_available']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )
