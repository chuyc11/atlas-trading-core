"""Virtual account state and trade application."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trading_core.accounting.positions import Position, PositionBook, empty_positions
from trading_core.broker.market_rules import is_t_plus_one
from trading_core.calendar.trading_calendar import is_trading_day, next_trading_day, parse_date


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
        if trade.get("status", "filled") != "filled":
            return
        symbol = str(trade["symbol"])
        market = str(trade.get("market", "A_SHARE"))
        side = str(trade["side"]).upper()
        quantity = int(trade["filled_quantity"])
        price = float(trade["filled_price"])
        trade_date = str(trade["date"]) if trade.get("date") is not None else None
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
                position.pending_t1_lots.append(
                    {
                        "quantity": quantity,
                        "buy_date": trade_date,
                        "settlement_date": _settlement_date_for_trade(trade, market),
                    }
                )
                position.pending_t1_quantity = _pending_quantity(position.pending_t1_lots)
            else:
                position.available_quantity += quantity
            position.last_buy_date = trade_date
        elif side == "SELL":
            self.cash = round(self.cash + float(trade["net_amount"]), 6)
            position.quantity -= quantity
            position.available_quantity = max(0, position.available_quantity - quantity)
            position.last_sell_date = trade_date
            if position.quantity <= 0:
                position.quantity = 0
                position.available_quantity = 0
                position.pending_t1_quantity = 0
                position.pending_t1_lots = []
                position.avg_cost = 0.0
        else:
            raise ValueError(f"Unsupported trade side: {side}")

    def settle_t_plus_one(
        self,
        settlement_date: str | None = None,
        *,
        paths: Any | None = None,
        calendar_path: Any | None = None,
    ) -> None:
        for position in self.positions.values():
            if position.pending_t1_quantity and not position.pending_t1_lots:
                position.pending_t1_lots = _legacy_pending_lots(position, paths=paths, calendar_path=calendar_path)
            if not position.pending_t1_lots:
                continue
            if settlement_date is None:
                settled_quantity = _pending_quantity(position.pending_t1_lots)
                position.available_quantity += settled_quantity
                position.pending_t1_lots = []
                position.pending_t1_quantity = 0
                continue
            if not is_trading_day(settlement_date, position.market, paths=paths, calendar_path=calendar_path):
                continue
            cutoff = parse_date(settlement_date)
            settled_quantity = 0
            remaining_lots: list[dict[str, Any]] = []
            for lot in position.pending_t1_lots:
                quantity_to_settle = int(lot.get("quantity", 0))
                lot_settlement_date = lot.get("settlement_date")
                if lot_settlement_date is not None and parse_date(str(lot_settlement_date)) <= cutoff:
                    settled_quantity += quantity_to_settle
                else:
                    remaining_lots.append(lot)
            if settled_quantity:
                position.available_quantity += settled_quantity
            position.pending_t1_lots = remaining_lots
            position.pending_t1_quantity = _pending_quantity(remaining_lots)

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


def account_from_portfolio(
    payload: dict[str, Any] | None,
    account_id: str,
    initial_cash: float,
    *,
    paths: Any | None = None,
    calendar_path: Any | None = None,
) -> Account:
    if not payload:
        return Account(account_id=account_id, cash=initial_cash, high_watermark=initial_cash)
    account = Account(
        account_id=account_id,
        cash=float(payload.get("cash", initial_cash)),
        cumulative_return=float(payload.get("cumulative_return", 0.0)),
        high_watermark=max(float(payload.get("total_asset", initial_cash)), initial_cash),
    )
    for row in payload.get("positions", []):
        pending_lots = _normalize_pending_lots(row.get("pending_t1_lots", []))
        pending_quantity = _pending_quantity(pending_lots) if pending_lots else int(row.get("pending_t1_quantity", 0))
        position = Position(
            symbol=str(row["symbol"]),
            market=str(row.get("market", "A_SHARE")),
            quantity=int(row.get("quantity", 0)),
            available_quantity=int(row.get("available_quantity", 0)),
            avg_cost=float(row.get("avg_cost", 0.0)),
            current_price=float(row.get("current_price", 0.0)),
            strategy_id=str(row.get("strategy_id", "macro_etf_strategy_v1")),
            pending_t1_quantity=pending_quantity,
            pending_t1_lots=pending_lots,
            last_buy_date=row.get("last_buy_date"),
            last_sell_date=row.get("last_sell_date"),
        )
        if position.pending_t1_quantity and not position.pending_t1_lots:
            position.pending_t1_lots = _legacy_pending_lots(position, paths=paths, calendar_path=calendar_path)
            position.pending_t1_quantity = _pending_quantity(position.pending_t1_lots)
        if position.quantity > 0:
            account.positions[position.symbol] = position
    return account


def _settlement_date_for_trade(trade: dict[str, Any], market: str) -> str | None:
    explicit = trade.get("settlement_date")
    if explicit is not None:
        return str(explicit)
    trade_date = trade.get("date")
    if trade_date is None:
        return None
    return next_trading_day(
        str(trade_date),
        market,
        paths=trade.get("_paths"),
        calendar_path=trade.get("calendar_path"),
    )


def _legacy_pending_lots(position: Position, *, paths: Any | None = None, calendar_path: Any | None = None) -> list[dict[str, Any]]:
    if position.pending_t1_quantity <= 0:
        return []
    settlement_date = None
    if position.last_buy_date:
        settlement_date = next_trading_day(position.last_buy_date, position.market, paths=paths, calendar_path=calendar_path)
    return [
        {
            "quantity": position.pending_t1_quantity,
            "buy_date": position.last_buy_date,
            "settlement_date": settlement_date,
        }
    ]


def _normalize_pending_lots(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    lots: list[dict[str, Any]] = []
    for lot in value:
        if not isinstance(lot, dict):
            continue
        quantity = int(lot.get("quantity", 0))
        if quantity <= 0:
            continue
        lots.append(
            {
                "quantity": quantity,
                "buy_date": lot.get("buy_date"),
                "settlement_date": lot.get("settlement_date"),
            }
        )
    return lots


def _pending_quantity(lots: list[dict[str, Any]]) -> int:
    return sum(int(lot.get("quantity", 0)) for lot in lots)
