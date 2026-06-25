"""T-day signal and T+1 execution semantics."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

from trading_core.execution.trading_calendar_contract import default_calendar


MARKET_CLOSE = {"SSE": time(15, 0), "SZSE": time(15, 0), "HKEX": time(16, 0)}


def market_close_datetime(signal_date: str, market: str) -> datetime:
    close = MARKET_CLOSE["HKEX" if market.upper() in {"HK", "HKEX"} else "SSE" if market.upper() in {"SSE", "A_SHARE"} else "SZSE"]
    return datetime.fromisoformat(f"{signal_date}T{close.isoformat()}")


def next_execution_date(signal_date: str, market: str) -> str:
    return default_calendar().next_trading_day(signal_date, market)


def validate_execution_timeline(
    *,
    signal_date: str,
    generated_at: str,
    execution_date: str,
    execution_market: str,
    price_date: str | None = None,
) -> dict[str, Any]:
    expected = next_execution_date(signal_date, execution_market)
    generated = datetime.fromisoformat(generated_at.replace("Z", ""))
    close_dt = market_close_datetime(signal_date, execution_market)
    issues = []
    if generated < close_dt:
        issues.append("signal_generated_before_market_close")
    if execution_date < expected:
        issues.append("same_day_or_before_next_trading_day_execution_rejected")
    if price_date and price_date > execution_date:
        issues.append("future_price_rejected")
    return {
        "accepted": not issues,
        "issues": issues,
        "signal_date": signal_date,
        "signal_generated_at": generated_at,
        "decision_date": signal_date,
        "execution_date": execution_date,
        "execution_market": execution_market,
        "next_trading_day": expected,
    }

