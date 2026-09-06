"""Equal-weight benchmark construction."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_benchmarks.benchmark_config import BenchmarkConfig


def build_equal_weight_benchmark(
    *,
    benchmark_id: str,
    symbols: list[str],
    adjusted_prices: pd.DataFrame,
    daily_prices: pd.DataFrame,
    config: BenchmarkConfig,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    price_frame = _combined_price_frame(adjusted_prices, daily_prices, symbols)
    price_groups = {
        str(symbol): subset.sort_values("date")
        for symbol, subset in price_frame.groupby("symbol")
    } if not price_frame.empty else {}
    exclusions: list[dict[str, Any]] = []
    included_symbols: list[str] = []
    symbol_returns = []
    for symbol in sorted(set(symbols)):
        subset = price_groups.get(symbol, pd.DataFrame())
        subset = subset[subset["date"].astype(str) <= config.as_of_date]
        if subset.empty:
            exclusions.append(_exclusion(symbol, "missing_price_history"))
            continue
        if not (subset["date"].astype(str) == config.as_of_date).any():
            exclusions.append(_exclusion(symbol, "missing_as_of_price"))
            continue
        if subset["date"].nunique() < config.minimum_required_trading_days:
            exclusions.append(_exclusion(symbol, "insufficient_price_history"))
            continue
        included_symbols.append(symbol)
        subset = subset.tail(config.lookback_trading_days + 1).copy()
        subset["daily_return"] = subset["price"].pct_change().fillna(0.0)
        symbol_returns.append(subset[["date", "symbol", "daily_return"]])

    if not symbol_returns:
        availability = _availability(benchmark_id, "missing", "", "", 0, False, "no constituents with sufficient price data")
        return [], availability, _exclusion_report(benchmark_id, symbols, included_symbols, exclusions)

    returns_frame = pd.concat(symbol_returns, ignore_index=True)
    grouped = returns_frame.groupby("date", as_index=False).agg(daily_return=("daily_return", "mean"), component_return_count=("symbol", "nunique"))
    grouped = grouped.sort_values("date")
    records = [
        {
            "benchmark_id": benchmark_id,
            "date": str(row["date"]),
            "daily_return": float(row["daily_return"]),
            "component_return_count": int(row["component_return_count"]),
            "constituent_count": len(included_symbols),
            "source_type": "internal_equal_weight_as_of_universe",
            "is_placeholder": False,
        }
        for _, row in grouped.iterrows()
        if str(row["date"]) <= config.as_of_date
    ]
    as_of_available = any(row["date"] == config.as_of_date for row in records)
    status = "available" if len(records) >= config.minimum_required_trading_days and as_of_available else "failed"
    availability = _availability(
        benchmark_id,
        status,
        str(records[0]["date"]) if records else "",
        str(records[-1]["date"]) if records else "",
        len(records),
        as_of_available,
        None if status == "available" else "equal-weight benchmark history insufficient",
    )
    return records, availability, _exclusion_report(benchmark_id, symbols, included_symbols, exclusions)


def _combined_price_frame(adjusted_prices: pd.DataFrame, daily_prices: pd.DataFrame, symbols: list[str]) -> pd.DataFrame:
    frames = []
    if not adjusted_prices.empty and "adj_close" in adjusted_prices.columns:
        frames.append(
            adjusted_prices[adjusted_prices["symbol"].astype(str).isin(symbols)][["date", "symbol", "adj_close"]]
            .rename(columns={"adj_close": "price"})
            .assign(price_field="adj_close")
        )
    if not daily_prices.empty and "close" in daily_prices.columns:
        frames.append(
            daily_prices[daily_prices["symbol"].astype(str).isin(symbols)][["date", "symbol", "close"]]
            .rename(columns={"close": "price"})
            .assign(price_field="close")
        )
    if not frames:
        return pd.DataFrame(columns=["date", "symbol", "price", "price_field"])
    frame = pd.concat(frames, ignore_index=True)
    frame["date"] = frame["date"].astype(str)
    frame["symbol"] = frame["symbol"].astype(str)
    frame["price_source_rank"] = frame["price_field"].map({"adj_close": 0, "close": 1}).fillna(2)
    frame = frame.sort_values(["symbol", "date", "price_source_rank"]).drop_duplicates(["symbol", "date"], keep="first")
    return frame.drop(columns=["price_source_rank"]).reset_index(drop=True)


def _availability(benchmark_id: str, status: str, first: str, last: str, days: int, as_of_available: bool, reason: str | None) -> dict[str, Any]:
    return {
        "benchmark_id": benchmark_id,
        "status": status,
        "source_type": "internal_equal_weight_as_of_universe",
        "source_path": None,
        "symbol_or_index_code": "as_of_universe_constituents",
        "first_available_date": first,
        "last_available_date": last,
        "as_of_date_available": as_of_available,
        "trading_days_available": days,
        "missing_reason": reason,
        "is_placeholder": False,
    }


def _exclusion(symbol: str, reason: str) -> dict[str, Any]:
    return {"symbol": symbol, "reason": reason}


def _exclusion_report(benchmark_id: str, requested: list[str], included: list[str], exclusions: list[dict[str, Any]]) -> dict[str, Any]:
    reason_counts: dict[str, int] = {}
    for row in exclusions:
        reason_counts[row["reason"]] = reason_counts.get(row["reason"], 0) + 1
    return {
        "benchmark_id": benchmark_id,
        "requested_constituent_count": len(set(requested)),
        "constituent_count": len(included),
        "excluded_constituent_count": len(exclusions),
        "price_missing_count": reason_counts.get("missing_price_history", 0) + reason_counts.get("missing_as_of_price", 0),
        "exclusion_reasons": reason_counts,
        "excluded_constituents": exclusions[:500],
    }
