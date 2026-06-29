"""Warning aggregation for current-day research runs."""

from __future__ import annotations

from typing import Any

from trading_core.equity_current_day.current_day_config import KNOWN_DATA_REFRESH_WARNINGS, TARGET_VERSION


def build_current_day_warning_summary(
    *,
    as_of_date: str,
    resolved_as_of_date: str,
    data_refresh_warnings: list[str],
    workflow_warnings: list[str],
    benchmark_warnings: list[str] | None = None,
    performance_warnings: list[str] | None = None,
    attribution_warnings: list[str] | None = None,
    runner_warnings: list[str] | None = None,
) -> dict[str, Any]:
    records = []
    for source, warnings in [
        ("data_refresh", data_refresh_warnings),
        ("workflow", workflow_warnings),
        ("benchmark", benchmark_warnings or []),
        ("performance", performance_warnings or []),
        ("attribution", attribution_warnings or []),
        ("current_day_runner", runner_warnings or []),
    ]:
        for warning in warnings:
            records.append(
                {
                    "source": source,
                    "warning": warning,
                    "classification": "known_non_blocking" if warning in KNOWN_DATA_REFRESH_WARNINGS else "warning",
                }
            )
    blocking = [row for row in records if row["classification"] == "blocking"]
    return {
        "warning_summary_id": "A-SHARE-CURRENT-DAY-WARNING-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "warnings": records,
        "warning_count": len(records),
        "blocking_warning_count": len(blocking),
        "known_warnings_carried_forward": [row["warning"] for row in records if row["classification"] == "known_non_blocking"],
        "overall_passed": not blocking,
        "blocking_reasons": [row["warning"] for row in blocking],
    }

