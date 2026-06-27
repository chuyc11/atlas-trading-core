"""Markdown reports for v0.7.5 candidate generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_selection.candidate_config import CANDIDATE_REPORTS
from trading_core.equity_selection.filter_inputs import selection_output_dir
from trading_core.storage.file_paths import ProjectPaths


def write_candidate_reports(paths: ProjectPaths, as_of_date: str, payload: dict[str, Any]) -> dict[str, str]:
    out_dir = selection_output_dir(paths, as_of_date)
    out_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "long_candidates_report": _horizon_report("Long Candidates", payload["long_candidates"], "LongScore"),
        "mid_candidates_report": _horizon_report("Mid Candidates", payload["mid_candidates"], "MidScore"),
        "short_candidates_report": _horizon_report("Short Candidates", payload["short_candidates"], "ShortScore"),
        "multi_horizon_candidates_report": _multi_report(payload["multi_horizon_candidates"]),
        "risk_downgraded_candidates_report": _risk_report(payload["risk_downgraded_candidates"]),
        "candidate_generation_summary_report": _summary_report(payload),
    }
    written = {}
    for key, content in reports.items():
        path = out_dir / CANDIDATE_REPORTS[key]
        path.write_text(content, encoding="utf-8")
        written[key] = str(path)
    return written


def _horizon_report(title: str, rows: list[dict[str, Any]], score_column: str) -> str:
    lines = [
        f"# {title}",
        "",
        "These are research candidates only. They are not investment advice, buy/sell signals, order instructions, portfolio actions, or profit guarantees.",
        "",
        "## Top 10",
        "",
        "| Rank | Symbol | Name | Score | RiskScore | LiquidityScore | Reasons | Risk Notes |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in rows[:10]:
        lines.append(
            f"| {row['candidate_rank']} | {row['symbol']} | {row.get('name','')} | {_fmt(row.get(score_column))} | {_fmt(row.get('RiskScore'))} | {_fmt(row.get('LiquidityScore'))} | {row.get('primary_inclusion_reasons','')} | {row.get('main_risk_reasons','')} |"
        )
    lines.extend(["", f"Total records: {len(rows)}"])
    return "\n".join(lines) + "\n"


def _multi_report(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Multi-Horizon Candidates",
        "",
        "These rows show multi-horizon score overlap for research review only. They are not buy/sell signals or order instructions.",
        "",
        "| Rank | Symbol | Name | Overlap | Best Horizon | CompositeScore | Risk Notes |",
        "|---|---|---|---|---|---:|---|",
    ]
    for index, row in enumerate(rows[:10], start=1):
        lines.append(
            f"| {index} | {row['symbol']} | {row.get('name','')} | {row.get('horizon_overlap_type','')} | {row.get('best_horizon','')} | {_fmt(row.get('CompositeOpportunityScore'))} | {row.get('risk_notes','')} |"
        )
    lines.extend(["", f"Total records: {len(rows)}"])
    return "\n".join(lines) + "\n"


def _risk_report(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Risk-Downgraded Candidates",
        "",
        "These rows had high horizon scores but were downgraded for risk, liquidity, or confidence reasons. They are not strict candidates and are not trade instructions.",
        "",
        "| Symbol | Name | Trigger Horizon | Trigger Score | Downgrade Reason | RiskScore | LiquidityScore |",
        "|---|---|---|---:|---|---:|---:|",
    ]
    for row in rows[:20]:
        lines.append(
            f"| {row['symbol']} | {row.get('name','')} | {row.get('trigger_horizon','')} | {_fmt(row.get('trigger_score'))} | {row.get('downgrade_reason','')} | {_fmt(row.get('RiskScore'))} | {_fmt(row.get('LiquidityScore'))} |"
        )
    lines.extend(["", f"Total records: {len(rows)}"])
    return "\n".join(lines) + "\n"


def _summary_report(payload: dict[str, Any]) -> str:
    counts = payload["candidate_counts"]
    boundary = payload["boundary"]
    lines = [
        "# Candidate Generation Summary",
        "",
        f"- as_of_date: {payload['as_of_date']}",
        f"- strict_tradable_count: {payload['strict_tradable_count']}",
        f"- scored_symbols: {payload['scored_symbols']}",
        f"- candidate_counts: {counts}",
        f"- recommended_next_version: {payload['recommended_next_version']}",
        "",
        "## Boundary",
        f"- candidate_generation_only: {str(boundary['candidate_generation_only']).lower()}",
        f"- candidates_generated: {str(boundary['candidates_generated']).lower()}",
        f"- watchlists_generated: {str(boundary['watchlists_generated']).lower()}",
        f"- virtual_portfolio_generated: {str(boundary['virtual_portfolio_generated']).lower()}",
        f"- buy_sell_signals_generated: {str(boundary['buy_sell_signals_generated']).lower()}",
        f"- order_preview_generated: {str(boundary['order_preview_generated']).lower()}",
        f"- run_daily_called: {str(boundary['run_daily_called']).lower()}",
        f"- broker_connected: {str(boundary['broker_connected']).lower()}",
        f"- real_orders_placed: {str(boundary['real_orders_placed']).lower()}",
        f"- model_profit_guaranteed: {str(boundary['model_profit_guaranteed']).lower()}",
        f"- live_trading_ready: {str(boundary['live_trading_ready']).lower()}",
        "",
        "Candidates are research inputs only. Virtual portfolios are deferred to v0.7.6.",
    ]
    return "\n".join(lines) + "\n"


def _fmt(value: Any) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return ""
