"""Snapshot the isolated forward dry-run ledger after day 1."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import DAY_INDEX, day_json, day_report, ledger_root, non_claim_lines, paths_or_default, read_json_file, write_artifact
from trading_core.forward_dry_run.day1_virtual_execution_result import build_day1_virtual_execution_result
from trading_core.storage.file_paths import ProjectPaths


def build_day1_ledger_snapshot(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    execution_path = day_json(paths, "day1_virtual_execution_result.json")
    if not execution_path.exists():
        build_day1_virtual_execution_result(paths=paths)
    execution = read_json_file(execution_path)
    ledger = read_json_file(ledger_root(paths) / "day1_ledger.json")
    positions = ledger.get("virtual_positions", execution.get("virtual_positions", {}))
    cash = ledger.get("virtual_cash", execution.get("virtual_cash", {}))
    valuation = {
        "cash": cash.get("cash", 0.0),
        "market_value": round(sum(float(item.get("market_value", 0.0)) for item in positions.values()), 6),
    }
    valuation["total_equity"] = round(float(valuation["cash"]) + float(valuation["market_value"]), 6)
    payload: dict[str, Any] = {
        "ledger_snapshot_id": "FORWARD-DRY-RUN-DAY1-LEDGER-SNAPSHOT",
        "day_index": DAY_INDEX,
        "forward_dry_run_started": True,
        "forward_dry_run_days_completed": 1,
        "next_day_index": 2,
        "virtual_cash": cash,
        "virtual_positions": positions,
        "virtual_available_shares": {symbol: item.get("available_quantity", 0) for symbol, item in positions.items()},
        "virtual_valuation": valuation,
        "fills_count": len(execution.get("fills", [])),
        "rejects_count": len(execution.get("rejects", [])),
        "boundary": {
            "forward_dry_run_ledger_only": True,
            "main_ledger_written": False,
            "real_trading": False,
            "broker_connected": False,
        },
    }
    return write_artifact(day_json(paths, "day1_forward_dry_run_ledger_snapshot.json"), payload, day_report(paths, "DAY1_FORWARD_DRY_RUN_LEDGER_SNAPSHOT.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day 1 Ledger Snapshot",
        "",
        "- forward_dry_run_started: true",
        "- forward_dry_run_days_completed: 1",
        "- next_day_index: 2",
        f"- total_equity: {payload['virtual_valuation']['total_equity']}",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)

