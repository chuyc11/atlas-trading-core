"""Risk state summaries for reports and promotion gates."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class RiskState:
    account_id: str
    date: str
    rejected_orders: int
    accepted_orders: int
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def summarize_risk(date: str, account_id: str, orders: list[dict[str, Any]]) -> dict[str, Any]:
    rejected = [order for order in orders if order.get("risk_check") == "rejected"]
    accepted = [order for order in orders if order.get("risk_check") == "passed"]
    return RiskState(
        account_id=account_id,
        date=date,
        rejected_orders=len(rejected),
        accepted_orders=len(accepted),
        notes=[str(order.get("risk_reason")) for order in rejected],
    ).to_dict()
