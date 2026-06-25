"""Fail-closed virtual execution engine for isolated A-share replay tests."""

from __future__ import annotations

from typing import Any

from trading_core.broker.cost_model import calculate_trade_cost, slippage_price
from trading_core.broker.market_rules import get_market_rule
from trading_core.execution.ashare_lot_rules import validate_order_quantity
from trading_core.execution.ashare_tradability import evaluate_tradability
from trading_core.execution.position_availability import t_plus_one_available_after


def execute_virtual_order(order: dict[str, Any], state: dict[str, Any], price_row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    side = str(order.get("side", "")).upper()
    symbol = str(order.get("symbol"))
    market = str(order.get("market", "A_SHARE"))
    quantity = int(order.get("quantity", 0))
    execution_date = str(order.get("execution_date", order.get("date")))
    status = str(price_row.get("status", "tradable"))
    price = price_row.get("price")
    position = state.setdefault("positions", {}).setdefault(symbol, {"quantity": 0, "available_quantity": 0, "pending": {}})
    tradability = evaluate_tradability(status, side, price_available=price is not None, status_date=price_row.get("status_date"), execution_date=execution_date)
    if not tradability.allowed:
        return _reject(order, tradability.reason), None
    lot = validate_order_quantity(side, quantity, position_quantity=int(position["quantity"]), available_quantity=int(position["available_quantity"]))
    if not lot["accepted"]:
        return _reject(order, lot["reason"]), None
    rule = get_market_rule(market)
    cost = calculate_trade_cost(float(price), quantity, side, market, rule)
    if side == "BUY" and float(state.get("cash", 0.0)) < cost.net_amount:
        return _reject(order, "insufficient_cash_rejected"), None
    filled_price = slippage_price(float(price), side, rule)
    trade = {
        "trade_id": str(order["order_id"]).replace("ORD-", "TRD-"),
        "order_id": order["order_id"],
        "date": execution_date,
        "symbol": symbol,
        "market": market,
        "side": side,
        "filled_price": filled_price,
        "filled_quantity": quantity,
        "gross_amount": cost.gross_amount,
        "commission": cost.commission,
        "tax": cost.tax,
        "slippage": cost.slippage,
        "net_amount": cost.net_amount,
        "status": "filled",
        "fill_reason": "virtual_execution_rules_passed",
    }
    accepted = {**order, "status": "filled", "reject_reason": None, "fill_reason": trade["fill_reason"]}
    if side == "BUY":
        state["cash"] = round(float(state.get("cash", 0.0)) - cost.net_amount, 6)
        position["quantity"] += quantity
        settle = t_plus_one_available_after(execution_date, "SSE")
        position["pending"][settle] = position["pending"].get(settle, 0) + quantity
    else:
        state["cash"] = round(float(state.get("cash", 0.0)) + cost.net_amount, 6)
        position["quantity"] -= quantity
        position["available_quantity"] -= quantity
    return accepted, trade


def settle_available_shares(state: dict[str, Any], date: str) -> None:
    for position in state.get("positions", {}).values():
        pending = position.setdefault("pending", {})
        for settle_date in [item for item in pending if item <= date]:
            position["available_quantity"] += pending.pop(settle_date)


def portfolio_snapshot(state: dict[str, Any], prices: dict[str, float]) -> dict[str, Any]:
    positions = []
    market_value = 0.0
    for symbol, position in state.get("positions", {}).items():
        price = float(prices.get(symbol, 0.0))
        value = round(int(position["quantity"]) * price, 6)
        market_value += value
        positions.append({"symbol": symbol, "quantity": int(position["quantity"]), "available_quantity": int(position["available_quantity"]), "current_price": price, "market_value": value, "pending": position.get("pending", {})})
    return {"cash": round(float(state.get("cash", 0.0)), 6), "market_value": round(market_value, 6), "total_asset": round(float(state.get("cash", 0.0)) + market_value, 6), "positions": positions}


def _reject(order: dict[str, Any], reason: str) -> dict[str, Any]:
    return {**order, "status": "rejected", "reject_reason": reason, "fill_reason": None}

