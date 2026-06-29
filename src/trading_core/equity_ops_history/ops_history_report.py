"""Markdown reports for ops history baselines."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_ops_history_reports(output_dir: Path, payload: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "A_SHARE_OPS_RUN_HISTORY_BASELINE.md").write_text(render_run_history(payload), encoding="utf-8")
    (output_dir / "A_SHARE_OPS_HEALTH_SCORE_BASELINE.md").write_text(render_health_score(payload), encoding="utf-8")
    (output_dir / "A_SHARE_OPS_WARNING_ISSUE_BASELINE.md").write_text(render_warning_issue(payload), encoding="utf-8")
    (output_dir / "A_SHARE_OPS_MODULE_RELIABILITY_BASELINE.md").write_text(render_module_reliability(payload), encoding="utf-8")
    (output_dir / "A_SHARE_OPS_HISTORY_SOURCE_TRACE.md").write_text(render_source_trace(payload), encoding="utf-8")


def render_run_history(payload: dict[str, Any]) -> str:
    summary = payload["ops_history_summary"]
    append = payload["ops_history_append_result"]
    sufficiency = payload["ops_trend_sufficiency"]
    return "\n".join(
        [
            "# A-Share Ops Run History Baseline",
            "",
            f"- as_of_date: {summary['as_of_date']}",
            f"- source_version: {summary['source_version']}",
            f"- observation_count: {summary['run_history_observation_count']}",
            f"- trend_analysis_available: {str(summary['trend_analysis_available']).lower()}",
            f"- baseline_status: {summary['baseline_status']}",
            f"- minimum_required_observations: {sufficiency['minimum_required_observations']}",
            f"- append_completed: {str(append['append_completed']).lower()}",
            f"- idempotent_append: {str(append['idempotent_append']).lower()}",
            "",
            "This report documents historical ops baselines only. It does not generate order previews, broker actions, or buy/sell instructions.",
            "",
        ]
    )


def render_health_score(payload: dict[str, Any]) -> str:
    history = payload["ops_health_score_history"]
    baseline = payload["ops_health_score_baseline"]
    latest = history.get("records", [{}])[-1] if history.get("records") else {}
    return "\n".join(
        [
            "# A-Share Ops Health Score Baseline",
            "",
            f"- latest_score: {latest.get('score')}",
            f"- latest_grade: {latest.get('grade')}",
            f"- baseline_status: {baseline.get('baseline_status')}",
            f"- observation_count: {baseline.get('observation_count')}",
            f"- average_score: {baseline.get('average_score')}",
            "",
        ]
    )


def render_warning_issue(payload: dict[str, Any]) -> str:
    warnings = payload["ops_warning_recurrence_baseline"].get("items", [])
    issues = payload["ops_issue_recurrence_baseline"].get("items", [])
    actions = payload["ops_action_recurrence_baseline"].get("items", [])
    return "\n".join(
        [
            "# A-Share Ops Warning And Issue Baseline",
            "",
            f"- warning_items: {len(warnings)}",
            f"- issue_items: {len(issues)}",
            f"- safe_action_items: {len(actions)}",
            "- recurrence_status: insufficient history until the minimum observation threshold is met",
            "",
            "Safe actions remain informational and manual. This file is not an order instruction.",
            "",
        ]
    )


def render_module_reliability(payload: dict[str, Any]) -> str:
    modules = payload["ops_module_reliability_baseline"].get("modules", [])
    lines = ["# A-Share Ops Module Reliability Baseline", ""]
    for row in modules:
        lines.append(f"- {row['module_id']}: status={row['latest_status']}, reliability_rate={row['reliability_rate']}")
    lines.append("")
    return "\n".join(lines)


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["ops_history_source_trace"]
    return "\n".join(
        [
            "# A-Share Ops History Source Trace",
            "",
            f"- source_trace_complete: {str(trace.get('source_trace_complete')).lower()}",
            f"- source_count: {len(trace.get('source_artifacts', []))}",
            f"- output_count: {len(trace.get('output_artifacts', []))}",
            f"- forbidden_path_hits: {len(trace.get('forbidden_path_hits', []))}",
            "",
        ]
    )


def render_audit(audit: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Ops History Baseline Audit",
            "",
            f"- audit_id: {audit['audit_id']}",
            f"- overall_passed: {str(audit['overall_passed']).lower()}",
            f"- blocking_reasons: {', '.join(audit['blocking_reasons']) if audit['blocking_reasons'] else 'none'}",
            f"- run_history_observation_count: {audit['trend_sufficiency']['run_history_observation_count']}",
            f"- trend_analysis_available: {str(audit['trend_sufficiency']['trend_analysis_available']).lower()}",
            f"- baseline_status: {audit['trend_sufficiency']['baseline_status']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )

