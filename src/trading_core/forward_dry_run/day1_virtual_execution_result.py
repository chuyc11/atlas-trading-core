"""Execute forward dry-run day 1 virtual orders in an isolated ledger."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import DAY_INDEX, INITIAL_CASH_PER_STRATEGY, boundary, day_json, day_report, ledger_root, non_claim_lines, paths_or_default, read_json_file, safe_float, write_artifact, write_json_only
from trading_core.forward_dry_run.day1_virtual_order_preview import build_day1_virtual_order_preview
from trading_core.storage.file_paths import ProjectPaths


def build_day1_virtual_execution_result(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    preview_path = day_json(paths, "day1_virtual_order_preview.json")
    if not preview_path.exists():
        build_day1_virtual_order_preview(paths=paths)
    preview = read_json_file(preview_path)
    strategy_count = max(len({order.get("strategy_id") for order in preview.get("orders", [])}), 1)
    initial_cash = INITIAL_CASH_PER_STRATEGY * strategy_count
    fills = []
    rejects = []
    positions: dict[str, dict[str, Any]] = {}
    total_cost = 0.0
    cost_summary = {"commission": 0.0, "tax": 0.0, "slippage": 0.0, "gross": 0.0, "net": 0.0}
    for order in preview.get("orders", []):
        if order.get("reject_reason") or int(order.get("quantity", 0) or 0) <= 0:
            rejects.append({**order, "executed": False})
            continue
        quantity = int(order["quantity"])
        price = safe_float(order.get("estimated_price"))
        net = safe_float(order.get("estimated_cost"))
        total_cost += net
        cost_summary["commission"] += safe_float(order.get("estimated_commission"))
        cost_summary["tax"] += safe_float(order.get("estimated_tax"))
        cost_summary["slippage"] += safe_float(order.get("estimated_slippage"))
        cost_summary["gross"] += price * quantity
        cost_summary["net"] += net
        fills.append(
            {
                "order_id": order["order_id"],
                "strategy_id": order["strategy_id"],
                "symbol": order["symbol"],
                "side": order["side"],
                "quantity": quantity,
                "fill_price": price,
                "gross_amount": round(price * quantity, 6),
                "net_amount": round(net, 6),
                "virtual_execution": True,
                "real_execution": False,
                "broker_execution": False,
            }
        )
        position = positions.setdefault(order["symbol"], {"symbol": order["symbol"], "quantity": 0, "available_quantity": 0, "average_price": price})
        position["quantity"] += quantity
        position["available_quantity"] += 0
        position["average_price"] = price
    virtual_cash = {"currency": "CNY", "initial_cash": round(initial_cash, 6), "cash": round(initial_cash - total_cost, 6)}
    virtual_positions = {symbol: {**position, "market_value": round(position["quantity"] * position["average_price"], 6)} for symbol, position in positions.items()}
    invariants = {
        "cash_non_negative": virtual_cash["cash"] >= 0,
        "positions_non_negative": all(item["quantity"] >= 0 for item in virtual_positions.values()),
        "available_shares_valid": all(0 <= item["available_quantity"] <= item["quantity"] for item in virtual_positions.values()),
    }
    ledger = {
        "day_index": DAY_INDEX,
        "as_of_date": preview.get("as_of_date"),
        "virtual_cash": virtual_cash,
        "virtual_positions": virtual_positions,
        "fills": fills,
        "rejects": rejects,
        "costs": {key: round(value, 6) for key, value in cost_summary.items()},
    }
    write_json_only(ledger_root(paths) / "day1_ledger.json", ledger)
    write_json_only(ledger_root(paths) / "cash.json", virtual_cash)
    write_json_only(ledger_root(paths) / "positions.json", virtual_positions)
    write_json_only(ledger_root(paths) / "fills.json", {"fills": fills})
    write_json_only(ledger_root(paths) / "rejects.json", {"rejects": rejects})
    payload: dict[str, Any] = {
        "execution_result_id": "FORWARD-DRY-RUN-DAY1-VIRTUAL-EXECUTION-RESULT",
        "day_index": DAY_INDEX,
        "as_of_date": preview.get("as_of_date"),
        "execution_mode": "forward_dry_run_virtual",
        "virtual_execution": True,
        "real_execution": False,
        "broker_execution": False,
        "executed": True,
        "fills": fills,
        "rejects": rejects,
        "costs": {key: round(value, 6) for key, value in cost_summary.items()},
        "virtual_cash": virtual_cash,
        "virtual_positions": virtual_positions,
        "ledger_writes": {
            "forward_dry_run_ledger_written": True,
            "main_orders_written": False,
            "main_trades_written": False,
            "main_portfolio_written": False,
            "main_accounts_written": False,
        },
        "invariants": invariants,
        "no_trade_fallback": len(fills) == 0,
        "boundary": boundary("virtual_execution_only"),
    }
    return write_artifact(day_json(paths, "day1_virtual_execution_result.json"), payload, day_report(paths, "DAY1_VIRTUAL_EXECUTION_RESULT.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day 1 Virtual Execution Result",
        "",
        "- execution_mode: forward_dry_run_virtual",
        "- virtual_execution: true",
        "- real_execution: false",
        "- broker_execution: false",
        f"- fills: {len(payload['fills'])}",
        f"- rejects: {len(payload['rejects'])}",
        "- forward_dry_run_ledger_written: true",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)

