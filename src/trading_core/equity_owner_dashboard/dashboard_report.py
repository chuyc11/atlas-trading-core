"""Markdown reports for the v0.8.2 owner dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_dashboard_reports(output_dir: Path, payload: dict[str, Any], *, compact_only: bool = False) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "owner_dashboard_report": output_dir / "A_SHARE_OWNER_DASHBOARD.md",
        "owner_dashboard_compact_report": output_dir / "A_SHARE_OWNER_DASHBOARD_COMPACT.md",
        "owner_warning_blocker_report": output_dir / "A_SHARE_OWNER_WARNING_AND_BLOCKER_SUMMARY.md",
        "owner_artifact_navigation_report": output_dir / "A_SHARE_OWNER_ARTIFACT_NAVIGATION.md",
        "owner_dashboard_source_trace_report": output_dir / "A_SHARE_OWNER_DASHBOARD_SOURCE_TRACE.md",
    }
    reports["owner_dashboard_compact_report"].write_text(render_compact_dashboard(payload), encoding="utf-8")
    if not compact_only:
        reports["owner_dashboard_report"].write_text(render_owner_dashboard(payload), encoding="utf-8")
        reports["owner_warning_blocker_report"].write_text(render_warning_blocker(payload), encoding="utf-8")
        reports["owner_artifact_navigation_report"].write_text(render_navigation(payload), encoding="utf-8")
        reports["owner_dashboard_source_trace_report"].write_text(render_source_trace(payload), encoding="utf-8")
    return reports


def render_owner_dashboard(payload: dict[str, Any]) -> str:
    summary = payload["dashboard_summary"]
    executive = payload["executive_status_card"]
    freshness = payload["data_freshness_card"]
    provider = payload["provider_health_card"]
    workflow = payload["workflow_status_card"]
    research = payload["research_output_card"]
    candidates = payload["candidate_summary_card"]
    portfolio = payload["portfolio_summary_card"]
    benchmark = payload["benchmark_summary_card"]
    performance = payload["performance_summary_card"]
    attribution = payload["attribution_summary_card"]
    warnings = payload["warning_and_blocker_card"]
    nav = payload["artifact_navigation_index"]
    boundary = payload["dashboard_boundary_check"]
    trace = payload["dashboard_source_trace"]
    lines = [
        "# A Share Owner Dashboard",
        "",
        f"- As of date: {summary['as_of_date']}",
        f"- Resolved as of date: {summary['resolved_as_of_date']}",
        f"- Overall status: {summary['overall_status']}",
        f"- Warning count: {summary['warning_count']}",
        f"- Blocking count: {summary['blocking_count']}",
        "- Scope: owner-facing research monitoring only; not order instruction; no broker connection; no real orders.",
        "",
        "## 1. Executive Status",
        f"- Status: {executive['status_label_zh']} / {executive['overall_status']}",
        f"- Briefing: {executive['briefing_status']}",
        f"- Tracking: {executive['tracking_status']}",
        f"- Benchmark: {executive['benchmark_status']}",
        f"- Performance: {executive['performance_status']}",
        f"- Attribution: {executive['attribution_status']}",
        "",
        "## 2. Data Freshness",
        f"- Data refresh audit passed: {freshness.get('data_refresh_audit_passed')}",
        f"- Freshness status: {freshness.get('freshness_validation_status')}",
        f"- Coverage status: {freshness.get('coverage_validation_status')}",
        f"- Gap count: {freshness.get('gap_count')}",
        "",
        "## 3. Provider Health",
        f"- Providers: {provider.get('provider_count')} total, {provider.get('enabled_provider_count')} enabled",
        f"- Enabled providers: {_join(provider.get('enabled_providers', []))}",
        f"- Disabled providers: {_join(provider.get('disabled_providers', []))}",
        f"- Network providers disabled: {provider.get('network_providers_disabled')}",
        "",
        "## 4. Workflow Status",
        f"- Current-day audit passed: {workflow.get('current_day_run_audit_passed')}",
        f"- Workflow audit passed: {workflow.get('workflow_audit_passed')}",
        f"- Workflow mode: {workflow.get('workflow_mode')}",
        f"- Old run-daily called: {workflow.get('old_run_daily_called')}",
        f"- Day2 executed: {workflow.get('day2_executed')}",
        "",
        "## 5. Research Outputs",
    ]
    for row in research.get("outputs", []):
        lines.append(f"- {row.get('artifact_id')}: {row.get('status')} ({row.get('path')})")
    lines.extend(
        [
            "",
            "## 6. Candidate Summary",
            f"- Long candidates: {candidates.get('long_candidate_count')}",
            f"- Mid candidates: {candidates.get('mid_candidate_count')}",
            f"- Short candidates: {candidates.get('short_candidate_count')}",
            f"- Extended watch pool: {candidates.get('extended_watch_pool_count')}",
            f"- Risk downgraded: {candidates.get('risk_downgraded_count')}",
            f"- Top long symbols: {_join(candidates.get('top10_symbols', {}).get('long', []))}",
            "",
            "## 7. Portfolio Summary",
            f"- Portfolio count: {portfolio.get('portfolio_count')}",
            f"- Performance observed: {portfolio.get('performance_observed')}",
            f"- Included risk-downgraded symbols: {_join(portfolio.get('risk_downgraded_symbols_included', []))}",
            "",
            "## 8. Benchmark Summary",
            f"- Status: {benchmark.get('status')}",
            f"- First-day initialization: {benchmark.get('first_day_initialization')}",
            f"- Available benchmarks: {_join(benchmark.get('available_benchmarks', []))}",
            "",
            "## 9. Performance Summary",
            f"- Status: {performance.get('status')}",
            f"- Observation count: {performance.get('portfolio_observation_count')} / {performance.get('minimum_required_observations')}",
            f"- Sufficient history: {performance.get('sufficient_history')}",
            "",
            "## 10. Attribution Summary",
            f"- Status: {attribution.get('status')}",
            f"- Structural diagnostics available: {attribution.get('structural_diagnostics_available')}",
            f"- Realized attribution available: {attribution.get('realized_performance_attribution_available')}",
            "",
            "## 11. Warning And Blocker Summary",
            f"- Blocking count: {warnings.get('blocking_count')}",
            f"- Warning count: {warnings.get('warning_count')}",
        ]
    )
    lines.extend([f"- Warning: {item}" for item in warnings.get("warnings", [])[:20]])
    lines.extend(
        [
            "",
            "## 12. Artifact Navigation",
            f"- Artifact count: {nav.get('artifact_count')}",
        ]
    )
    for row in nav.get("artifacts", []):
        lines.append(f"- {row.get('artifact_id')}: {row.get('path')} (exists={row.get('exists')})")
    lines.extend(
        [
            "",
            "## 13. Source Trace And Boundary",
            f"- Source trace complete: {trace.get('source_trace_complete')}",
            f"- Boundary passed: {boundary.get('overall_passed')}",
            f"- Forbidden artifacts: {_join(boundary.get('forbidden_artifacts_present', []))}",
            "- Boundary statement: research-only, virtual-only, no order preview, no broker, no real account data, no live execution.",
            "",
        ]
    )
    return "\n".join(lines)


def render_compact_dashboard(payload: dict[str, Any]) -> str:
    summary = payload["dashboard_summary"]
    executive = payload["executive_status_card"]
    warnings = payload["warning_and_blocker_card"]
    candidates = payload["candidate_summary_card"]
    lines = [
        "# A Share Owner Dashboard Compact",
        f"As of {summary['as_of_date']} / resolved {summary['resolved_as_of_date']}.",
        f"Status: {executive['overall_status']} ({executive['status_label_zh']}).",
        f"Warnings: {warnings.get('warning_count')}; blockers: {warnings.get('blocking_count')}.",
        f"Candidates long/mid/short: {candidates.get('long_candidate_count')}/{candidates.get('mid_candidate_count')}/{candidates.get('short_candidate_count')}.",
        f"Tracking: {executive.get('tracking_status')}; benchmark: {executive.get('benchmark_status')}; performance: {executive.get('performance_status')}; attribution: {executive.get('attribution_status')}.",
        "Boundary: research monitoring only, virtual portfolio only, no broker, no order preview, no real orders.",
    ]
    return "\n".join(lines)[:1200]


def render_warning_blocker(payload: dict[str, Any]) -> str:
    card = payload["warning_and_blocker_card"]
    lines = [
        "# A Share Owner Warning And Blocker Summary",
        "",
        f"- Blocking count: {card.get('blocking_count')}",
        f"- Warning count: {card.get('warning_count')}",
        f"- Critical warning count: {card.get('critical_warning_count')}",
        "",
        "## Blocking Reasons",
    ]
    lines.extend([f"- {item}" for item in card.get("blocking_reasons", [])] or ["- None"])
    lines.extend(["", "## Warnings"])
    lines.extend([f"- {item}" for item in card.get("warnings", [])] or ["- None"])
    lines.extend(["", "## Carry Forward Decisions"])
    lines.extend([f"- {item}" for item in card.get("known_non_blocking_warnings", [])] or ["- None"])
    return "\n".join(lines) + "\n"


def render_navigation(payload: dict[str, Any]) -> str:
    nav = payload["artifact_navigation_index"]
    lines = ["# A Share Owner Artifact Navigation", "", f"- Artifact count: {nav.get('artifact_count')}", ""]
    for row in nav.get("artifacts", []):
        lines.append(f"- {row.get('artifact_id')} | {row.get('label_zh')} | {row.get('path')} | exists={row.get('exists')}")
    return "\n".join(lines) + "\n"


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["dashboard_source_trace"]
    lines = [
        "# A Share Owner Dashboard Source Trace",
        "",
        f"- Source trace complete: {trace.get('source_trace_complete')}",
        f"- Forbidden path hits: {_join(trace.get('forbidden_path_hits', []))}",
        "",
        "## Sources",
    ]
    for row in trace.get("source_artifacts", []):
        lines.append(f"- {row.get('path')} | exists={row.get('exists')} | sha256={row.get('sha256')}")
    lines.extend(["", "## Outputs"])
    for row in trace.get("output_artifacts", []):
        lines.append(f"- {row.get('path')} | exists={row.get('exists')} | sha256={row.get('sha256')}")
    return "\n".join(lines) + "\n"


def render_audit(audit: dict[str, Any]) -> str:
    lines = [
        "# A Share Owner Dashboard Audit",
        "",
        f"- Overall passed: {audit.get('overall_passed')}",
        f"- Blocking reasons: {_join(audit.get('blocking_reasons', []))}",
        f"- Warning count: {len(audit.get('warnings', []))}",
        f"- Recommended next version: {audit.get('recommended_next_version')}",
        "",
        "## Checks",
    ]
    for key, value in audit.get("checks", {}).items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) + "\n"


def _join(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values) if values else "None"
