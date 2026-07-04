"""Simulated market-order matching."""

from __future__ import annotations

from typing import Any

from trading_core.broker.cost_model import calculate_trade_cost, slippage_price
from trading_core.broker.market_constraints import market_constraint_rejection
from trading_core.broker.market_rules import get_market_rule, is_t_plus_one
from trading_core.calendar.trading_calendar import next_trading_day


def match_order(order: dict[str, Any], price: float, price_row: dict[str, Any] | None = None) -> dict[str, Any]:
    side = str(order["side"]).upper()
    market = str(order.get("market", "A_SHARE"))
    quantity = int(order["quantity"])
    rejection = market_constraint_rejection(order, price_row or order.get("price_row"), require_price_row=True)
    if rejection:
        return _rejected_trade(order, market, side, rejection)
    rule = get_market_rule(market)
    filled_price = slippage_price(price, side, rule)
    cost = calculate_trade_cost(price, quantity, side, market, rule)
    settlement_date = order.get("settlement_date")
    if settlement_date is None and side == "BUY" and is_t_plus_one(market):
        settlement_date = next_trading_day(str(order["date"]), market, calendar_path=order.get("calendar_path"))
    return {
        "trade_id": str(order["order_id"]).replace("ORD-", "TRD-"),
        "order_id": order["order_id"],
        "signal_id": order.get("signal_id"),
        "date": order["date"],
        "account_id": order["account_id"],
        "symbol": order["symbol"],
        "market": market,
        "side": side,
        "filled_time": f"{order['date']} 09:31:00",
        "filled_price": filled_price,
        "filled_quantity": quantity,
        "gross_amount": cost.gross_amount,
        "commission": cost.commission,
        "tax": cost.tax,
        "slippage": cost.slippage,
        "net_amount": cost.net_amount,
        "settlement_date": settlement_date,
        "status": "filled",
    }


def _rejected_trade(order: dict[str, Any], market: str, side: str, rejection: dict[str, str]) -> dict[str, Any]:
    return {
        "trade_id": str(order.get("order_id", "")).replace("ORD-", "TRD-"),
        "order_id": order.get("order_id"),
        "signal_id": order.get("signal_id"),
        "date": order.get("date"),
        "account_id": order.get("account_id"),
        "symbol": order.get("symbol"),
        "market": market,
        "side": side,
        "filled_time": None,
        "filled_price": None,
        "filled_quantity": 0,
        "gross_amount": 0.0,
        "commission": 0.0,
        "tax": 0.0,
        "slippage": 0.0,
        "net_amount": 0.0,
        "status": "rejected",
        **rejection,
    }
