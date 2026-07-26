"""Build virtual order previews for forward dry-run day 1."""

from __future__ import annotations

from typing import Any

from trading_core.broker.cost_model import calculate_trade_cost
from trading_core.daily_workflow.common import market_rows_for_date, price_for_symbol
from trading_core.execution.ashare_lot_rules import validate_order_quantity
from trading_core.execution.ashare_tradability import evaluate_tradability
from trading_core.forward_dry_run.day1_common import DAY_INDEX, INITIAL_CASH_PER_STRATEGY, day_json, day_report, non_claim_lines, paths_or_default, read_json_file, write_artifact
from trading_core.forward_dry_run.day1_strategy_signals import build_day1_strategy_signals
from trading_core.storage.file_paths import ProjectPaths
from trading_core.strategies.common import market_for_symbol


def build_day1_virtual_order_preview(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    signals_path = day_json(paths, "day1_strategy_signals.json")
    if not signals_path.exists():
        build_day1_strategy_signals(paths=paths)
    signals_payload = read_json_file(signals_path)
    as_of_date = str(signals_payload["as_of_date"])
    market_rows = market_rows_for_date(paths, as_of_date)
    orders = []
    for signal_index, signal in enumerate(signals_payload.get("signals", []), 1):
        for symbol, target_weight in sorted(signal.get("target_weights", {}).items()):
            price = price_for_symbol(market_rows, symbol)
            raw_quantity = int((INITIAL_CASH_PER_STRATEGY * float(target_weight)) / float(price or 1.0))
            quantity = (raw_quantity // 100) * 100
            side = "BUY"
            market = "A_SHARE" if market_for_symbol(symbol) in {"SSE", "SZSE"} else "HK"
            decision = evaluate_tradability("tradable", side, price_available=price is not None, status_date=as_of_date, execution_date=signal["execution_earliest_date"])
            lot = validate_order_quantity(side, quantity)
            reject_reason = None
            if not decision.allowed:
                reject_reason = decision.reason
            elif not lot["accepted"]:
                reject_reason = lot["reason"]
            cost = calculate_trade_cost(float(price or 0.0), quantity, side, market) if price and quantity > 0 else None
            orders.append(
                {
                    "order_id": f"FDD1-{signal_index:02d}-{symbol.replace('.', '')}",
                    "strategy_id": signal["strategy_id"],
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "estimated_price": price,
                    "estimated_cost": cost.net_amount if cost else 0.0,
                    "estimated_commission": cost.commission if cost else 0.0,
                    "estimated_tax": cost.tax if cost else 0.0,
                    "estimated_slippage": cost.slippage if cost else 0.0,
                    "execution_earliest_date": signal["execution_earliest_date"],
                    "target_weight": float(target_weight),
                    "t_plus_1_applied": signal["execution_earliest_date"] > as_of_date,
                    "tradability_check": {"applied": True, "allowed": decision.allowed, "reason": decision.reason},
                    "board_lot_applied": quantity % 100 == 0,
                    "cost_estimate_present": cost is not None,
                    "preview_only": True,
                    "executed": False,
                    "real_order": False,
                    "broker_order": False,
                    "reject_reason": reject_reason,
                    "downsize_reason": "board_lot_rounding" if quantity != raw_quantity else None,
                }
            )
    payload: dict[str, Any] = {
        "order_preview_id": "FORWARD-DRY-RUN-DAY1-VIRTUAL-ORDER-PREVIEW",
        "day_index": DAY_INDEX,
        "as_of_date": as_of_date,
        "preview_only": True,
        "executed": False,
        "real_order": False,
        "broker_order": False,
        "orders": orders,
        "summary": {
            "orders_total": len(orders),
            "orders_rejected": sum(1 for order in orders if order.get("reject_reason")),
            "orders_downsized": sum(1 for order in orders if order.get("downsize_reason")),
        },
        "boundary": {
            "virtual_orders_only": True,
            "broker_connected": False,
            "main_orders_written": False,
            "real_orders_enabled": False,
        },
    }
    return write_artifact(day_json(paths, "day1_virtual_order_preview.json"), payload, day_report(paths, "DAY1_VIRTUAL_ORDER_PREVIEW.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day 1 Virtual Order Preview",
        "",
        f"- orders_total: {payload['summary']['orders_total']}",
        f"- orders_rejected: {payload['summary']['orders_rejected']}",
        "- preview_only: true",
        "- real_order: false",
        "- broker_order: false",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)

