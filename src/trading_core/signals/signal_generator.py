"""Convert macro signals into trading signals."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from trading_core.signals.trading_signal import TradingSignal
from trading_core.universe.universe_loader import universe_by_symbol


CONFIDENCE_MAP = {"high": 0.75, "medium": 0.60, "low": 0.40}
MIN_BUY_CONFIDENCE = 0.50


def confidence_to_score(value: str | float | int | None, risk_flags: list[str] | None = None) -> float:
    if isinstance(value, (int, float)):
        base = float(value)
    else:
        base = CONFIDENCE_MAP.get(str(value or "low").lower(), 0.40)
    penalty = 0.05 * len(risk_flags or [])
    return max(0.0, round(base - penalty, 4))


def generate_trading_signals(
    macro_signals: list[dict[str, Any]],
    date: str,
    account_id: str = "CHINA_PAPER",
    strategy_id: str = "macro_etf_strategy_v1",
    universe: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    by_symbol = universe_by_symbol(universe)
    rows: list[dict[str, Any]] = []
    sequence = 1
    for macro in macro_signals:
        risk_flags = list(macro.get("risk_flags", []))
        confidence = confidence_to_score(macro.get("confidence"), risk_flags)
        if confidence < MIN_BUY_CONFIDENCE:
            continue
        raw_side = str(macro.get("side") or macro.get("action") or "LONG").upper()
        side = "SELL" if raw_side in {"SELL", "REDUCE", "EXIT"} else "LONG"
        for symbol in macro.get("affected_assets", []):
            asset = by_symbol.get(symbol)
            if not asset:
                continue
            signal = TradingSignal(
                signal_id=f"SIG-{date.replace('-', '')}-{sequence:03d}",
                macro_signal_id=macro.get("macro_signal_id"),
                date=date,
                strategy_id=strategy_id,
                account_id=account_id,
                symbol=symbol,
                market=asset["market"],
                signal_time=f"{date} 15:10:00",
                side=side,
                target_weight=float(macro.get("target_weight", 0.05)),
                confidence=confidence,
                reason=str(macro.get("scenario") or "macro signal maps to ETF universe"),
                risk_flags=risk_flags,
            )
            rows.append(signal.to_dict())
            sequence += 1
    return rows


def hold_signal(date: str, account_id: str, reason: str) -> dict[str, Any]:
    return {
        "signal_id": f"HOLD-{date.replace('-', '')}-001",
        "macro_signal_id": None,
        "date": date,
        "strategy_id": "hold_strategy",
        "account_id": account_id,
        "symbol": "CASH",
        "market": "CASH",
        "signal_time": f"{date} 15:10:00",
        "side": "HOLD",
        "target_weight": 0.0,
        "confidence": 1.0,
        "reason": reason,
        "risk_flags": ["no_trade"],
        "status": "hold",
    }
