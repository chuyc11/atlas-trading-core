"""Markdown reporting for v0.7.8 virtual portfolio tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_portfolio_tracking.tracking_config import PORTFOLIO_HORIZONS, TRACKING_REPORTS


def write_tracking_reports(output_dir: Path, payload: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "tracking_summary_report": output_dir / TRACKING_REPORTS["tracking_summary_report"],
        "long_tracking_report": output_dir / TRACKING_REPORTS["long_tracking_report"],
        "mid_tracking_report": output_dir / TRACKING_REPORTS["mid_tracking_report"],
        "short_tracking_report": output_dir / TRACKING_REPORTS["short_tracking_report"],
        "benchmark_comparison_report": output_dir / TRACKING_REPORTS["benchmark_comparison_report"],
    }
    reports["tracking_summary_report"].write_text(render_tracking_summary(payload), encoding="utf-8")
    for key in ["long", "mid", "short"]:
        reports[f"{key}_tracking_report"].write_text(render_portfolio_tracking(payload, key), encoding="utf-8")
    reports["benchmark_comparison_report"].write_text(render_benchmark_comparison(payload), encoding="utf-8")
    return {key: str(path) for key, path in reports.items()}


def render_tracking_summary(payload: dict[str, Any]) -> str:
    summary = payload["tracking_summary"]
    nav = payload["portfolio_nav_snapshot"]["portfolios"]
    lines = [
        "# Virtual Portfolio Tracking Summary",
        "",
        f"- target_version: {summary['target_version']}",
        f"- as_of_date: {summary['as_of_date']}",
        f"- virtual_only: {str(summary['virtual_only']).lower()}",
        f"- research_only: {str(summary['research_only']).lower()}",
        f"- not_investment_advice: {str(summary['not_investment_advice']).lower()}",
        f"- not_order_instruction: {str(summary['not_order_instruction']).lower()}",
        f"- not_real_trade: {str(summary['not_real_trade']).lower()}",
        f"- not_profit_guarantee: {str(summary['not_profit_guarantee']).lower()}",
        f"- not_live_trading_ready: {str(summary['not_live_trading_ready']).lower()}",
        "",
        "## Portfolio NAV",
        "",
        "| Portfolio | Holdings | NAV | Cash | Weight Sum | Daily Return | Cumulative Return |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    perf = payload["portfolio_performance_snapshot"]["portfolios"]
    for key in ["long", "mid", "short"]:
        record = nav[key]
        performance = perf[key]
        lines.append(
            f"| {key} | {record['holding_count']} | {record['portfolio_nav']:.6f} | {record['cash_balance']:.6f} | {record['weight_sum']:.6f} | {performance['daily_return']:.6f} | {performance['cumulative_return']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "- Paper ledger is virtual-only and research-only.",
            "- Virtual holdings are not real holdings.",
            "- Virtual returns are not actual returns.",
            "- Buy/sell signal artifacts: false.",
            "- Order preview artifacts: false.",
            "- Broker connected: false.",
            "- Real orders placed: false.",
            "- run-daily called: false.",
            "- Day2 executed: false.",
            "- Model profit guaranteed: false.",
            "- Live trading ready: false.",
            "",
            f"Recommended next version: {summary['recommended_next_version']}",
            "",
        ]
    )
    return "\n".join(lines)


def render_portfolio_tracking(payload: dict[str, Any], key: str) -> str:
    holdings_snapshot = payload[f"{key}_holdings_snapshot"]
    nav = payload["portfolio_nav_snapshot"]["portfolios"][key]
    exposure = payload["portfolio_exposure_snapshot"]["portfolios"][key]
    lines = [
        f"# {PORTFOLIO_HORIZONS[key]} Virtual Portfolio Tracking",
        "",
        f"- as_of_date: {payload['tracking_summary']['as_of_date']}",
        f"- portfolio_id: {nav['portfolio_id']}",
        f"- virtual_only: {str(holdings_snapshot['virtual_only']).lower()}",
        f"- research_only: {str(holdings_snapshot['research_only']).lower()}",
        f"- not_order_instruction: {str(holdings_snapshot['not_order_instruction']).lower()}",
        f"- not_real_trade: {str(holdings_snapshot['not_real_trade']).lower()}",
        "",
        "## Metrics",
        f"- portfolio_nav: {nav['portfolio_nav']:.6f}",
        f"- cash_balance: {nav['cash_balance']:.6f}",
        f"- gross_exposure: {nav['gross_exposure']:.6f}",
        f"- net_exposure: {nav['net_exposure']:.6f}",
        f"- max_industry_weight: {exposure['max_industry_weight']:.6f}",
        f"- risk_score_weighted_avg: {_fmt(exposure['risk_score_weighted_avg'])}",
        f"- liquidity_score_weighted_avg: {_fmt(exposure['liquidity_score_weighted_avg'])}",
        "",
        "## Holdings",
        "",
        "| Symbol | Name | Target Weight | Actual Weight | Entry | Mark | Virtual Shares | Unrealized Return |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in holdings_snapshot["holdings"]:
        lines.append(
            f"| {row['symbol']} | {row['name']} | {row['target_weight']:.6f} | {row['actual_weight']:.6f} | {row['entry_price']:.6f} | {row['mark_price']:.6f} | {row['virtual_shares']:.6f} | {row['unrealized_return']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "- This report is a virtual tracking report.",
            "- It is not an order instruction.",
            "- It is not a real trade record.",
            "- It is not a profit guarantee.",
            "- Live trading ready: false.",
            "",
        ]
    )
    return "\n".join(lines)


def render_benchmark_comparison(payload: dict[str, Any]) -> str:
    snapshot = payload["benchmark_comparison_snapshot"]
    lines = [
        "# Benchmark Comparison",
        "",
        f"- as_of_date: {snapshot['as_of_date']}",
        f"- first_day_initialization: {str(snapshot['first_day_initialization']).lower()}",
        f"- performance_not_yet_observed: {str(snapshot['performance_not_yet_observed']).lower()}",
        f"- benchmark_data_available: {str(snapshot['benchmark_data_available']).lower()}",
        f"- benchmark_gap_reason: {snapshot['benchmark_gap_reason']}",
        "",
        "| Portfolio | Benchmark | Portfolio Return | Benchmark Return | Excess Return | Available | Gap Reason |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in snapshot["records"]:
        lines.append(
            f"| {row['portfolio_id']} | {row['benchmark']} | {_fmt(row['portfolio_return'])} | {_fmt(row['benchmark_return'])} | {_fmt(row['excess_return'])} | {str(row['benchmark_data_available']).lower()} | {row['benchmark_gap_reason']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "- Benchmark placeholders do not fabricate index prices.",
            "- First-day returns remain zero until later marks are observed.",
            "- This comparison is research-only.",
            "",
        ]
    )
    return "\n".join(lines)


def render_tracking_audit(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Virtual Portfolio Tracking Audit",
            "",
            f"- target_version: {payload['target_version']}",
            f"- as_of_date: {payload['as_of_date']}",
            f"- overall_passed: {str(payload['overall_passed']).lower()}",
            f"- blocking_reasons: {payload['blocking_reasons']}",
            f"- warnings: {len(payload['warnings'])}",
            f"- counts: {payload['counts']}",
            f"- nav_checks: {payload['nav_checks']}",
            "",
            "## Boundary",
            "- Virtual tracking only.",
            "- Paper ledger generated: true.",
            "- Real portfolio generated: false.",
            "- Buy/sell signals generated: false.",
            "- Order preview generated: false.",
            "- Official forward dry-run status unchanged.",
            "- Day2 executed: false.",
            "- run-daily called: false.",
            "- Broker connected: false.",
            "- Real orders placed: false.",
            "- Model profit guaranteed: false.",
            "- Live trading ready: false.",
            "",
            f"Recommended next version: {payload['recommended_next_version']}",
            "",
        ]
    )


def _fmt(value: Any) -> str:
    if value is None:
        return "null"
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return str(value)
