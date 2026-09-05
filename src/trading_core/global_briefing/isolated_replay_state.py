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
    equity: float | None
    currency: str = "CNY"
    created_at: str = field(default_factory=utc_now)
    isolated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "cash": self.cash,
            "equity": float(self.equity) if self.equity is not None else None,
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
    reference_price: float | None = None
    slippage_bps: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "replay_id": self.replay_id,
            "date": self.date,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": int(self.quantity),
            "price": float(self.price),
            "execution_price": float(self.price),
            "reference_price": float(self.reference_price) if self.reference_price is not None else float(self.price),
            "slippage_bps": float(self.slippage_bps),
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
    reference_price: float | None = None
    slippage_bps: float = 0.0
    slippage_cost: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        reference_price = float(self.reference_price) if self.reference_price is not None else float(self.price)
        total_transaction_cost = float(self.fee) + float(self.tax) + float(self.slippage_cost)
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "replay_id": self.replay_id,
            "date": self.date,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": int(self.quantity),
            "price": float(self.price),
            "execution_price": float(self.price),
            "reference_price": reference_price,
            "notional": float(self.notional),
            "fee": float(self.fee),
            "commission": float(self.fee),
            "tax": float(self.tax),
            "slippage_bps": float(self.slippage_bps),
            "slippage_cost": float(self.slippage_cost),
            "total_transaction_cost": total_transaction_cost,
            "costs": {
                "commission": float(self.fee),
                "tax": float(self.tax),
                "slippage": float(self.slippage_cost),
                "total": total_transaction_cost,
            },
            "isolated": self.isolated,
        }


@dataclass
class ReplayValuation:
    replay_id: str
    date: str
    cash: float
    market_value: float | None
    equity: float | None
    positions: list[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)
    isolated: bool = True
    valuation_valid: bool = True
    price_observations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "date": self.date,
            "cash": float(self.cash),
            "market_value": float(self.market_value) if self.market_value is not None else None,
            "equity": float(self.equity) if self.equity is not None else None,
            "positions": self.positions,
            "warnings": list(self.warnings),
            "isolated": self.isolated,
            "valuation_valid": self.valuation_valid,
            "price_observations": list(self.price_observations),
        }


@dataclass
class ReplayDayResult:
    replay_id: str
    date: str
    signals: int
    orders: int
    trades: int
    cash: float
    equity: float | None
    warnings: list[str] = field(default_factory=list)
    isolated: bool = True
    valuation_valid: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "date": self.date,
            "signals": int(self.signals),
            "orders": int(self.orders),
            "trades": int(self.trades),
            "cash": float(self.cash),
            "equity": float(self.equity) if self.equity is not None else None,
            "warnings": list(self.warnings),
            "isolated": self.isolated,
            "valuation_valid": self.valuation_valid,
        }


@dataclass
class ReplayState:
    replay_id: str
    account: ReplayAccount
    positions: dict[str, ReplayPosition] = field(default_factory=dict)
    day_results: list[ReplayDayResult] = field(default_factory=list)
    isolated: bool = True
    last_prices: dict[str, dict[str, Any]] = field(default_factory=dict, repr=False)

    @classmethod
    def initialize(cls, replay_id: str, initial_cash: float, currency: str = "CNY") -> ReplayState:
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
