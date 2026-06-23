"""Default hold strategy."""

from __future__ import annotations

from trading_core.signals.signal_generator import hold_signal


def generate_hold(date: str, account_id: str, reason: str) -> list[dict[str, object]]:
    return [hold_signal(date, account_id, reason)]
