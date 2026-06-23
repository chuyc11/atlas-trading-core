"""Virtual broker that converts signals into orders and trades."""

from __future__ import annotations

from typing import Any

from trading_core.accounting.account import Account
from trading_core.broker.market_rules import round_lot
from trading_core.broker.matching_engine import match_order
from trading_core.risk.risk_engine import check_order


def signal_to_order(
    signal: dict[str, Any],
    date: str,
    account: Account,
    price_row: dict[str, Any] | None,
    sequence: int = 1,
    existing_order_count: int = 0,
) -> dict[str, Any]:
    side = "BUY" if signal.get("side") == "LONG" else str(signal.get("side", "HOLD")).upper()
    if side == "HOLD":
        return {
            "order_id": f"ORD-{date.replace('-', '')}-{sequence:03d}",
            "signal_id": signal.get("signal_id"),
            "date": date,
            "account_id": signal.get("account_id"),
            "symbol": signal.get("symbol"),
            "market": signal.get("market"),
            "side": "HOLD",
            "quantity": 0,
            "estimated_price": None,
            "target_weight": 0.0,
            "risk_check": "passed",
            "risk_reason": "hold signal",
            "status": "held",
        }

    price = float(price_row["price"]) if price_row and price_row.get("price") is not None else 0.0
    market = str(signal.get("market", "A_SHARE"))
    target_value = account.total_asset * float(signal.get("target_weight", 0.0))
    quantity = round_lot(target_value / price if price else 0, market)
    order = {
        "order_id": f"ORD-{date.replace('-', '')}-{sequence:03d}",
        "signal_id": signal.get("signal_id"),
        "date": date,
        "account_id": signal.get("account_id"),
        "symbol": signal.get("symbol"),
        "market": market,
        "side": side,
        "order_time": f"{date} 09:30:00",
        "order_type": "market_simulated",
        "target_weight": signal.get("target_weight", 0.0),
        "quantity": quantity,
        "estimated_price": price if price else None,
    }
    quality = str(price_row.get("quality", "missing")) if price_row else "missing"
    order.update(check_order(account, order, quality, existing_order_count))
    order["status"] = "submitted" if order["risk_check"] == "passed" else "rejected"
    return order


def execute_order(order: dict[str, Any], account: Account, price_row: dict[str, Any] | None) -> dict[str, Any] | None:
    if order.get("status") != "submitted":
        return None
    if not price_row or price_row.get("price") is None:
        return None
    trade = match_order(order, float(price_row["price"]))
    account.apply_trade(trade)
    return trade


def process_signals(
    signals: list[dict[str, Any]],
    date: str,
    account: Account,
    prices: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    orders: list[dict[str, Any]] = []
    trades: list[dict[str, Any]] = []
    for index, signal in enumerate(signals, 1):
        order = signal_to_order(signal, date, account, prices.get(str(signal.get("symbol"))), index, len(orders))
        orders.append(order)
        trade = execute_order(order, account, prices.get(str(signal.get("symbol"))))
        if trade:
            trades.append(trade)
    return orders, trades
