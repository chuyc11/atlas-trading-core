"""Virtual account state and trade application."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trading_core.accounting.positions import Position, PositionBook, empty_positions
from trading_core.broker.market_rules import is_t_plus_one


@dataclass
class Account:
    account_id: str
    cash: float = 100000.0
    positions: PositionBook = field(default_factory=empty_positions)
    cumulative_return: float = 0.0
    high_watermark: float = 100000.0

    @property
    def market_value(self) -> float:
        return round(sum(position.market_value for position in self.positions.values()), 6)

    @property
    def total_asset(self) -> float:
        return round(self.cash + self.market_value, 6)

    def get_position(self, symbol: str, market: str) -> Position:
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol, market=market)
        return self.positions[symbol]

    def apply_trade(self, trade: dict[str, Any]) -> None:
        symbol = str(trade["symbol"])
        market = str(trade.get("market", "A_SHARE"))
        side = str(trade["side"]).upper()
        quantity = int(trade["filled_quantity"])
        price = float(trade["filled_price"])
        position = self.get_position(symbol, market)
        position.current_price = price

        if side == "BUY":
            self.cash = round(self.cash - float(trade["net_amount"]), 6)
            old_quantity = position.quantity
            new_quantity = old_quantity + quantity
            if new_quantity:
                position.avg_cost = round(
                    ((position.avg_cost * old_quantity) + (price * quantity)) / new_quantity,
                    6,
                )
            position.quantity = new_quantity
            if is_t_plus_one(market):
                position.pending_t1_quantity += quantity
            else:
                position.available_quantity += quantity
            position.last_buy_date = str(trade.get("date"))
        elif side == "SELL":
            self.cash = round(self.cash + float(trade["net_amount"]), 6)
            position.quantity -= quantity
            position.available_quantity = max(0, position.available_quantity - quantity)
            position.last_sell_date = str(trade.get("date"))
            if position.quantity <= 0:
                position.quantity = 0
                position.available_quantity = 0
                position.pending_t1_quantity = 0
                position.avg_cost = 0.0
        else:
            raise ValueError(f"Unsupported trade side: {side}")

    def settle_t_plus_one(self) -> None:
        for position in self.positions.values():
            if position.pending_t1_quantity:
                position.available_quantity += position.pending_t1_quantity
                position.pending_t1_quantity = 0

    def mark_prices(self, prices: dict[str, float]) -> None:
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = float(price)

    def to_portfolio(self, date: str, previous_total_asset: float | None = None) -> dict[str, Any]:
        total = self.total_asset
        previous = previous_total_asset if previous_total_asset not in (None, 0) else total
        daily_return = (total / previous) - 1 if previous else 0.0
        self.high_watermark = max(self.high_watermark, total)
        max_drawdown = (total / self.high_watermark) - 1 if self.high_watermark else 0.0
        return {
            "date": date,
            "account_id": self.account_id,
            "cash": round(self.cash, 6),
            "market_value": self.market_value,
            "total_asset": total,
            "daily_return": round(daily_return, 8),
            "cumulative_return": round(self.cumulative_return, 8),
            "max_drawdown": round(max_drawdown, 8),
            "positions": [
                position.to_dict(total)
                for position in self.positions.values()
                if position.quantity > 0
            ],
        }


def account_from_portfolio(payload: dict[str, Any] | None, account_id: str, initial_cash: float) -> Account:
    if not payload:
        return Account(account_id=account_id, cash=initial_cash, high_watermark=initial_cash)
    account = Account(
        account_id=account_id,
        cash=float(payload.get("cash", initial_cash)),
        cumulative_return=float(payload.get("cumulative_return", 0.0)),
        high_watermark=max(float(payload.get("total_asset", initial_cash)), initial_cash),
    )
    for row in payload.get("positions", []):
        position = Position(
            symbol=str(row["symbol"]),
            market=str(row.get("market", "A_SHARE")),
            quantity=int(row.get("quantity", 0)),
            available_quantity=int(row.get("available_quantity", 0)),
            avg_cost=float(row.get("avg_cost", 0.0)),
            current_price=float(row.get("current_price", 0.0)),
            strategy_id=str(row.get("strategy_id", "macro_etf_strategy_v1")),
            pending_t1_quantity=int(row.get("pending_t1_quantity", 0)),
            last_buy_date=row.get("last_buy_date"),
            last_sell_date=row.get("last_sell_date"),
        )
        if position.quantity > 0:
            account.positions[position.symbol] = position
    return account
