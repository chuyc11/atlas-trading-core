"""Append-only ledger entries for virtual trading."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class LedgerEntry:
    date: str
    account_id: str
    entry_type: str
    symbol: str | None
    cash_delta: float
    quantity_delta: int
    reason: str
    ref_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
