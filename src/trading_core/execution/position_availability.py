"""Position availability rules for T+1 markets."""

from __future__ import annotations

from dataclasses import dataclass, field

from trading_core.execution.trading_calendar_contract import default_calendar


@dataclass
class AvailabilityBook:
    market: str = "SSE"
    position: int = 0
    available: int = 0
    pending_by_settle_date: dict[str, int] = field(default_factory=dict)

    def buy(self, quantity: int, trade_date: str) -> str:
        self.position += quantity
        settle = default_calendar().next_trading_day(trade_date, self.market)
        self.pending_by_settle_date[settle] = self.pending_by_settle_date.get(settle, 0) + quantity
        return settle

    def settle(self, date: str) -> None:
        matured = [day for day in self.pending_by_settle_date if day <= date]
        for day in matured:
            self.available += self.pending_by_settle_date.pop(day)

    def sell(self, quantity: int) -> bool:
        if quantity > self.position or quantity > self.available:
            return False
        self.position -= quantity
        self.available -= quantity
        return True


def t_plus_one_available_after(trade_date: str, market: str = "SSE") -> str:
    return default_calendar().next_trading_day(trade_date, market)

