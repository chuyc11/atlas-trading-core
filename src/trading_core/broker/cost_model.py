"""Transaction cost and simulated execution price model."""

from __future__ import annotations

from dataclasses import dataclass

from trading_core.broker.market_rules import MarketRule, get_market_rule


@dataclass(frozen=True)
class TradeCost:
    gross_amount: float
    commission: float
    tax: float
    slippage: float
    net_amount: float


def slippage_price(price: float, side: str, rule: MarketRule) -> float:
    adjustment = price * (rule.default_slippage_bps / 10000)
    if side.upper() == "BUY":
        return round(price + adjustment, 6)
    return round(price - adjustment, 6)


def calculate_trade_cost(
    price: float,
    quantity: int,
    side: str,
    market: str,
    rule: MarketRule | None = None,
) -> TradeCost:
    rule = rule or get_market_rule(market)
    fill_price = slippage_price(price, side, rule)
    gross = round(fill_price * quantity, 6)
    commission = max(abs(gross) * rule.commission_rate, rule.min_commission) if quantity else 0.0
    tax = abs(gross) * rule.stamp_tax_sell_rate if side.upper() == "SELL" else 0.0
    net = gross + commission + tax if side.upper() == "BUY" else gross - commission - tax
    return TradeCost(
        gross_amount=round(gross, 6),
        commission=round(commission, 6),
        tax=round(tax, 6),
        slippage=round(abs(fill_price - price), 6),
        net_amount=round(net, 6),
    )
