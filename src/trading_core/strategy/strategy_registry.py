"""Strategy registry for first-stage rule strategies."""

from __future__ import annotations


def default_strategy_registry() -> dict[str, dict[str, str]]:
    return {
        "hold_strategy": {"status": "active_normal", "mode": "main"},
        "macro_etf_strategy_v1": {"status": "active_small", "mode": "main"},
        "momentum_strategy_v1": {"status": "shadow", "mode": "shadow"},
    }
