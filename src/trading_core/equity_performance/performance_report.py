"""Markdown reports for A-share multi-day performance tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_performance.performance_config import PERFORMANCE_REPORTS


def write_performance_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {key: output_dir / filename for key, filename in PERFORMANCE_REPORTS.items()}
    reports["performance_summary_report"].write_text(render_performance_summary(payload), encoding="utf-8")
    reports["portfolio_nav_return_report"].write_text(render_nav_return_series(payload), encoding="utf-8")
    reports["portfolio_relative_performance_report"].write_text(render_relative_performance(payload), encoding="utf-8")
    reports["performance_limitations_report"].write_text(render_limitations(payload), encoding="utf-8")
    reports["performance_source_trace_report"].write_text(render_source_trace(payload), encoding="utf-8")
    return {key: str(path) for key, path in reports.items()}


def render_performance_summary(payload: dict[str, Any]) -> str:
    summary = payload["performance_summary"]
    lines = [
        "# A Share Multi-Day Performance Summary",
        "",
        "## 总体结论",
        f"- 数据日期: {summary['as_of_date']}",
        f"- 跟踪起始日期: {summary['tracking_start_date']}",
        f"- 可用观测数: {summary['portfolio_observation_count']}",
        f"- 是否足够形成多日绩效判断: {str(summary['sufficient_history']).lower()}",
        f"- first_day_initialization: {str(summary['first_day_initialization']).lower()}",
        f"- performance_not_yet_observed: {str(summary['performance_not_yet_observed']).lower()}",
        "",
        "## Portfolios",
        "| Portfolio | NAV | Daily Return | Cumulative Return | Drawdown | Max Drawdown | Holdings |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for portfolio_id, row in summary["portfolios"].items():
        lines.append(
            f"| {portfolio_id} | {_fmt(row['nav'])} | {_fmt(row['daily_return'])} | {_fmt(row['cumulative_return'])} | {_fmt(row['drawdown'])} | {_fmt(row['max_drawdown'])} | {row['holding_count']} |"
        )
    lines.extend(
        [
            "",
            "## Benchmark-Relative Status",
        ]
    )
    for portfolio_id, row in summary["portfolios"].items():
        lines.append(f"- {portfolio_id}: {row['benchmark_relative_status']}")
    lines.extend(
        [
            "",
            "## Limited History",
            "- Current portfolio tracking has limited observations.",
            "- First-day initialization is not evidence of strategy performance.",
            "- Benchmark history may be available, but portfolio realized virtual history is limited.",
            "",
            "## Boundary",
            "- research_only: true.",
            "- virtual_only: true.",
            "- broker_connected: false.",
            "- real_orders_placed: false.",
            "- buy_sell_signals_generated: false.",
            "- order_preview_generated: false.",
            "- run_daily_called: false.",
            "- day2_executed: false.",
            "- model_profit_guaranteed: false.",
            "- live_trading_ready: false.",
            "",
            f"Recommended next version: {summary['recommended_next_version']}",
            "",
            summary["disclaimer"],
            "",
        ]
    )
    return "\n".join(lines)


def render_nav_return_series(payload: dict[str, Any]) -> str:
    returns = payload["portfolio_return_series"]["records"]
    drawdowns = {
        (row["portfolio_id"], row["as_of_date"]): row
        for row in payload["portfolio_drawdown_series"]["records"]
    }
    lines = [
        "# Portfolio NAV and Return Series",
        "",
        "| Portfolio | Date | NAV | Daily Return | Cumulative Return | Drawdown | Max Drawdown | Status |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in returns:
        drawdown = drawdowns.get((row["portfolio_id"], row["as_of_date"]), {})
        lines.append(
            f"| {row['portfolio_id']} | {row['as_of_date']} | {_fmt(row['nav'])} | {_fmt(row['daily_return'])} | {_fmt(row['cumulative_return'])} | {_fmt(drawdown.get('drawdown'))} | {_fmt(drawdown.get('max_drawdown'))} | {row['metric_status']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_relative_performance(payload: dict[str, Any]) -> str:
    lines = [
        "# Portfolio Relative Performance",
        "",
        "| Portfolio | Benchmark | Date | Portfolio Daily | Benchmark Daily | Excess Daily | Portfolio Cum | Benchmark Cum | Excess Cum | Status |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["portfolio_relative_performance_series"]["records"]:
        lines.append(
            f"| {row['portfolio_id']} | {row['benchmark_id']} | {row['as_of_date']} | {_fmt(row['portfolio_daily_return'])} | {_fmt(row['benchmark_daily_return'])} | {_fmt(row['excess_daily_return'])} | {_fmt(row['portfolio_cumulative_return'])} | {_fmt(row['benchmark_cumulative_return'])} | {_fmt(row['excess_cumulative_return'])} | {row['metric_status']} |"
        )
    lines.extend(["", "- Limited-history rows are intentionally not interpreted as strategy performance.", ""])
    return "\n".join(lines)


def render_limitations(payload: dict[str, Any]) -> str:
    limitations = payload["performance_limitations"]
    lines = [
        "# Performance Limitations",
        "",
        f"- portfolio_observation_count: {limitations['portfolio_observation_count']}",
        f"- minimum_required_observations: {limitations['minimum_required_observations']}",
        f"- insufficient_history: {str(limitations['insufficient_history']).lower()}",
        "",
    ]
    lines.extend(f"- {item}" for item in limitations["limitations"])
    lines.append("")
    return "\n".join(lines)


def render_source_trace(payload: dict[str, Any]) -> str:
    trace = payload["performance_source_trace"]
    lines = [
        "# Performance Source Trace",
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


def render_performance_audit(payload: dict[str, Any]) -> str:
    lines = [
        "# A-Share Multi-Day Performance Audit",
        "",
        f"- target_version: {payload['target_version']}",
        f"- as_of_date: {payload['as_of_date']}",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {len(payload['warnings'])}",
        "",
        "## Observation Checks",
    ]
    for key, value in payload["observation_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Boundary",
            "- Multi-day performance tracking only.",
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
