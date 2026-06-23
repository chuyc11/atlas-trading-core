"""Risk checks for simulated orders."""

from __future__ import annotations

from typing import Any

from trading_core.accounting.account import Account
from trading_core.config_loader import load_config
from trading_core.data.data_quality import trade_action_for_quality


def load_risk_rules(config: dict[str, Any] | None = None) -> dict[str, Any]:
    return config or load_config("risk_rules.yaml")


def check_order(
    account: Account,
    order: dict[str, Any],
    price_quality: str,
    existing_order_count: int = 0,
    risk_rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rules = load_risk_rules(risk_rules)
    limits = rules["limits"]
    side = str(order.get("side", "")).upper()
    target_weight = float(order.get("target_weight", 0.0))
    estimated_price = float(order.get("estimated_price") or 0.0)
    quantity = int(order.get("quantity") or 0)
    symbol = str(order.get("symbol"))
    market_value = account.market_value
    total_asset = account.total_asset

    if existing_order_count >= int(limits["max_orders_per_day"]):
        return reject("max_orders_per_day exceeded")
    action, reason = trade_action_for_quality(price_quality, side)
    if action != "ALLOW":
        return reject(reason)
    if quantity <= 0 and side != "HOLD":
        return reject("quantity is zero")
    if target_weight > float(limits["max_single_position_weight"]):
        return reject("max_single_position_weight exceeded")

    if side == "BUY":
        gross_needed = estimated_price * quantity
        if gross_needed > account.cash:
            return reject("cash insufficient")
        projected_position_value = gross_needed
        if symbol in account.positions:
            projected_position_value += account.positions[symbol].market_value
        if total_asset and projected_position_value / total_asset > float(limits["max_single_position_weight"]):
            return reject("single position limit exceeded")
        projected_total_position = market_value + gross_needed
        if total_asset and projected_total_position / total_asset > float(limits["max_total_position_weight"]):
            return reject("max_total_position_weight exceeded")
        projected_cash_weight = (account.cash - gross_needed) / total_asset if total_asset else 0.0
        if projected_cash_weight < float(limits["min_cash_weight"]):
            return reject("min_cash_weight breached")

    if side == "SELL":
        position = account.positions.get(symbol)
        available = position.available_quantity if position else 0
        if quantity > available:
            return reject("sell quantity exceeds available position")

    return {"risk_check": "passed", "risk_reason": "passed"}


def reject(reason: str) -> dict[str, str]:
    return {"risk_check": "rejected", "risk_reason": reason}
