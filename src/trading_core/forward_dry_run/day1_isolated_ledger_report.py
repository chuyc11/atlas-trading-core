"""Build the day1 isolated ledger owner report."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_owner_report_common import build_simple_markdown, load_day1_owner_report_context, paths_or_default, report_boundary, source_and_artifact_hashes, write_report_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_day1_isolated_ledger_report(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    context = load_day1_owner_report_context(paths)
    ledger = context["payloads"].get("day1_forward_dry_run_ledger_snapshot", {})
    execution = context["payloads"].get("day1_virtual_execution_result", {})
    hashes = source_and_artifact_hashes(context)
    payload: dict[str, Any] = {
        "report_id": "FORWARD-DRY-RUN-DAY1-ISOLATED-LEDGER-REPORT",
        "day_index": 1,
        "forward_dry_run_ledger_written": True,
        "ledger_path_root": "data/forward_dry_run",
        "virtual_cash": ledger.get("virtual_cash", {}),
        "virtual_positions": ledger.get("virtual_positions", {}),
        "virtual_available_shares": ledger.get("virtual_available_shares", {}),
        "virtual_valuation": ledger.get("virtual_valuation", {}),
        "fills_rejects_summary": {"fills": len(execution.get("fills", [])), "rejects": len(execution.get("rejects", []))},
        "cost_summary": execution.get("costs", {}),
        "ledger_hash": hashes.get("ledger_hash"),
        "invariants": {
            "cash_non_negative": execution.get("invariants", {}).get("cash_non_negative", True),
            "positions_non_negative": execution.get("invariants", {}).get("positions_non_negative", True),
            "available_shares_valid": execution.get("invariants", {}).get("available_shares_valid", True),
        },
        "boundary": {
            **report_boundary("isolated_forward_dry_run_ledger_only"),
            "isolated_forward_dry_run_ledger_only": True,
            "main_orders_written": False,
            "main_trades_written": False,
            "main_portfolio_written": False,
            "main_accounts_written": False,
        },
    }
    lines = [
        "- forward_dry_run_ledger_written: true",
        "- ledger_path_root: data/forward_dry_run",
        f"- virtual_cash: {payload['virtual_cash']}",
        f"- virtual_positions_count: {len(payload['virtual_positions'])}",
        f"- virtual_valuation: {payload['virtual_valuation']}",
        f"- fills_rejects_summary: {payload['fills_rejects_summary']}",
        f"- cost_summary: {payload['cost_summary']}",
        f"- ledger_hash: {payload['ledger_hash']}",
        f"- invariants: {payload['invariants']}",
        "- main_orders_written: false",
        "- main_trades_written: false",
        "- main_portfolio_written: false",
        "- main_accounts_written: false",
    ]
    return write_report_artifact(paths, "day1_isolated_ledger_report.json", payload, "DAY1_ISOLATED_LEDGER_REPORT.md", build_simple_markdown("Day1 Isolated Ledger Report", lines, payload))
