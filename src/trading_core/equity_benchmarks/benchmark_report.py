"""Markdown reports for A-share benchmark comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_benchmarks.benchmark_config import BENCHMARK_REPORTS, PORTFOLIO_IDS


def write_benchmark_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        key: output_dir / filename
        for key, filename in BENCHMARK_REPORTS.items()
    }
    reports["benchmark_summary_report"].write_text(render_benchmark_summary(payload), encoding="utf-8")
    reports["portfolio_benchmark_comparison_report"].write_text(render_portfolio_comparison(payload), encoding="utf-8")
    reports["benchmark_data_availability_report"].write_text(render_data_availability(payload), encoding="utf-8")
    reports["benchmark_source_trace_report"].write_text(render_source_trace(payload), encoding="utf-8")
    return {key: str(path) for key, path in reports.items()}


def render_benchmark_summary(payload: dict[str, Any]) -> str:
    summary = payload["benchmark_summary"]
    availability = payload["benchmark_data_availability"]["benchmarks"]
    lines = [
        "# A Share Benchmark Summary",
        "",
        "## 总体结论",
        f"- 数据日期: {summary['as_of_date']}",
        f"- benchmark 数量: {len(summary['benchmark_ids'])}",
        f"- first_day_initialization: {str(summary['first_day_initialization']).lower()}",
        f"- performance_not_yet_observed: {str(summary['performance_not_yet_observed']).lower()}",
        f"- limited_history_flagged: {str(summary['limited_history_flagged']).lower()}",
        "",
        "## Benchmark Availability",
        "| Benchmark | Status | Days | Placeholder | Source |",
        "|---|---|---:|---|---|",
    ]
    for row in availability:
        lines.append(f"| {row['benchmark_id']} | {row['status']} | {row['trading_days_available']} | {str(row['is_placeholder']).lower()} | {row['source_type']} |")
    lines.extend(
        [
            "",
            "## 当前比较限制",
            "- 当前组合跟踪仍处在首日初始化状态，组合层面的多日相对表现尚未被观测。",
            "- 指数与等权 benchmark 的历史序列可以用于基准参照，但不应被解释为投资结论。",
            "- tracking error、information ratio、correlation 会在组合历史达到最小天数后再启用。",
            "",
            "## Boundary",
            "- research_only: true.",
            "- virtual_only: true.",
            "- broker_connected: false.",
            "- real_orders_placed: false.",
            "- run_daily_called: false.",
            "- day2_executed: false.",
            "- model_profit_guaranteed: false.",
            "- live_trading_ready: false.",
            "",
            f"Next recommended version: {summary['recommended_next_version']}",
            "",
        ]
    )
    return "\n".join(lines)


def render_portfolio_comparison(payload: dict[str, Any]) -> str:
    comparison = payload["portfolio_benchmark_comparison"]
    lines = ["# Portfolio Benchmark Comparison", ""]
    for portfolio_id in PORTFOLIO_IDS.values():
        lines.extend(
            [
                f"## {portfolio_id}",
                "",
                "| Benchmark | Portfolio Daily | Benchmark Daily | Excess Daily | Portfolio Cum | Benchmark Cum | Excess Cum | Status |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in comparison["comparisons"]:
            if row["portfolio_id"] != portfolio_id:
                continue
            lines.append(
                f"| {row['benchmark_id']} | {_fmt(row['portfolio_daily_return'])} | {_fmt(row['benchmark_daily_return'])} | {_fmt(row['excess_daily_return'])} | {_fmt(row['portfolio_cumulative_return'])} | {_fmt(row['benchmark_cumulative_return'])} | {_fmt(row['excess_cumulative_return'])} | {row['comparison_status']} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Caveats",
            "- limited_history means the portfolio side has not accumulated enough observed days for tracking error, information ratio, or correlation.",
            "- No multi-day portfolio performance is fabricated.",
            "",
        ]
    )
    return "\n".join(lines)


def render_data_availability(payload: dict[str, Any]) -> str:
    availability = payload["benchmark_data_availability"]["benchmarks"]
    exclusions = payload["benchmark_exclusion_report"]["benchmarks"]
    lines = [
        "# Benchmark Data Availability",
        "",
        "| Benchmark | Status | First | Last | Days | As-Of Available | Missing Reason |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in availability:
        lines.append(
            f"| {row['benchmark_id']} | {row['status']} | {row['first_available_date']} | {row['last_available_date']} | {row['trading_days_available']} | {str(row['as_of_date_available']).lower()} | {row['missing_reason']} |"
        )
    lines.extend(["", "## Equal-Weight Exclusions", ""])
    for row in exclusions:
        lines.append(f"- {row['benchmark_id']}: constituents={row['constituent_count']}, excluded={row['excluded_constituent_count']}, reasons={row['exclusion_reasons']}")
    lines.extend(["", "## Cash Assumption", "- CASH uses 0.0 daily return for v0.7.10.", ""])
    return "\n".join(lines)


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["benchmark_source_trace"]
    lines = [
        "# Benchmark Source Trace",
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
    lines.extend(["", "## Index Source", f"- {trace['index_benchmark_source']}", ""])
    return "\n".join(lines)


def render_benchmark_audit(payload: dict[str, Any]) -> str:
    lines = [
        "# A-Share Benchmark Comparison Audit",
        "",
        f"- target_version: {payload['target_version']}",
        f"- as_of_date: {payload['as_of_date']}",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {len(payload['warnings'])}",
        "",
        "## Benchmark Availability",
    ]
    for benchmark_id, status in payload["benchmark_availability_checks"].items():
        lines.append(f"- {benchmark_id}: {status}")
    lines.extend(
        [
            "",
            "## Boundary",
            "- Benchmark comparison only.",
            "- Research-only and virtual-only.",
            "- Broker connected: false.",
            "- Real orders placed: false.",
            "- Buy/sell signals generated: false.",
            "- Order preview generated: false.",
            "- run-daily called: false.",
            "- Day2 executed: false.",
            "- Model profit guaranteed: false.",
            "- Live trading ready: false.",
            "",
            f"Recommended next version: {payload['recommended_next_version']}",
            "",
        ]
    )
    return "\n".join(lines)


def _fmt(value: Any) -> str:
    if value is None:
        return "null"
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return str(value)
