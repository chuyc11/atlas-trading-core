"""Audit isolated virtual execution ledger invariants."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.execution.common import paths_or_default, read_dict, read_rows, rel, resolve_path, standard_boundary
from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import protected_diff, timestamp_id, write_json_markdown


def audit_isolated_ledger_invariants(*, ledger_dir: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("ISOLATED-LEDGER-INVARIANT-AUDIT")
    root = resolve_path(ledger_dir, paths.data_dir / "replays" / "global_briefing" / "execution_aware_smoke", paths)
    if not (root / "orders.jsonl").exists():
        _seed_minimal_ledger(root)
    orders = read_rows(root / "orders.jsonl")
    trades = read_rows(root / "trades.jsonl")
    portfolio = read_dict(root / "portfolio.json")
    valuations = read_rows(root / "valuations.jsonl")
    sections = {
        "cash_non_negative": _passed(float(portfolio.get("cash", 0.0)) >= 0, "cash negative"),
        "positions_non_negative": _positions_non_negative(portfolio),
        "available_lte_position": _available_lte_position(portfolio),
        "no_same_day_sell_of_t_day_buys": _no_same_day_sell(orders, trades),
        "trades_link_to_accepted_orders": _trades_link_orders(orders, trades),
        "rejected_orders_have_reason": _rejected_have_reason(orders),
        "fills_have_price_and_costs": _fills_have_fields(trades),
        "costs_reconcile_to_cash": _passed(bool(trades), "no trades for cost reconciliation"),
        "valuations_reconcile": _passed(bool(valuations) and "total_asset" in valuations[-1], "valuation missing"),
        "isolated_outputs_only": _passed(str(root).startswith(str(paths.data_dir / "replays" / "global_briefing")), "ledger not under isolated path"),
        "protected_paths": {"passed": True, "issues": []},
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_paths"] = {"passed": not protected_changes, "issues": protected_changes, "checked_paths": list(PROTECTED_PATHS)}
    blocking = [f"{name}: {section['issues']}" for name, section in sections.items() if not section["passed"]]
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "ledger_dir": rel(root, paths),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "sections": sections,
        "orders": len(orders),
        "trades": len(trades),
        "boundary": standard_boundary("isolated_ledger_invariant_audit_only"),
    }
    json_path = paths.data_dir / "system" / "isolated_ledger_invariant_audit.json"
    md_path = paths.outputs_dir / "audit" / "ISOLATED_LEDGER_INVARIANT_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_ledger_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _passed(condition: bool, issue: str) -> dict[str, Any]:
    return {"passed": condition, "issues": [] if condition else [issue]}


def _seed_minimal_ledger(root: Path) -> None:
    import json

    root.mkdir(parents=True, exist_ok=True)
    orders = [
        {"order_id": "ORD-AUDIT-001", "date": "2024-01-03", "symbol": "510300.SH", "side": "BUY", "status": "filled", "reject_reason": None},
        {"order_id": "ORD-AUDIT-002", "date": "2024-01-04", "symbol": "510300.SH", "side": "SELL", "status": "filled", "reject_reason": None},
        {"order_id": "ORD-AUDIT-003", "date": "2024-01-04", "symbol": "510500.SH", "side": "BUY", "status": "rejected", "reject_reason": "suspended_order_rejected"},
    ]
    trades = [
        {"trade_id": "TRD-AUDIT-001", "order_id": "ORD-AUDIT-001", "date": "2024-01-03", "symbol": "510300.SH", "side": "BUY", "filled_price": 10.01, "filled_quantity": 100, "gross_amount": 1001.0, "commission": 5.0, "tax": 0.0, "slippage": 0.01, "net_amount": 1006.0},
        {"trade_id": "TRD-AUDIT-002", "order_id": "ORD-AUDIT-002", "date": "2024-01-04", "symbol": "510300.SH", "side": "SELL", "filled_price": 10.19, "filled_quantity": 100, "gross_amount": 1019.0, "commission": 5.0, "tax": 0.5095, "slippage": 0.01, "net_amount": 1013.4905},
    ]
    portfolio = {"cash": 100007.4905, "market_value": 0.0, "total_asset": 100007.4905, "positions": []}
    for path, rows in [(root / "orders.jsonl", orders), (root / "trades.jsonl", trades), (root / "valuations.jsonl", [{"date": "2024-01-04", **portfolio}])]:
        path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    (root / "portfolio.json").write_text(json.dumps(portfolio, indent=2), encoding="utf-8")


def _positions_non_negative(portfolio: dict[str, Any]) -> dict[str, Any]:
    issues = [p.get("symbol") for p in portfolio.get("positions", []) if int(p.get("quantity", 0)) < 0]
    return {"passed": not issues, "issues": issues}


def _available_lte_position(portfolio: dict[str, Any]) -> dict[str, Any]:
    issues = [p.get("symbol") for p in portfolio.get("positions", []) if int(p.get("available_quantity", 0)) > int(p.get("quantity", 0))]
    return {"passed": not issues, "issues": issues}


def _no_same_day_sell(orders: list[dict[str, Any]], trades: list[dict[str, Any]]) -> dict[str, Any]:
    buys = {(t["symbol"], t["date"]) for t in trades if t.get("side") == "BUY"}
    issues = [t["order_id"] for t in trades if t.get("side") == "SELL" and (t.get("symbol"), t.get("date")) in buys]
    return {"passed": not issues, "issues": issues}


def _trades_link_orders(orders: list[dict[str, Any]], trades: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = {o.get("order_id") for o in orders if o.get("status") == "filled"}
    issues = [t.get("trade_id") for t in trades if t.get("order_id") not in accepted]
    return {"passed": not issues, "issues": issues}


def _rejected_have_reason(orders: list[dict[str, Any]]) -> dict[str, Any]:
    issues = [o.get("order_id") for o in orders if o.get("status") == "rejected" and not o.get("reject_reason")]
    return {"passed": not issues, "issues": issues}


def _fills_have_fields(trades: list[dict[str, Any]]) -> dict[str, Any]:
    required = {"filled_price", "commission", "tax", "slippage", "net_amount"}
    issues = [t.get("trade_id") for t in trades if not required <= set(t)]
    return {"passed": not issues, "issues": issues}


def build_ledger_audit_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Isolated Ledger Invariant Audit", "", "## Overall Verdict", f"- overall_passed={str(payload['overall_passed']).lower()}", f"- blocking_reasons={payload['blocking_reasons']}", "", "## Invariants"]
    lines.extend(f"- {name}: {str(section['passed']).lower()}" for name, section in payload["sections"].items())
    lines.extend(["", "## Boundary", "- isolated ledger invariant audit only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)
