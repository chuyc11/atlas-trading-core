"""Weekly report placeholder for first-stage file output."""

from __future__ import annotations


def generate_weekly_report(start_date: str, end_date: str, summaries: list[dict[str, object]]) -> str:
    return "\n".join(
        [
            f"# 虚拟交易周报 {start_date} to {end_date}",
            "",
            f"- days: {len(summaries)}",
            "- status: first-stage summary placeholder",
        ]
    )
