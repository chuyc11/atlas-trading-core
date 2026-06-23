"""Simulated market-order matching."""

from __future__ import annotations

from typing import Any

from trading_core.broker.cost_model import calculate_trade_cost, slippage_price
from trading_core.broker.market_rules import get_market_rule


def match_order(order: dict[str, Any], price: float) -> dict[str, Any]:
    side = str(order["side"]).upper()
    market = str(order.get("market", "A_SHARE"))
    quantity = int(order["quantity"])
    rule = get_market_rule(market)
    filled_price = slippage_price(price, side, rule)
    cost = calculate_trade_cost(price, quantity, side, market, rule)
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
        "status": "filled",
    }
