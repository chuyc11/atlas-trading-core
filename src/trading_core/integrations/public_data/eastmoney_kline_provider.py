"""Eastmoney historical kline adapter."""

from __future__ import annotations

from typing import Any


PROVIDER_NAME = "eastmoney_kline_public_http"


def fetch_eastmoney_price_history(
    symbols: list[str],
    *,
    start_date: str,
    end_date: str,
    adjustment_type: str = "raw",
    max_workers: int = 32,
    retry: int = 2,
    rate_limit_per_minute: int | None = None,
) -> dict[str, Any]:
    del retry, rate_limit_per_minute
    from trading_core.integrations.public_data.historical_provider_registry import fetch_price_history

    return fetch_price_history(
        symbols,
        start_date=start_date,
        end_date=end_date,
        adjustment_type=adjustment_type,
        max_workers=max_workers,
    )
