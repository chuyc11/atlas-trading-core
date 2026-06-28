"""Markdown reports for A-share data refresh."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import DATA_REFRESH_REPORTS


def write_data_refresh_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {key: output_dir / filename for key, filename in DATA_REFRESH_REPORTS.items()}
    reports["data_refresh_summary_report"].write_text(render_summary(payload), encoding="utf-8")
    reports["provider_health_report"].write_text(render_provider_health(payload), encoding="utf-8")
    reports["dataset_coverage_report"].write_text(render_coverage(payload), encoding="utf-8")
    reports["data_gap_report_md"].write_text(render_gap_report(payload), encoding="utf-8")
    reports["data_refresh_source_trace_report"].write_text(render_source_trace(payload), encoding="utf-8")
    return {key: str(path) for key, path in reports.items()}


def render_summary(payload: dict[str, Any]) -> str:
    summary = payload["data_refresh_summary"]
    lines = [
        "# A Share Data Refresh Summary",
        "",
        "## 总体结论",
        f"- 数据日期: {summary['as_of_date']}",
        f"- 刷新模式: {summary['mode']}",
        f"- resolved_as_of_date: {summary['resolved_as_of_date']}",
        f"- provider summary: {summary['provider_summary']}",
        "",
        "## Dataset Status Table",
        "| Dataset | Status |",
        "|---|---|",
    ]
    for dataset_id, status in summary["dataset_status"].items():
        lines.append(f"| {dataset_id} | {status} |")
    lines.extend(
        [
            "",
            f"- schema validation summary: {summary['schema_validation_status']}",
            f"- freshness validation summary: {summary['freshness_validation_status']}",
            f"- coverage summary: {summary['coverage_validation_status']}",
            f"- data gaps: {summary['data_gaps']}",
            f"- fallback decisions: fallback_used={summary['fallback_used']}",
            f"- boundary summary: {summary['boundary']}",
            f"- warnings: {summary['warnings']}",
            f"- blocking reasons: {summary['blocking_reasons']}",
            f"- recommended next version: {summary['recommended_next_version']}",
            "",
            f"Disclaimer: {summary['disclaimer']}",
            "",
        ]
    )
    return "\n".join(lines)


def render_provider_health(payload: dict[str, Any]) -> str:
    lines = ["# Provider Health Check", "", "| Provider | Enabled | Health | Fallback | Error |", "|---|---|---|---|---|"]
    for row in payload["provider_health_check"]["providers"]:
        lines.append(f"| {row['provider_id']} | {row['enabled']} | {row['current_attempt_status']} | {row['fallback_used']} | {row.get('error_message') or ''} |")
    lines.extend(["", f"Network usage summary: {payload['provider_health_check']['network_usage_summary']}", ""])
    return "\n".join(lines)


def render_coverage(payload: dict[str, Any]) -> str:
    coverage = payload["dataset_coverage_summary"]
    lines = ["# Dataset Coverage Summary", "", "| Dataset | Symbols | Coverage vs Equity Master | Threshold Passed |", "|---|---:|---:|---|"]
    for dataset_id, row in coverage["datasets"].items():
        lines.append(f"| {dataset_id} | {row['symbol_count']} | {_fmt(row['coverage_vs_equity_master'])} | {row['threshold_passed']} |")
    lines.extend(["", f"Critical missing count: {coverage['critical_missing_count']}", ""])
    return "\n".join(lines)


def render_gap_report(payload: dict[str, Any]) -> str:
    gap = payload["data_gap_report"]
    lines = [
        "# Data Gap Report",
        "",
        f"- missing datasets: {gap['missing_datasets']}",
        f"- missing dates: {gap['missing_dates']}",
        f"- missing fields: {gap['missing_fields']}",
        f"- lagged datasets: {gap['lagged_datasets']}",
        f"- stale datasets: {gap['stale_datasets']}",
        f"- provider failures: {gap['provider_failures']}",
        f"- recommended data fixes: {gap['recommended_data_fixes']}",
        "",
    ]
    return "\n".join(lines)


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["data_refresh_source_trace"]
    lines = ["# Data Refresh Source Trace", "", f"- source_trace_complete: {trace['source_trace_complete']}", f"- forbidden_source_path_hits: {trace['forbidden_source_path_hits']}", "", "| Path | Exists | SHA256 |", "|---|---|---|"]
    for row in trace["source_artifacts"]:
        lines.append(f"| {row['path']} | {row['exists']} | {row['sha256']} |")
    lines.append("")
    return "\n".join(lines)


def render_audit(payload: dict[str, Any]) -> str:
    lines = [
        "# A-Share Daily Data Refresh Audit",
        "",
        f"- target_version: {payload['target_version']}",
        f"- as_of_date: {payload['as_of_date']}",
        f"- mode: {payload['mode']}",
        f"- overall_passed: {payload['overall_passed']}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {len(payload['warnings'])}",
        "",
        "## Dataset Checks",
    ]
    for key, value in payload["dataset_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Boundary"])
    for key, value in payload["boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", f"Recommended next version: {payload['recommended_next_version']}", ""])
    return "\n".join(lines)


def _fmt(value: Any) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return str(value)
