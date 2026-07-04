"""Shared market microstructure constraints for simulated A-share execution."""

from __future__ import annotations

from typing import Any


MAX_VOLUME_PARTICIPATION = 0.10


def market_constraint_rejection(
    order: dict[str, Any],
    price_row: dict[str, Any] | None,
    *,
    require_price_row: bool = False,
) -> dict[str, str] | None:
    side = str(order.get("side", "")).upper()
    market = str(order.get("market", "A_SHARE"))
    if side == "HOLD":
        return None
    if not price_row:
        if require_price_row and market == "A_SHARE":
            return _reject("missing_market_constraints")
        return None
    row = _flatten_price_row(price_row)
    quantity = int(order.get("quantity") or 0)
    if _truthy(row.get("suspended")) or _truthy(row.get("is_suspended")) or _truthy(row.get("halted")):
        return _reject("security_suspended")
    volume = _number(row.get("volume"))
    if volume is not None:
        if volume <= 0:
            return _reject("zero_volume_suspension")
        if quantity > int(volume * MAX_VOLUME_PARTICIPATION):
            return _reject("volume_capacity_exceeded")
    if side == "BUY" and (_truthy(row.get("limit_up")) or _at_price_limit(row, "up")):
        return _reject("buy_blocked_at_limit_up")
    if side == "SELL" and (_truthy(row.get("limit_down")) or _at_price_limit(row, "down")):
        return _reject("sell_blocked_at_limit_down")
    return None


def _flatten_price_row(price_row: dict[str, Any]) -> dict[str, Any]:
    raw = price_row.get("raw")
    return {**raw, **price_row} if isinstance(raw, dict) else price_row


def _at_price_limit(row: dict[str, Any], direction: str) -> bool:
    pct_change = _number(row.get("pct_change") if row.get("pct_change") is not None else row.get("change_pct"))
    if pct_change is not None:
        return pct_change >= 9.9 if direction == "up" else pct_change <= -9.9
    price = _number(row.get("price"))
    previous_close = _number(row.get("previous_close"))
    if price is None or previous_close in (None, 0):
        return False
    change = (price / previous_close - 1.0) * 100
    return change >= 9.9 if direction == "up" else change <= -9.9


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _reject(reason: str) -> dict[str, str]:
    return {"risk_check": "rejected", "risk_reason": reason, "risk_reason_code": reason}
