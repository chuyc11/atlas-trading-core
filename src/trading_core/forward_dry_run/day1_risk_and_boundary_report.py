"""Risk and boundary report for virtual forward dry-run day 1."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import DAY_INDEX, day_json, day_report, non_claim_lines, paths_or_default, read_json_file, write_artifact
from trading_core.forward_dry_run.day1_ledger_snapshot import build_day1_ledger_snapshot
from trading_core.storage.file_paths import ProjectPaths


def build_day1_risk_and_boundary_report(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    ledger_path = day_json(paths, "day1_forward_dry_run_ledger_snapshot.json")
    if not ledger_path.exists():
        build_day1_ledger_snapshot(paths=paths)
    ledger = read_json_file(ledger_path)
    execution = read_json_file(day_json(paths, "day1_virtual_execution_result.json"))
    positions = ledger.get("virtual_positions", {})
    total_equity = float(ledger.get("virtual_valuation", {}).get("total_equity", 0.0) or 0.0)
    max_position_value = max([float(item.get("market_value", 0.0)) for item in positions.values()] or [0.0])
    risk_summary = {
        "position_concentration": round(max_position_value / total_equity, 6) if total_equity else 0.0,
        "cash_usage": round(1.0 - float(ledger.get("virtual_cash", {}).get("cash", 0.0) or 0.0) / total_equity, 6) if total_equity else 0.0,
        "rejects_count": len(execution.get("rejects", [])),
        "no_trade_fallback": execution.get("no_trade_fallback") is True,
        "costs": execution.get("costs", {}),
        "ledger_invariants": execution.get("invariants", {}),
    }
    payload: dict[str, Any] = {
        "report_id": "FORWARD-DRY-RUN-DAY1-RISK-AND-BOUNDARY-REPORT",
        "day_index": DAY_INDEX,
        "risk_summary": risk_summary,
        "boundary_summary": {
            "main_ledger_written": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "ml_shadow_used_as_authorization": False,
            "llm_trading_decision": False,
            "rl_used": False,
            "promotion_triggered": False,
            "strategy_effectiveness_proven": False,
            "live_trading_ready": False,
        },
        "warnings": [],
        "blocking_reasons": [],
    }
    return write_artifact(day_json(paths, "day1_risk_and_boundary_report.json"), payload, day_report(paths, "DAY1_RISK_AND_BOUNDARY_REPORT.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day 1 Risk and Boundary Report",
        "",
        f"- position_concentration: {payload['risk_summary']['position_concentration']}",
        f"- cash_usage: {payload['risk_summary']['cash_usage']}",
        f"- rejects_count: {payload['risk_summary']['rejects_count']}",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)

