"""Market rules for lot sizes, T+1, and price ticks."""

from __future__ import annotations

from dataclasses import dataclass
from math import floor
from typing import Any

from trading_core.config_loader import load_config


@dataclass(frozen=True)
class MarketRule:
    market: str
    lot_size: int
    allow_fractional: bool
    t_plus_one: bool
    price_tick: float
    default_slippage_bps: float
    commission_rate: float
    min_commission: float
    stamp_tax_sell_rate: float


def load_market_rules(config: dict[str, Any] | None = None) -> dict[str, MarketRule]:
    payload = config or load_config("broker_rules.yaml")
    rules = {}
    for market, values in payload["markets"].items():
        rules[market] = MarketRule(market=market, **values)
    return rules


def get_market_rule(market: str, rules: dict[str, MarketRule] | None = None) -> MarketRule:
    rule_map = rules or load_market_rules()
    if market not in rule_map:
        raise KeyError(f"Unknown market: {market}")
    return rule_map[market]


def round_lot(quantity: float, market: str, rules: dict[str, MarketRule] | None = None) -> int:
    rule = get_market_rule(market, rules)
    if rule.allow_fractional:
        return int(quantity)
    if quantity <= 0:
        return 0
    return int(floor(quantity / rule.lot_size) * rule.lot_size)


def is_t_plus_one(market: str, rules: dict[str, MarketRule] | None = None) -> bool:
    return get_market_rule(market, rules).t_plus_one
