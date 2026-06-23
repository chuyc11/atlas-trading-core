"""Simple trading calendar with weekday fallback."""

from __future__ import annotations

from datetime import date as Date, datetime, timedelta


def parse_date(value: str | Date) -> Date:
    if isinstance(value, Date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def format_date(value: Date) -> str:
    return value.isoformat()


def is_trading_day(date: str | Date, market: str = "A_SHARE") -> bool:
    current = parse_date(date)
    return current.weekday() < 5


def next_trading_day(date: str | Date, market: str = "A_SHARE") -> str:
    current = parse_date(date) + timedelta(days=1)
    while not is_trading_day(current, market):
        current += timedelta(days=1)
    return format_date(current)


def previous_trading_day(date: str | Date, market: str = "A_SHARE") -> str:
    current = parse_date(date) - timedelta(days=1)
    while not is_trading_day(current, market):
        current -= timedelta(days=1)
    return format_date(current)
