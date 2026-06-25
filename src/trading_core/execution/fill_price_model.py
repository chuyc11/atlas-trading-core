"""PIT-safe fill price model."""

from __future__ import annotations

from typing import Any

from trading_core.broker.cost_model import slippage_price
from trading_core.broker.market_rules import get_market_rule


def resolve_fill_price(price_row: dict[str, Any] | None, side: str, market: str = "A_SHARE", *, execution_date: str | None = None) -> dict[str, Any]:
    if not price_row or price_row.get("price") in (None, ""):
        return {"accepted": False, "reason": "fill_price_missing"}
    price_date = price_row.get("date")
    if execution_date and price_date and str(price_date) > execution_date:
        return {"accepted": False, "reason": "future_price_rejected"}
    price = float(price_row["price"])
    return {"accepted": True, "price": slippage_price(price, side, get_market_rule(market)), "source": price_row.get("source", "configured_execution_price")}

