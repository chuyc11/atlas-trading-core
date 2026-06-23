"""Backtest report formatting."""

from __future__ import annotations

from typing import Any


def format_backtest_report(summary: dict[str, Any]) -> str:
    lines = [
        f"# Backtest {summary.get('start_date')} to {summary.get('end_date')}",
        "",
        f"- Days: {summary.get('days')}",
        f"- Start asset: {summary.get('start_asset')}",
        f"- End asset: {summary.get('end_asset')}",
        f"- Total return: {summary.get('total_return')}",
        "",
        summary.get("pit_note", ""),
    ]
    return "\n".join(lines)
