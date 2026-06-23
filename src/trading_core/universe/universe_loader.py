"""Universe loading and validation."""

from __future__ import annotations

from typing import Any

from trading_core.config_loader import load_config


REQUIRED_FIELDS = {"symbol", "market", "asset_type"}


def load_universe(config: dict[str, Any] | None = None) -> dict[str, Any]:
    universe = config or load_config("universe_china_etf.yaml")
    symbols = universe.get("symbols", [])
    if not isinstance(symbols, list) or not symbols:
        raise ValueError("Universe must contain non-empty symbols")
    for item in symbols:
        missing = REQUIRED_FIELDS - item.keys()
        if missing:
            raise ValueError(f"Universe item missing fields: {sorted(missing)}")
    return universe


def universe_symbols(universe: dict[str, Any] | None = None, market: str | None = None) -> list[str]:
    data = load_universe(universe)
    symbols = data["symbols"]
    if market:
        symbols = [item for item in symbols if item["market"] == market]
    return [item["symbol"] for item in symbols]


def universe_by_symbol(universe: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    data = load_universe(universe)
    return {item["symbol"]: item for item in data["symbols"]}
