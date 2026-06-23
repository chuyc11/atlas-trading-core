"""Position helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Position:
    symbol: str
    market: str
    quantity: int = 0
    available_quantity: int = 0
    avg_cost: float = 0.0
    current_price: float = 0.0
    strategy_id: str = "macro_etf_strategy_v1"
    pending_t1_quantity: int = 0
    last_buy_date: str | None = None
    last_sell_date: str | None = None

    @property
    def market_value(self) -> float:
        return round(self.quantity * self.current_price, 6)

    @property
    def unrealized_pnl(self) -> float:
        return round((self.current_price - self.avg_cost) * self.quantity, 6)

    def to_dict(self, total_asset: float | None = None) -> dict[str, object]:
        weight = self.market_value / total_asset if total_asset else 0.0
        return {
            "symbol": self.symbol,
            "market": self.market,
            "quantity": self.quantity,
            "available_quantity": self.available_quantity,
            "avg_cost": round(self.avg_cost, 6),
            "current_price": round(self.current_price, 6),
            "market_value": self.market_value,
            "unrealized_pnl": self.unrealized_pnl,
            "weight": round(weight, 6),
            "strategy_id": self.strategy_id,
            "pending_t1_quantity": self.pending_t1_quantity,
            "last_buy_date": self.last_buy_date,
            "last_sell_date": self.last_sell_date,
        }


PositionBook = dict[str, Position]


def positions_from_dict(rows: list[dict[str, object]]) -> PositionBook:
    return {str(row["symbol"]): Position(**row) for row in rows}


def empty_positions() -> PositionBook:
    return {}
