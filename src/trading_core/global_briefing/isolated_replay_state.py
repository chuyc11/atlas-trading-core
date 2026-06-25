"""State model for isolated global-briefing historical replay."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass
class ReplayAccount:
    replay_id: str
    cash: float
    equity: float
    currency: str = "CNY"
    created_at: str = field(default_factory=utc_now)
    isolated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "cash": self.cash,
            "equity": self.equity,
            "currency": self.currency,
            "created_at": self.created_at,
            "isolated": self.isolated,
        }


@dataclass
class ReplayPosition:
    replay_id: str
    symbol: str
    quantity: int = 0
    avg_cost: float = 0.0
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    isolated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "symbol": self.symbol,
            "quantity": int(self.quantity),
            "avg_cost": float(self.avg_cost),
            "market_value": float(self.market_value),
            "unrealized_pnl": float(self.unrealized_pnl),
            "isolated": self.isolated,
        }


@dataclass
class ReplaySignal:
    replay_id: str
    replay_date: str
    symbol: str
    target_weight: float
    reason: str
    source_signal_as_of_date: str | None
    source_signal_generated_at: str | None
    isolated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "replay_date": self.replay_date,
            "symbol": self.symbol,
            "target_weight": float(self.target_weight),
            "reason": self.reason,
            "source_signal_as_of_date": self.source_signal_as_of_date,
            "source_signal_generated_at": self.source_signal_generated_at,
            "isolated": self.isolated,
        }


@dataclass
class ReplayOrder:
    order_id: str
    replay_id: str
    date: str
    symbol: str
    side: str
    quantity: int
    price: float
    status: str
    reason: str = "isolated_replay_order"
    isolated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "replay_id": self.replay_id,
            "date": self.date,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": int(self.quantity),
            "price": float(self.price),
            "status": self.status,
            "reason": self.reason,
            "isolated": self.isolated,
        }


@dataclass
class ReplayTrade:
    trade_id: str
    order_id: str
    replay_id: str
    date: str
    symbol: str
    side: str
    quantity: int
    price: float
    notional: float
    fee: float
    tax: float = 0.0
    isolated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "replay_id": self.replay_id,
            "date": self.date,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": int(self.quantity),
            "price": float(self.price),
            "notional": float(self.notional),
            "fee": float(self.fee),
            "tax": float(self.tax),
            "isolated": self.isolated,
        }


@dataclass
class ReplayValuation:
    replay_id: str
    date: str
    cash: float
    market_value: float
    equity: float
    positions: list[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)
    isolated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "date": self.date,
            "cash": float(self.cash),
            "market_value": float(self.market_value),
            "equity": float(self.equity),
            "positions": self.positions,
            "warnings": list(self.warnings),
            "isolated": self.isolated,
        }


@dataclass
class ReplayDayResult:
    replay_id: str
    date: str
    signals: int
    orders: int
    trades: int
    cash: float
    equity: float
    warnings: list[str] = field(default_factory=list)
    isolated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "date": self.date,
            "signals": int(self.signals),
            "orders": int(self.orders),
            "trades": int(self.trades),
            "cash": float(self.cash),
            "equity": float(self.equity),
            "warnings": list(self.warnings),
            "isolated": self.isolated,
        }


@dataclass
class ReplayState:
    replay_id: str
    account: ReplayAccount
    positions: dict[str, ReplayPosition] = field(default_factory=dict)
    day_results: list[ReplayDayResult] = field(default_factory=list)
    isolated: bool = True

    @classmethod
    def initialize(cls, replay_id: str, initial_cash: float, currency: str = "CNY") -> "ReplayState":
        account = ReplayAccount(replay_id=replay_id, cash=float(initial_cash), equity=float(initial_cash), currency=currency)
        return cls(replay_id=replay_id, account=account)

    def get_position(self, symbol: str) -> ReplayPosition:
        if symbol not in self.positions:
            self.positions[symbol] = ReplayPosition(replay_id=self.replay_id, symbol=symbol)
        return self.positions[symbol]

    def active_positions(self) -> list[ReplayPosition]:
        return [position for position in self.positions.values() if position.quantity > 0]

    def record_day(self, result: ReplayDayResult) -> None:
        self.day_results.append(result)

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "isolated": self.isolated,
            "account": self.account.to_dict(),
            "positions": [position.to_dict() for position in sorted(self.positions.values(), key=lambda item: item.symbol)],
            "day_results": [result.to_dict() for result in self.day_results],
        }
