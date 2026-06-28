"""Valuation price selection for virtual portfolio tracking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from trading_core.equity_portfolio_tracking.tracking_config import TRACKING_FLAGS
from trading_core.equity_portfolio_tracking.tracking_inputs import TrackingInputs
from trading_core.system.common import relative


@dataclass(frozen=True)
class ValuationPrice:
    symbol: str
    as_of_date: str
    price: float
    price_field: str
    price_source_path: str
    source: str
    provider: str
    adjustment_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "as_of_date": self.as_of_date,
            "valuation_price": self.price,
            "price_field": self.price_field,
            "price_source_path": self.price_source_path,
            "source": self.source,
            "provider": self.provider,
            "adjustment_type": self.adjustment_type,
            "valuation_price_policy": "adjusted_close_then_close",
            **TRACKING_FLAGS,
        }


def build_valuation_prices(inputs: TrackingInputs) -> dict[str, ValuationPrice]:
    symbols = sorted({str(row.get("symbol")) for rows in inputs.portfolios.values() for row in rows if row.get("symbol")})
    prices: dict[str, ValuationPrice] = {}
    for symbol in symbols:
        prices[symbol] = valuation_price_for_symbol(inputs, symbol)
    return prices


def valuation_price_for_symbol(inputs: TrackingInputs, symbol: str) -> ValuationPrice:
    adjusted = _row_for_symbol(inputs.adjusted_prices, symbol)
    if adjusted is not None:
        price = _positive_float(adjusted.get("adj_close"))
        if price is not None:
            return ValuationPrice(
                symbol=symbol,
                as_of_date=inputs.as_of_date,
                price=price,
                price_field="adj_close",
                price_source_path=relative(inputs.adjusted_price_history_path, _project_root(inputs.adjusted_price_history_path)),
                source=str(adjusted.get("source") or ""),
                provider=str(adjusted.get("provider") or ""),
                adjustment_type=str(adjusted.get("adjustment_type") or ""),
            )
    daily = _row_for_symbol(inputs.daily_prices, symbol)
    if daily is not None:
        price = _positive_float(daily.get("close"))
        if price is not None:
            return ValuationPrice(
                symbol=symbol,
                as_of_date=inputs.as_of_date,
                price=price,
                price_field="close",
                price_source_path=relative(inputs.daily_price_history_path, _project_root(inputs.daily_price_history_path)),
                source=str(daily.get("source") or ""),
                provider=str(daily.get("provider") or ""),
                adjustment_type="raw_close_fallback",
            )
    raise ValueError(f"valuation price missing for {symbol} on {inputs.as_of_date}")


def _row_for_symbol(frame: pd.DataFrame, symbol: str) -> dict[str, Any] | None:
    if frame.empty or "symbol" not in frame.columns:
        return None
    rows = frame[frame["symbol"].astype(str) == symbol]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


def _positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(number) or number <= 0.0:
        return None
    return number


def _project_root(path):
    # .../work/trading-core/data/equity_market/history/file.parquet
    return path.parents[3]
