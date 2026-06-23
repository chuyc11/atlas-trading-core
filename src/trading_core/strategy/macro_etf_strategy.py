"""Macro ETF strategy wrapper."""

from __future__ import annotations

from typing import Any

from trading_core.signals.signal_generator import generate_trading_signals


def generate_macro_etf_signals(
    macro_signals: list[dict[str, Any]],
    date: str,
    account_id: str,
    universe: dict[str, Any],
) -> list[dict[str, Any]]:
    return generate_trading_signals(
        macro_signals=macro_signals,
        date=date,
        account_id=account_id,
        strategy_id="macro_etf_strategy_v1",
        universe=universe,
    )
