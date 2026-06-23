"""Portfolio valuation helpers."""

from __future__ import annotations

from typing import Any

from trading_core.accounting.account import Account


def value_account(account: Account, date: str, prices: dict[str, float], previous_total_asset: float | None = None) -> dict[str, Any]:
    account.mark_prices(prices)
    portfolio = account.to_portfolio(date, previous_total_asset)
    return {
        "date": date,
        "account_id": account.account_id,
        "total_asset": portfolio["total_asset"],
        "cash": portfolio["cash"],
        "market_value": portfolio["market_value"],
        "daily_return": portfolio["daily_return"],
        "positions": portfolio["positions"],
    }
