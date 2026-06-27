"""Listing-age filter helpers for A-share tradable universe filtering."""

from __future__ import annotations

from typing import Any

import pandas as pd


def listing_trading_days(list_date: Any, exchange: str, as_of_date: str, calendar: pd.DataFrame) -> int | None:
    if list_date in (None, "", "-", "--") or pd.isna(list_date):
        return None
    listed = str(list_date)[:10]
    if listed > as_of_date:
        return 0
    if calendar.empty:
        return None
    cal = calendar
    if "exchange" in cal.columns and exchange:
        exchange_cal = cal[cal["exchange"].astype(str) == exchange]
        if not exchange_cal.empty:
            cal = exchange_cal
    if "is_trading_day" in cal.columns:
        cal = cal[cal["is_trading_day"].fillna(False).astype(bool)]
    dates = cal["date"].astype(str)
    count = int(((dates >= listed) & (dates <= as_of_date)).sum())
    return count if count > 0 else None

