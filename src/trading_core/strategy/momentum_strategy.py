"""Simple shadow momentum strategy."""

from __future__ import annotations

from typing import Any


def generate_momentum_shadow_signals(
    prices: dict[str, dict[str, Any]],
    date: str,
    account_id: str,
    max_assets: int = 2,
) -> list[dict[str, Any]]:
    ranked = sorted(
        (
            (symbol, float(row.get("change_pct") or 0.0), row)
            for symbol, row in prices.items()
            if row.get("price") is not None
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    rows: list[dict[str, Any]] = []
    for index, (symbol, _, row) in enumerate(ranked[:max_assets], 1):
        rows.append(
            {
                "signal_id": f"SHADOW-MOM-{date.replace('-', '')}-{index:03d}",
                "macro_signal_id": None,
                "date": date,
                "strategy_id": "momentum_strategy_v1",
                "account_id": account_id,
                "symbol": symbol,
                "market": row.get("raw", {}).get("market", "A_SHARE"),
                "signal_time": f"{date} 15:10:00",
                "side": "LONG",
                "target_weight": 0.05,
                "confidence": 0.5,
                "reason": "shadow momentum rank",
                "risk_flags": ["shadow"],
                "status": "shadow",
            }
        )
    return rows
