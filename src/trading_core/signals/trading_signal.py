"""Trading signal data helpers."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class TradingSignal:
    signal_id: str
    macro_signal_id: str | None
    date: str
    strategy_id: str
    account_id: str
    symbol: str
    market: str
    signal_time: str
    side: str
    target_weight: float
    confidence: float
    reason: str
    risk_flags: list[str]
    status: str = "candidate"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
