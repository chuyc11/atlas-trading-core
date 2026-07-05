"""Virtual broker that converts signals into orders and trades."""

from __future__ import annotations

from typing import Any

from trading_core.accounting.account import Account
from trading_core.broker.market_constraints import market_constraint_rejection
from trading_core.broker.market_rules import is_t_plus_one, round_lot
from trading_core.broker.matching_engine import match_order
from trading_core.calendar.trading_calendar import next_trading_day
from trading_core.risk.risk_engine import check_order


def signal_to_order(
    signal: dict[str, Any],
    date: str,
    account: Account,
    price_row: dict[str, Any] | None,
    sequence: int = 1,
    existing_order_count: int = 0,
    today_traded_notional: float = 0.0,
    paths: Any | None = None,
    today_symbol_quantity: int = 0,
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
    if side == "BUY" and is_t_plus_one(market):
        order["settlement_date"] = next_trading_day(date, market, paths=paths)
    quality = str(price_row.get("quality", "missing")) if price_row else "missing"
    order["same_day_filled_quantity"] = today_symbol_quantity
    market_constraint = market_constraint_rejection(order, price_row, prior_filled_quantity=today_symbol_quantity)
    if market_constraint:
        order.update(market_constraint)
    else:
        order.update(check_order(account, order, quality, existing_order_count, today_traded_notional))
    order["status"] = "submitted" if order["risk_check"] == "passed" else "rejected"
    return order


def execute_order(order: dict[str, Any], account: Account, price_row: dict[str, Any] | None) -> dict[str, Any] | None:
    if order.get("status") != "submitted":
        return None
    if not price_row or price_row.get("price") is None:
        return None
    trade = match_order(order, float(price_row["price"]), price_row)
    if trade.get("status") != "filled":
        return None
    account.apply_trade(trade)
    return trade


def process_signals(
    signals: list[dict[str, Any]],
    date: str,
    account: Account,
    prices: dict[str, dict[str, Any]],
    *,
    paths: Any | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    orders: list[dict[str, Any]] = []
    trades: list[dict[str, Any]] = []
    today_traded_notional = 0.0
    today_filled_quantity_by_symbol: dict[str, int] = {}
    for index, signal in enumerate(signals, 1):
        symbol = str(signal.get("symbol"))
        order = signal_to_order(
            signal,
            date,
            account,
            prices.get(symbol),
            index,
            len(orders),
            today_traded_notional,
            paths,
            today_filled_quantity_by_symbol.get(symbol, 0),
        )
        orders.append(order)
        trade = execute_order(order, account, prices.get(symbol))
        if trade:
            trades.append(trade)
            today_traded_notional += abs(float(trade.get("gross_amount", 0.0)))
            today_filled_quantity_by_symbol[symbol] = today_filled_quantity_by_symbol.get(symbol, 0) + int(
                trade.get("filled_quantity", 0)
            )
    return orders, trades
