"""Markdown reports for v0.7.6 A-share virtual portfolios."""

from __future__ import annotations

from typing import Any

from trading_core.equity_portfolios.portfolio_config import PORTFOLIO_REPORTS
from trading_core.equity_portfolios.portfolio_inputs import portfolio_output_dir
from trading_core.storage.file_paths import ProjectPaths


def write_portfolio_reports(paths: ProjectPaths, as_of_date: str, payload: dict[str, Any]) -> dict[str, str]:
    out_dir = portfolio_output_dir(paths, as_of_date)
    out_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "long_virtual_portfolio_report": _portfolio_report("Long Virtual Portfolio", payload["long_virtual_portfolio"], "LongScore"),
        "mid_virtual_portfolio_report": _portfolio_report("Mid Virtual Portfolio", payload["mid_virtual_portfolio"], "MidScore"),
        "short_virtual_portfolio_report": _portfolio_report("Short Virtual Portfolio", payload["short_virtual_portfolio"], "ShortScore", short=True),
        "portfolio_construction_summary_report": _summary_report(payload),
    }
    written = {}
    for key, content in reports.items():
        path = out_dir / PORTFOLIO_REPORTS[key]
        path.write_text(content, encoding="utf-8")
        written[key] = str(path)
    return written


def _portfolio_report(title: str, rows: list[dict[str, Any]], score_column: str, *, short: bool = False) -> str:
    lines = [
        f"# {title}",
        "",
        "research_only=true",
        "virtual_only=true",
        "not_investment_advice=true",
        "not_order_instruction=true",
        "not_profit_guarantee=true",
        "",
        "Virtual target weights are for research tracking only. They are not broker orders, not real-account rebalance instructions, and not profit guarantees.",
        "",
        "| Weight Rank | Symbol | Name | Target Weight | Score | RiskScore | LiquidityScore | Industry | Weight Reason |",
        "|---:|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['weight_rank']} | {row['symbol']} | {row.get('name','')} | {_pct(row.get('target_weight'))} | {_fmt(row.get(score_column))} | {_fmt(row.get('RiskScore'))} | {_fmt(row.get('LiquidityScore'))} | {row.get('industry','')} | {row.get('weight_reason','')} |"
        )
    if short:
        lines.extend(
            [
                "",
                "## Short Horizon Notes",
                "- overheat_risk_notes are retained in each record.",
                "- liquidity_risk_notes are retained in each record.",
                "- short_horizon_validity_notes are retained in each record.",
            ]
        )
    lines.extend(["", f"Total holdings: {len(rows)}", f"Weight sum: {_fmt(sum(float(row.get('target_weight') or 0.0) for row in rows))}"])
    return "\n".join(lines) + "\n"


def _summary_report(payload: dict[str, Any]) -> str:
    boundary = payload["boundary"]
    lines = [
        "# Portfolio Construction Summary",
        "",
        f"- as_of_date: {payload['as_of_date']}",
        f"- long_holdings: {len(payload['long_virtual_portfolio'])}",
        f"- mid_holdings: {len(payload['mid_virtual_portfolio'])}",
        f"- short_holdings: {len(payload['short_virtual_portfolio'])}",
        f"- recommended_next_version: {payload['recommended_next_version']}",
        "",
        "## Boundary",
        f"- virtual_portfolio_construction_only: {str(boundary['virtual_portfolio_construction_only']).lower()}",
        f"- virtual_portfolio_generated: {str(boundary['virtual_portfolio_generated']).lower()}",
        f"- real_portfolio_generated: {str(boundary['real_portfolio_generated']).lower()}",
        f"- buy_sell_signals_generated: {str(boundary['buy_sell_signals_generated']).lower()}",
        f"- order_preview_generated: {str(boundary['order_preview_generated']).lower()}",
        f"- run_daily_called: {str(boundary['run_daily_called']).lower()}",
        f"- broker_connected: {str(boundary['broker_connected']).lower()}",
        f"- real_orders_placed: {str(boundary['real_orders_placed']).lower()}",
        f"- model_profit_guaranteed: {str(boundary['model_profit_guaranteed']).lower()}",
        f"- live_trading_ready: {str(boundary['live_trading_ready']).lower()}",
        "",
        "Virtual portfolios are research-only inputs for future virtual tracking and the v0.7.7 daily briefing.",
    ]
    return "\n".join(lines) + "\n"


def _fmt(value: Any) -> str:
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return ""


def _pct(value: Any) -> str:
    try:
        return f"{float(value):.2%}"
    except (TypeError, ValueError):
        return ""

