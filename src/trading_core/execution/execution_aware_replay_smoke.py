"""Execution-aware isolated replay smoke."""

from __future__ import annotations

from typing import Any

from trading_core.execution.common import HARDENING_NOTICE, paths_or_default, standard_boundary, write_rows
from trading_core.execution.isolated_ledger_invariant_audit import audit_isolated_ledger_invariants
from trading_core.execution.virtual_execution_engine import execute_virtual_order, portfolio_snapshot, settle_available_shares
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def run_execution_aware_replay_smoke(*, start_date: str = "2024-01-02", end_date: str = "2024-01-08", execution_mode: str = "isolated", paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    smoke_id, created_at = timestamp_id("EXECUTION-AWARE-REPLAY-SMOKE")
    root = paths.data_dir / "replays" / "global_briefing" / "execution_aware_smoke"
    state = {"cash": 100000.0, "positions": {}}
    orders: list[dict[str, Any]] = []
    trades: list[dict[str, Any]] = []
    scenarios = [
        ("normal_buy", {"order_id": "ORD-SMOKE-001", "date": "2024-01-03", "execution_date": "2024-01-03", "symbol": "510300.SH", "market": "A_SHARE", "side": "BUY", "quantity": 100}, {"date": "2024-01-03", "price": 10.0, "status": "tradable"}),
        ("lot_reject", {"order_id": "ORD-SMOKE-002", "date": "2024-01-03", "execution_date": "2024-01-03", "symbol": "510300.SH", "market": "A_SHARE", "side": "BUY", "quantity": 50}, {"date": "2024-01-03", "price": 10.0, "status": "tradable"}),
        ("suspended_reject", {"order_id": "ORD-SMOKE-003", "date": "2024-01-03", "execution_date": "2024-01-03", "symbol": "510500.SH", "market": "A_SHARE", "side": "BUY", "quantity": 100}, {"date": "2024-01-03", "price": 5.0, "status": "suspended"}),
        ("limit_reject", {"order_id": "ORD-SMOKE-004", "date": "2024-01-03", "execution_date": "2024-01-03", "symbol": "510500.SH", "market": "A_SHARE", "side": "BUY", "quantity": 100}, {"date": "2024-01-03", "price": 5.0, "status": "limit_up"}),
        ("cash_reject", {"order_id": "ORD-SMOKE-005", "date": "2024-01-03", "execution_date": "2024-01-03", "symbol": "510500.SH", "market": "A_SHARE", "side": "BUY", "quantity": 20000}, {"date": "2024-01-03", "price": 10.0, "status": "tradable"}),
    ]
    scenario_results = []
    for name, order, price in scenarios:
        accepted_order, trade = execute_virtual_order(order, state, price)
        accepted_order["scenario"] = name
        orders.append(accepted_order)
        if trade:
            trade["scenario"] = name
            trades.append(trade)
        scenario_results.append({"scenario": name, "order_status": accepted_order["status"], "reject_reason": accepted_order.get("reject_reason")})
    same_day_sell, same_day_trade = execute_virtual_order({"order_id": "ORD-SMOKE-006", "date": "2024-01-03", "execution_date": "2024-01-03", "symbol": "510300.SH", "market": "A_SHARE", "side": "SELL", "quantity": 100}, state, {"date": "2024-01-03", "price": 10.2, "status": "tradable"})
    same_day_sell["scenario"] = "same_day_available_reject"
    orders.append(same_day_sell)
    scenario_results.append({"scenario": "same_day_available_reject", "order_status": same_day_sell["status"], "reject_reason": same_day_sell.get("reject_reason")})
    settle_available_shares(state, "2024-01-04")
    sell, sell_trade = execute_virtual_order({"order_id": "ORD-SMOKE-007", "date": "2024-01-04", "execution_date": "2024-01-04", "symbol": "510300.SH", "market": "A_SHARE", "side": "SELL", "quantity": 100}, state, {"date": "2024-01-04", "price": 10.2, "status": "tradable"})
    sell["scenario"] = "normal_sell"
    orders.append(sell)
    if sell_trade:
        sell_trade["scenario"] = "normal_sell"
        trades.append(sell_trade)
    scenario_results.append({"scenario": "normal_sell", "order_status": sell["status"], "reject_reason": sell.get("reject_reason")})
    portfolio = portfolio_snapshot(state, {"510300.SH": 10.2, "510500.SH": 5.0})
    write_rows(root / "orders.jsonl", orders)
    write_rows(root / "trades.jsonl", trades)
    write_rows(root / "valuations.jsonl", [{"date": end_date, **portfolio}])
    (root / "portfolio.json").write_text(__import__("json").dumps(portfolio, indent=2), encoding="utf-8")
    ledger_audit = audit_isolated_ledger_invariants(ledger_dir=str(root), paths=paths)
    payload: dict[str, Any] = {
        "smoke_id": smoke_id,
        "created_at": created_at,
        "start_date": start_date,
        "end_date": end_date,
        "execution_mode": execution_mode,
        "scenarios": scenario_results,
        "included_scenarios": len(scenario_results),
        "ledger_dir": str(root),
        "ledger_invariant_audit_passed": ledger_audit["overall_passed"],
        "overall_passed": execution_mode == "isolated" and ledger_audit["overall_passed"] and len(scenario_results) >= 6,
        "boundary": standard_boundary("execution_aware_replay_smoke_only"),
    }
    json_path = paths.data_dir / "system" / "execution_aware_replay_smoke.json"
    md_path = paths.outputs_dir / "system" / "EXECUTION_AWARE_REPLAY_SMOKE.md"
    write_json_markdown(json_path, payload, md_path, build_smoke_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_smoke_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Execution Aware Replay Smoke", "", "## Scope", "This smoke connects virtual execution rules to an isolated replay sample.", HARDENING_NOTICE, "", "## Scenarios"]
    lines.extend(f"- {item['scenario']}: {item['order_status']} {item.get('reject_reason')}" for item in payload["scenarios"])
    lines.extend(["", "## Boundary", "- execution-aware replay smoke only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

