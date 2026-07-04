"""Isolated order, execution, and valuation adapters for replay."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from trading_core.broker.market_constraints import market_constraint_rejection
from trading_core.global_briefing.isolated_replay_state import (
    ReplayDayResult,
    ReplayOrder,
    ReplaySignal,
    ReplayState,
    ReplayTrade,
    ReplayValuation,
)
from trading_core.global_briefing.signal_schema import compact_date


@dataclass(frozen=True)
class ReplayCostModel:
    commission_rate: float = 0.0005
    min_commission: float = 0.0
    tax_rate: float = 0.0
    slippage_bps: float = 0.0


def process_isolated_replay_day(
    state: ReplayState,
    replay_date: str,
    signals: list[ReplaySignal],
    price_map: dict[str, dict[str, Any]],
    *,
    cost_model: ReplayCostModel | None = None,
    lot_size: int = 100,
) -> tuple[list[ReplayOrder], list[ReplayTrade], ReplayValuation, ReplayDayResult]:
    cost_model = cost_model or ReplayCostModel()
    warnings: list[str] = []
    orders: list[ReplayOrder] = []
    trades: list[ReplayTrade] = []
    equity_before = _mark_equity(state, price_map, warnings)

    for signal in signals:
        price_row = _lookup_price_row(signal.symbol, price_map)
        price = _price_from_row(price_row)
        if price is None:
            warnings.append(f"{replay_date}: missing price for {signal.symbol}; no order generated")
            continue
        if signal.target_weight < 0:
            warnings.append(f"{replay_date}: negative target ignored for {signal.symbol}")
            continue
        target_notional = equity_before * signal.target_weight
        position = state.get_position(signal.symbol)
        current_notional = position.quantity * price
        delta = target_notional - current_notional
        if abs(delta) < price * lot_size:
            warnings.append(f"{replay_date}: target delta below lot size for {signal.symbol}")
            continue
        side = "BUY" if delta > 0 else "SELL"
        quantity = _round_lot(abs(delta) / price, lot_size)
        if side == "SELL":
            quantity = min(quantity, position.quantity)
        if quantity <= 0:
            warnings.append(f"{replay_date}: quantity below minimum lot for {signal.symbol}")
            continue
        if side == "BUY":
            quantity = _shrink_to_cash(quantity, price, lot_size, state.account.cash, cost_model)
        if quantity <= 0:
            warnings.append(f"{replay_date}: insufficient cash for minimum lot in {signal.symbol}")
            continue
        constraint = market_constraint_rejection(
            {"symbol": signal.symbol, "market": "A_SHARE", "side": side, "quantity": quantity},
            {**price_row, "price": price} if price_row else None,
            require_price_row=True,
        )
        if constraint:
            warnings.append(f"{replay_date}: {constraint['risk_reason_code']} for {signal.symbol}; no order generated")
            continue
        order, trade = _execute_order(
            state,
            replay_date,
            signal.symbol,
            side,
            quantity,
            price,
            len(orders) + 1,
            cost_model,
        )
        orders.append(order)
        trades.append(trade)

    valuation = value_replay_state(state, replay_date, price_map, warnings)
    day_result = ReplayDayResult(
        replay_id=state.replay_id,
        date=replay_date,
        signals=len(signals),
        orders=len(orders),
        trades=len(trades),
        cash=state.account.cash,
        equity=state.account.equity,
        warnings=warnings,
    )
    state.record_day(day_result)
    return orders, trades, valuation, day_result


def value_replay_state(
    state: ReplayState,
    replay_date: str,
    price_map: dict[str, dict[str, Any]],
    warnings: list[str] | None = None,
) -> ReplayValuation:
    warnings = warnings if warnings is not None else []
    market_value = 0.0
    positions = []
    for position in sorted(state.positions.values(), key=lambda item: item.symbol):
        price = _lookup_price(position.symbol, price_map)
        if price is None:
            if position.quantity > 0:
                warnings.append(f"{replay_date}: missing valuation price for {position.symbol}")
            price = 0.0
        position.market_value = position.quantity * price
        position.unrealized_pnl = (price - position.avg_cost) * position.quantity if position.quantity else 0.0
        market_value += position.market_value
        positions.append(position.to_dict())
    state.account.equity = state.account.cash + market_value
    return ReplayValuation(
        replay_id=state.replay_id,
        date=replay_date,
        cash=state.account.cash,
        market_value=market_value,
        equity=state.account.equity,
        positions=positions,
        warnings=warnings,
    )


def _execute_order(
    state: ReplayState,
    replay_date: str,
    symbol: str,
    side: str,
    quantity: int,
    price: float,
    sequence: int,
    cost_model: ReplayCostModel,
) -> tuple[ReplayOrder, ReplayTrade]:
    order_id = f"GBORDER-{state.replay_id}-{compact_date(replay_date)}-{sequence:04d}"
    trade_id = f"GBTRADE-{state.replay_id}-{compact_date(replay_date)}-{sequence:04d}"
    notional = quantity * price
    fee = max(cost_model.min_commission, notional * cost_model.commission_rate)
    tax = notional * cost_model.tax_rate if side == "SELL" else 0.0
    position = state.get_position(symbol)
    if side == "BUY":
        total_cost = notional + fee
        state.account.cash = round(state.account.cash - total_cost, 6)
        new_quantity = position.quantity + quantity
        position.avg_cost = ((position.quantity * position.avg_cost) + notional) / new_quantity if new_quantity else 0.0
        position.quantity = new_quantity
    else:
        sell_quantity = min(quantity, position.quantity)
        notional = sell_quantity * price
        fee = max(cost_model.min_commission, notional * cost_model.commission_rate)
        tax = notional * cost_model.tax_rate
        state.account.cash = round(state.account.cash + notional - fee - tax, 6)
        position.quantity -= sell_quantity
        if position.quantity <= 0:
            position.quantity = 0
            position.avg_cost = 0.0
        quantity = sell_quantity
    order = ReplayOrder(
        order_id=order_id,
        replay_id=state.replay_id,
        date=replay_date,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        status="FILLED",
    )
    trade = ReplayTrade(
        trade_id=trade_id,
        order_id=order_id,
        replay_id=state.replay_id,
        date=replay_date,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        notional=notional,
        fee=fee,
        tax=tax,
    )
    if state.account.cash < -0.000001:
        raise RuntimeError("isolated replay cash became negative")
    if position.quantity < 0:
        raise RuntimeError("isolated replay position became negative")
    return order, trade


def _mark_equity(state: ReplayState, price_map: dict[str, dict[str, Any]], warnings: list[str]) -> float:
    valuation = value_replay_state(state, "pre_trade", price_map, warnings)
    return valuation.equity


def _lookup_price(symbol: str, price_map: dict[str, dict[str, Any]]) -> float | None:
    return _price_from_row(_lookup_price_row(symbol, price_map))


def _lookup_price_row(symbol: str, price_map: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [symbol]
    if "." in symbol:
        candidates.append(symbol.split(".", 1)[0])
    else:
        candidates.extend([f"{symbol}.SH", f"{symbol}.SZ", f"{symbol}.HK"])
    for candidate in candidates:
        row = price_map.get(candidate)
        if row:
            return row
    return None


def _price_from_row(row: dict[str, Any] | None) -> float | None:
    if not row:
        return None
    for key in ["close", "price"]:
        value = row.get(key)
        if value is not None and str(value) != "":
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    return None


def _round_lot(quantity: float, lot_size: int) -> int:
    if lot_size <= 1:
        return max(0, int(math.floor(quantity)))
    return max(0, int(math.floor(quantity / lot_size) * lot_size))


def _shrink_to_cash(quantity: int, price: float, lot_size: int, cash: float, cost_model: ReplayCostModel) -> int:
    current = quantity
    while current > 0:
        notional = current * price
        fee = max(cost_model.min_commission, notional * cost_model.commission_rate)
        if notional + fee <= cash + 0.000001:
            return current
        current -= max(1, lot_size)
    return 0
