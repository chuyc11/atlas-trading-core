"""Monthly report placeholder for first-stage file output."""

from __future__ import annotations


def generate_monthly_report(month: str, summaries: list[dict[str, object]]) -> str:
    return "\n".join(
        [
            f"# 虚拟交易月报 {month}",
            "",
            f"- days: {len(summaries)}",
            "- status: first-stage summary placeholder",
        ]
    )
