"""Isolated order, execution, and valuation adapters for replay."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
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

    def __post_init__(self) -> None:
        for name in ("commission_rate", "min_commission", "tax_rate", "slippage_bps"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be a finite non-negative number")
        if self.slippage_bps >= 10_000:
            raise ValueError("slippage_bps must be less than 10000")


@dataclass(frozen=True)
class _ResolvedPrice:
    symbol: str
    status: str
    price: float | None
    source_date: str | None
    age_days: int | None
    source: str | None
    row: dict[str, Any] | None

    def audit_dict(self, requirement: str) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "requirement": requirement,
            "status": self.status,
            "price": self.price,
            "source_date": self.source_date,
            "age_days": self.age_days,
            "source": self.source,
        }


def process_isolated_replay_day(
    state: ReplayState,
    replay_date: str,
    signals: list[ReplaySignal],
    price_map: dict[str, dict[str, Any]],
    *,
    cost_model: ReplayCostModel | None = None,
    lot_size: int = 100,
    max_price_staleness_days: int = 3,
) -> tuple[list[ReplayOrder], list[ReplayTrade], ReplayValuation, ReplayDayResult]:
    cost_model = cost_model or ReplayCostModel()
    _validate_max_staleness(max_price_staleness_days)
    warnings: list[str] = []
    orders: list[ReplayOrder] = []
    trades: list[ReplayTrade] = []
    trade_requirements: dict[str, str] = {}
    _remember_prices(state, replay_date, price_map, warnings)
    equity_before = _mark_equity(state, replay_date, max_price_staleness_days)

    for signal in signals:
        if signal.target_weight < 0:
            warnings.append(f"{replay_date}: negative target ignored for {signal.symbol}")
            continue
        existing_position = state.positions.get(signal.symbol)
        held_before_signal = existing_position is not None and existing_position.quantity > 0
        resolved = _resolve_price(state, signal.symbol, replay_date, max_price_staleness_days)
        if resolved.status != "exact" or resolved.price is None:
            if held_before_signal:
                trade_requirements[signal.symbol] = "trade"
            suffix = f"; latest source date {resolved.source_date}" if resolved.source_date else ""
            warnings.append(
                f"{replay_date}: missing price for {signal.symbol} "
                f"(exact execution price required){suffix}; no order generated"
            )
            continue
        if equity_before is None:
            warnings.append(f"{replay_date}: portfolio valuation unavailable; no order generated for {signal.symbol}")
            continue
        price = resolved.price
        price_row = resolved.row
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
        trade_requirements[signal.symbol] = "trade"
        orders.append(order)
        trades.append(trade)

    valuation = value_replay_state(
        state,
        replay_date,
        {},
        warnings,
        max_price_staleness_days=max_price_staleness_days,
        required_symbols=trade_requirements,
    )
    day_result = ReplayDayResult(
        replay_id=state.replay_id,
        date=replay_date,
        signals=len(signals),
        orders=len(orders),
        trades=len(trades),
        cash=state.account.cash,
        equity=state.account.equity,
        warnings=warnings,
        valuation_valid=valuation.valuation_valid,
    )
    state.record_day(day_result)
    return orders, trades, valuation, day_result


def value_replay_state(
    state: ReplayState,
    replay_date: str,
    price_map: dict[str, dict[str, Any]],
    warnings: list[str] | None = None,
    *,
    max_price_staleness_days: int = 3,
    required_symbols: dict[str, str] | None = None,
) -> ReplayValuation:
    _validate_max_staleness(max_price_staleness_days)
    warnings = warnings if warnings is not None else []
    _remember_prices(state, replay_date, price_map, warnings)
    requirements = dict(required_symbols or {})
    for position in state.active_positions():
        requirements.setdefault(position.symbol, "holding")

    resolutions = {
        symbol: _resolve_price(state, symbol, replay_date, max_price_staleness_days)
        for symbol in sorted(requirements)
    }
    price_observations = [resolutions[symbol].audit_dict(requirements[symbol]) for symbol in sorted(requirements)]
    valuation_valid = True
    market_value = 0.0
    positions: list[dict[str, Any]] = []
    for position in sorted(state.positions.values(), key=lambda item: item.symbol):
        if position.quantity > 0:
            resolved = resolutions[position.symbol]
            if resolved.status in {"exact", "carry_forward"} and resolved.price is not None:
                price = resolved.price
                position.market_value = position.quantity * price
                position.unrealized_pnl = (price - position.avg_cost) * position.quantity
                market_value += position.market_value
                if resolved.status == "carry_forward":
                    warnings.append(
                        f"{replay_date}: carry-forward valuation price for {position.symbol} "
                        f"from {resolved.source_date} ({resolved.age_days} days old)"
                    )
            else:
                valuation_valid = False
                label = "stale" if resolved.status == "stale" else "missing"
                warnings.append(
                    f"{replay_date}: {label} valuation price for {position.symbol}; "
                    "valuation failed closed and prior position value was preserved"
                )
        positions.append(position.to_dict())

    resolved_market_value: float | None = market_value if valuation_valid else None
    equity: float | None = state.account.cash + market_value if valuation_valid else None
    state.account.equity = equity
    return ReplayValuation(
        replay_id=state.replay_id,
        date=replay_date,
        cash=state.account.cash,
        market_value=resolved_market_value,
        equity=equity,
        positions=positions,
        warnings=warnings,
        valuation_valid=valuation_valid,
        price_observations=price_observations,
    )


def summarize_replay_price_coverage(
    valuations: list[dict[str, Any]],
    trades: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    required = 0
    resolved = 0
    exact = 0
    carried = 0
    unresolved: list[dict[str, Any]] = []
    invalid_days: list[str] = []
    trade_symbols_by_date: dict[str, set[str]] = {}
    for trade in trades or []:
        if not isinstance(trade, dict):
            continue
        trade_date = str(trade.get("date") or "unknown")
        symbol = str(trade.get("symbol") or "")
        if symbol:
            trade_symbols_by_date.setdefault(trade_date, set()).add(symbol)
    valuation_dates: set[str] = set()
    for valuation in valuations:
        if not isinstance(valuation, dict):
            continue
        replay_date = str(valuation.get("date") or "unknown")
        valuation_dates.add(replay_date)
        if valuation.get("valuation_valid") is False:
            invalid_days.append(replay_date)
        observations = valuation.get("price_observations")
        if not isinstance(observations, list):
            observations = []
        by_symbol = {
            str(observation.get("symbol")): observation
            for observation in observations
            if isinstance(observation, dict) and observation.get("symbol")
        }
        requirements = {symbol: str(observation.get("requirement") or "holding") for symbol, observation in by_symbol.items()}
        for position in valuation.get("positions", []) if isinstance(valuation.get("positions"), list) else []:
            if isinstance(position, dict) and _positive_quantity(position):
                requirements.setdefault(str(position.get("symbol") or "unknown"), "holding")
        for symbol in trade_symbols_by_date.get(replay_date, set()):
            requirements[symbol] = "trade"
        for symbol in sorted(requirements):
            observation = dict(by_symbol.get(symbol) or _missing_price_observation(symbol, requirements[symbol]))
            observation["requirement"] = requirements[symbol]
            required += 1
            requirement = requirements[symbol]
            status = str(observation.get("status") or "missing")
            observation_resolved = status == "exact" or (status == "carry_forward" and requirement == "holding")
            if observation_resolved:
                resolved += 1
                exact += int(status == "exact")
                carried += int(status == "carry_forward")
            else:
                unresolved.append({"date": replay_date, **observation})
    for replay_date in sorted(set(trade_symbols_by_date) - valuation_dates):
        invalid_days.append(replay_date)
        for symbol in sorted(trade_symbols_by_date[replay_date]):
            required += 1
            unresolved.append({"date": replay_date, **_missing_price_observation(symbol, "trade")})
    ratio = (resolved / required) if required else 1.0
    return {
        "required_price_observations": required,
        "resolved_price_observations": resolved,
        "exact_price_observations": exact,
        "carried_price_observations": carried,
        "price_coverage_ratio": ratio,
        "unresolved_price_observations": unresolved,
        "invalid_valuation_days": sorted(set(invalid_days)),
        "missing_price_days": sorted({str(item["date"]) for item in unresolved}),
    }


def _positive_quantity(position: dict[str, Any]) -> bool:
    try:
        return int(position.get("quantity", 0)) > 0
    except (TypeError, ValueError):
        return False


def _missing_price_observation(symbol: str, requirement: str) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "requirement": requirement,
        "status": "missing",
        "price": None,
        "source_date": None,
        "age_days": None,
        "source": None,
    }


def _execute_order(
    state: ReplayState,
    replay_date: str,
    symbol: str,
    side: str,
    quantity: int,
    reference_price: float,
    sequence: int,
    cost_model: ReplayCostModel,
) -> tuple[ReplayOrder, ReplayTrade]:
    order_id = f"GBORDER-{state.replay_id}-{compact_date(replay_date)}-{sequence:04d}"
    trade_id = f"GBTRADE-{state.replay_id}-{compact_date(replay_date)}-{sequence:04d}"
    execution_price = _execution_price(reference_price, side, cost_model)
    notional = quantity * execution_price
    fee = max(cost_model.min_commission, notional * cost_model.commission_rate)
    tax = notional * cost_model.tax_rate if side == "SELL" else 0.0
    slippage_cost = abs(execution_price - reference_price) * quantity
    position = state.get_position(symbol)
    if side == "BUY":
        total_cost = notional + fee
        state.account.cash = round(state.account.cash - total_cost, 6)
        new_quantity = position.quantity + quantity
        position.avg_cost = ((position.quantity * position.avg_cost) + notional) / new_quantity if new_quantity else 0.0
        position.quantity = new_quantity
    else:
        sell_quantity = min(quantity, position.quantity)
        notional = sell_quantity * execution_price
        fee = max(cost_model.min_commission, notional * cost_model.commission_rate)
        tax = notional * cost_model.tax_rate
        slippage_cost = abs(execution_price - reference_price) * sell_quantity
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
        price=execution_price,
        status="FILLED",
        reference_price=reference_price,
        slippage_bps=cost_model.slippage_bps,
    )
    trade = ReplayTrade(
        trade_id=trade_id,
        order_id=order_id,
        replay_id=state.replay_id,
        date=replay_date,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=execution_price,
        notional=notional,
        fee=fee,
        tax=tax,
        reference_price=reference_price,
        slippage_bps=cost_model.slippage_bps,
        slippage_cost=slippage_cost,
    )
    if state.account.cash < -0.000001:
        raise RuntimeError("isolated replay cash became negative")
    if position.quantity < 0:
        raise RuntimeError("isolated replay position became negative")
    return order, trade


def _mark_equity(state: ReplayState, replay_date: str, max_price_staleness_days: int) -> float | None:
    valuation = value_replay_state(
        state,
        replay_date,
        {},
        [],
        max_price_staleness_days=max_price_staleness_days,
    )
    return valuation.equity


def _remember_prices(
    state: ReplayState,
    replay_date: str,
    price_map: dict[str, dict[str, Any]],
    warnings: list[str],
) -> None:
    requested_date = _parse_date(replay_date, "replay_date")
    for map_symbol, row in price_map.items():
        if not isinstance(row, dict):
            continue
        price = _price_from_row(row)
        if price is None:
            warnings.append(f"{replay_date}: invalid price row for {map_symbol}; row ignored")
            continue
        source_date_text = str(row.get("date") or replay_date)
        try:
            source_date = date.fromisoformat(source_date_text)
        except ValueError:
            warnings.append(f"{replay_date}: invalid source date for {map_symbol}; row ignored")
            continue
        if source_date > requested_date:
            warnings.append(f"{replay_date}: future price source for {map_symbol} from {source_date_text}; row ignored")
            continue
        observation = {
            "price": price,
            "source_date": source_date_text,
            "source": str(row.get("source") or "price_map"),
            "row": dict(row),
        }
        aliases = {str(map_symbol), str(row.get("symbol") or map_symbol)}
        for alias in aliases:
            existing = state.last_prices.get(alias)
            if existing is None or str(existing.get("source_date") or "") <= source_date_text:
                state.last_prices[alias] = observation


def _resolve_price(
    state: ReplayState,
    symbol: str,
    replay_date: str,
    max_price_staleness_days: int,
) -> _ResolvedPrice:
    requested_date = _parse_date(replay_date, "replay_date")
    candidates: list[dict[str, Any]] = []
    for candidate in _symbol_candidates(symbol):
        observation = state.last_prices.get(candidate)
        if observation is not None:
            candidates.append(observation)
    eligible = [item for item in candidates if str(item.get("source_date") or "") <= replay_date]
    if not eligible:
        return _ResolvedPrice(symbol, "missing", None, None, None, None, None)
    latest = max(eligible, key=lambda item: str(item.get("source_date") or ""))
    source_date_text = str(latest["source_date"])
    source_date = _parse_date(source_date_text, "price source date")
    age_days = (requested_date - source_date).days
    status = "exact" if age_days == 0 else "carry_forward" if age_days <= max_price_staleness_days else "stale"
    price = float(latest["price"]) if status != "stale" else None
    return _ResolvedPrice(
        symbol=symbol,
        status=status,
        price=price,
        source_date=source_date_text,
        age_days=age_days,
        source=str(latest.get("source") or "price_map"),
        row=dict(latest.get("row") or {}),
    )


def _symbol_candidates(symbol: str) -> list[str]:
    candidates = [symbol]
    if "." in symbol:
        candidates.append(symbol.split(".", 1)[0])
    else:
        candidates.extend([f"{symbol}.SH", f"{symbol}.SZ", f"{symbol}.HK"])
    return candidates


def _price_from_row(row: dict[str, Any] | None) -> float | None:
    if not row:
        return None
    for key in ["close", "price"]:
        value = row.get(key)
        if value is not None and str(value) != "":
            try:
                price = float(value)
            except (TypeError, ValueError):
                return None
            return price if math.isfinite(price) and price > 0 else None
    return None


def _execution_price(reference_price: float, side: str, cost_model: ReplayCostModel) -> float:
    direction = 1.0 if side == "BUY" else -1.0
    price = reference_price * (1.0 + direction * cost_model.slippage_bps / 10_000.0)
    if not math.isfinite(price) or price <= 0:
        raise ValueError("slippage produced an invalid execution price")
    return price


def _round_lot(quantity: float, lot_size: int) -> int:
    if lot_size <= 1:
        return max(0, int(math.floor(quantity)))
    return max(0, int(math.floor(quantity / lot_size) * lot_size))


def _shrink_to_cash(
    quantity: int,
    reference_price: float,
    lot_size: int,
    cash: float,
    cost_model: ReplayCostModel,
) -> int:
    execution_price = _execution_price(reference_price, "BUY", cost_model)
    current = quantity
    while current > 0:
        notional = current * execution_price
        fee = max(cost_model.min_commission, notional * cost_model.commission_rate)
        if notional + fee <= cash + 0.000001:
            return current
        current -= max(1, lot_size)
    return 0


def _validate_max_staleness(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("max_price_staleness_days must be a non-negative integer")


def _parse_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO date: {value}") from exc
