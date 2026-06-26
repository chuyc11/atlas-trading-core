"""Build the day1 owner summary report."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_owner_report_common import (
    DAY1_AS_OF_DATE,
    LATEST_COMMON_LOCAL_DATA_DATE,
    RECOMMENDED_NEXT_VERSION,
    build_simple_markdown,
    key_numbers,
    load_day1_owner_report_context,
    paths_or_default,
    report_boundary,
    write_report_artifact,
)
from trading_core.storage.file_paths import ProjectPaths


def build_day1_owner_summary_report(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    context = load_day1_owner_report_context(paths)
    numbers = key_numbers(context)
    execution = context["payloads"].get("day1_virtual_execution_result", {})
    payload: dict[str, Any] = {
        "report_id": "FORWARD-DRY-RUN-DAY1-OWNER-SUMMARY-REPORT",
        "day_index": 1,
        "as_of_date": execution.get("as_of_date") or DAY1_AS_OF_DATE,
        "plain_language_summary": {
            "what_happened": "Day 1 used local authorized historical data to generate baseline strategy signals, create virtual order previews, and execute those orders only inside the isolated forward dry-run ledger.",
            "data_date": execution.get("as_of_date") or DAY1_AS_OF_DATE,
            "signals": f"{numbers['strategies_generated']} baseline strategies generated signals.",
            "orders_and_fills": f"{numbers['virtual_orders_total']} virtual orders produced {numbers['virtual_fills']} virtual fills and {numbers['virtual_rejects']} rejects.",
            "isolated_ledger": "The isolated forward dry-run ledger was written.",
            "main_ledger": "The main orders, trades, portfolio, and accounts ledgers were not written.",
            "broker": "No broker was connected and no real orders were placed.",
            "day2_blocker": f"Day 2 cannot continue because the latest common local market, benchmark, and risk proxy date is {LATEST_COMMON_LOCAL_DATA_DATE}, the same date already used by day 1.",
            "next_step": f"Extend the local authorized data horizon before retrying day2 in {RECOMMENDED_NEXT_VERSION}.",
        },
        "key_numbers": numbers,
        "boundary": {
            **report_boundary("owner_summary_only"),
            "virtual_forward_dry_run_only": True,
            "real_trading": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "main_ledger_written": False,
            "strategy_effectiveness_proven": False,
            "forward_dry_run_fully_validated": False,
            "live_trading_ready": False,
        },
    }
    lines = [
        f"- as_of_date: {payload['as_of_date']}",
        f"- strategies_generated: {numbers['strategies_generated']}",
        f"- virtual_orders_total: {numbers['virtual_orders_total']}",
        f"- virtual_fills: {numbers['virtual_fills']}",
        f"- virtual_rejects: {numbers['virtual_rejects']}",
        "- isolated_forward_dry_run_ledger_written: true",
        "- main_ledger_written: false",
        "- broker_connected: false",
        "- real_orders_placed: false",
        f"- day2_blocker: local data horizon stops at {LATEST_COMMON_LOCAL_DATA_DATE}",
        f"- recommended_next_version: {RECOMMENDED_NEXT_VERSION}",
    ]
    return write_report_artifact(paths, "day1_owner_summary_report.json", payload, "DAY1_OWNER_SUMMARY_REPORT.md", build_simple_markdown("Day1 Owner Summary Report", lines, payload))
