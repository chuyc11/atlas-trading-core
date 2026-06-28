"""Markdown reports for attribution diagnostics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_REPORTS
from trading_core.equity_attribution.attribution_limitations import LIMITATION_TEXT


def write_attribution_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {key: output_dir / filename for key, filename in ATTRIBUTION_REPORTS.items()}
    reports["attribution_summary_report"].write_text(render_attribution_summary(payload), encoding="utf-8")
    reports["holding_industry_report"].write_text(render_holding_industry(payload), encoding="utf-8")
    reports["score_risk_liquidity_report"].write_text(render_score_risk_liquidity(payload), encoding="utf-8")
    reports["benchmark_relative_report"].write_text(render_benchmark_relative(payload), encoding="utf-8")
    reports["attribution_limitations_report"].write_text(render_limitations(payload), encoding="utf-8")
    reports["attribution_source_trace_report"].write_text(render_source_trace(payload), encoding="utf-8")
    return {key: str(path) for key, path in reports.items()}


def render_attribution_summary(payload: dict[str, Any]) -> str:
    summary = payload["attribution_summary"]
    lines = [
        "# A Share Attribution Summary",
        "",
        "## 总体结论",
        f"- 数据日期: {summary['as_of_date']}",
        f"- 归因模式: {summary['mode']}",
        "- 当前历史限制: only one portfolio observation; realized multi-day attribution is not available.",
        "- long/mid/short 结构性归因摘要: structural exposure diagnostics are available for all virtual portfolios.",
        f"- 持仓贡献摘要: {summary['holding_count']} virtual holdings, contribution status is limited-history.",
        f"- 行业贡献摘要: {summary['industry_portfolios']}",
        f"- 评分桶贡献摘要: bucket edges {summary['score_bucket_edges']}",
        f"- 风险桶贡献摘要: risk downgraded symbols in portfolio {summary['risk_downgraded_symbols_in_portfolio']}",
        f"- 流动性桶贡献摘要: {summary['liquidity_portfolios']}",
        "- benchmark-relative attribution status: index constituent exposure unavailable for CSI benchmarks; equal-weight exposure is structural.",
        f"- 关键风险诊断: {summary['diagnostic_flags']}",
        "- 免责声明: attribution diagnostics are research-only virtual outputs and not investment advice.",
        f"- recommended next version: {summary['recommended_next_version']}",
        "",
    ]
    return "\n".join(lines)


def render_holding_industry(payload: dict[str, Any]) -> str:
    rows = payload["holding_contribution_snapshot"]["records"]
    lines = [
        "# Holding and Industry Attribution",
        "",
        "## Top Holdings by Weight",
        "| Portfolio | Symbol | Name | Weight | Contribution Status |",
        "|---|---|---|---:|---|",
    ]
    for row in sorted(rows, key=lambda item: -float(item.get("actual_weight") or 0.0))[:15]:
        lines.append(f"| {row['portfolio_id']} | {row['symbol']} | {row['name']} | {_fmt(row['actual_weight'])} | {row['contribution_status']} |")
    lines.extend(["", "## Top Holdings by Available Contribution", "- Realized contribution is limited-history for the current one-observation portfolio set.", "", "## Industry Exposure Table"])
    for portfolio_id, records in payload["industry_contribution_snapshot"]["portfolios"].items():
        lines.extend([f"### {portfolio_id}", "| Industry | Weight | Contribution Status |", "|---|---:|---|"])
        for row in records:
            lines.append(f"| {row['industry_level_1']} | {_fmt(row['weight'])} | {row['daily_contribution_status']} |")
    lines.extend(["", "## Unclassified Industry Notes", "- Missing industry values are mapped to Unclassified and surfaced in diagnostics.", ""])
    return "\n".join(lines)


def render_score_risk_liquidity(payload: dict[str, Any]) -> str:
    lines = ["# Score Risk Liquidity Diagnostics", ""]
    lines.append("## Score Bucket Exposure")
    _bucket_lines(lines, payload["score_bucket_contribution_snapshot"]["portfolios"])
    lines.append("## Risk Bucket Exposure")
    _bucket_lines(lines, payload["risk_bucket_contribution_snapshot"]["portfolios"])
    lines.append("## Liquidity Bucket Exposure")
    _bucket_lines(lines, payload["liquidity_bucket_contribution_snapshot"]["portfolios"])
    lines.extend(["## Weighted Average Scores"])
    for portfolio_id, row in payload["factor_exposure_snapshot"]["portfolios"].items():
        lines.append(f"- {portfolio_id}: {row}")
    lines.extend(["", "## Diagnostic Flags"])
    for portfolio_id, row in payload["portfolio_concentration_diagnostics"]["portfolios"].items():
        lines.append(f"- {portfolio_id}: {row['diagnostic_flags']}")
    lines.extend(
        [
            "",
            f"- risk downgrade exposure: {payload['risk_bucket_contribution_snapshot']['risk_downgraded_exposure']}",
            f"- low liquidity exposure: {payload['liquidity_diagnostics_snapshot']['portfolios']}",
            "",
        ]
    )
    return "\n".join(lines)


def render_benchmark_relative(payload: dict[str, Any]) -> str:
    lines = ["# Benchmark Relative Attribution", "", "| Portfolio | Benchmark | Status | Limitation |", "|---|---|---|---|"]
    for row in payload["benchmark_relative_attribution_snapshot"]["records"]:
        lines.append(f"| {row['portfolio_id']} | {row['benchmark_id']} | {row['benchmark_constituent_exposure_status']} | {row.get('limitation') or ''} |")
    lines.extend(
        [
            "",
            "- portfolio vs CSI300 attribution status: constituent exposure unavailable; return comparison remains limited-history.",
            "- portfolio vs CSI500 attribution status: constituent exposure unavailable; return comparison remains limited-history.",
            "- portfolio vs CSI1000 attribution status: constituent exposure unavailable; return comparison remains limited-history.",
            "- portfolio vs CASH attribution status: no constituent exposure applies.",
            "- portfolio vs EQUAL_WEIGHT_STRICT_TRADABLE attribution status: structural exposure is computed from available universe records.",
            "- portfolio vs EQUAL_WEIGHT_CANDIDATE_POOL attribution status: structural exposure is computed from candidate pool records.",
            "- limitations where benchmark constituent exposure is unavailable are recorded without fabricating benchmark holdings.",
            "",
        ]
    )
    return "\n".join(lines)


def render_limitations(payload: dict[str, Any]) -> str:
    lines = ["# Attribution Limitations", ""]
    lines.extend(f"- {item}" for item in LIMITATION_TEXT)
    lines.append("")
    return "\n".join(lines)


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["attribution_source_trace"]
    lines = [
        "# Attribution Source Trace",
        "",
        f"- source_trace_complete: {str(trace['source_trace_complete']).lower()}",
        f"- forbidden_source_path_hits: {trace['forbidden_source_path_hits']}",
        "",
        "## Sources",
        "| Path | Exists | SHA256 |",
        "|---|---|---|",
    ]
    for row in trace["source_artifacts"]:
        lines.append(f"| {row['path']} | {str(row['exists']).lower()} | {row['sha256']} |")
    lines.extend(["", "## Assumptions"])
    lines.extend(f"- {item}" for item in trace["assumptions"])
    lines.append("")
    return "\n".join(lines)


def render_attribution_audit(payload: dict[str, Any]) -> str:
    lines = [
        "# A-Share Performance Attribution Audit",
        "",
        f"- target_version: {payload['target_version']}",
        f"- as_of_date: {payload['as_of_date']}",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {len(payload['warnings'])}",
        "",
        "## Availability Checks",
    ]
    for key, value in payload["availability_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Reconciliation Checks"])
    for key, value in payload["reconciliation_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Boundary"])
    for key, value in payload["boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", f"Recommended next version: {payload['recommended_next_version']}", ""])
    return "\n".join(lines)


def _bucket_lines(lines: list[str], portfolios: dict[str, Any]) -> None:
    for portfolio_id, records in portfolios.items():
        lines.extend([f"### {portfolio_id}", "| Bucket | Weight | Count | Status |", "|---|---:|---:|---|"])
        for row in records:
            lines.append(f"| {row['bucket_label']} | {_fmt(row['weight'])} | {row['holding_count']} | {row['daily_contribution_status']} |")
        lines.append("")


def _fmt(value: Any) -> str:
    if value is None:
        return "null"
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return str(value)
