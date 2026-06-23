"""Benchmark generation for virtual portfolios."""

from __future__ import annotations

from statistics import mean
from typing import Any

from trading_core.config_loader import load_config
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json
from trading_core.universe.universe_loader import universe_symbols


def _pct_to_return(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value) / 100


def _return_from_price_row(row: dict[str, Any] | None) -> float:
    if not row:
        return 0.0
    price = row.get("price")
    previous_close = row.get("previous_close")
    # Prefer explicit price math when available. Real global-briefing
    # snapshots express change_pct in percent units, e.g. 0.63 means 0.63%.
    if price is not None and previous_close not in (None, 0):
        return (float(price) / float(previous_close)) - 1
    if row.get("change_pct") is not None:
        return _pct_to_return(row.get("change_pct"))
    return 0.0


def build_benchmark(
    date: str,
    portfolio: dict[str, Any],
    prices: dict[str, dict[str, Any]],
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    config = load_config("benchmarks.yaml")
    universe = universe_symbols()
    results = {}
    for row in config["benchmarks"]:
        benchmark_id = row["benchmark_id"]
        symbol = row["symbol"]
        if benchmark_id == "CASH":
            result_return = 0.0
        elif benchmark_id == "EQUAL_ETF":
            returns = [_return_from_price_row(prices[s]) for s in universe if s in prices]
            result_return = mean(returns) if returns else 0.0
        else:
            result_return = _return_from_price_row(prices.get(symbol))
        results[benchmark_id] = {
            "symbol": symbol,
            "name": row["name"],
            "return": round(result_return, 8),
        }
    portfolio_return = float(portfolio.get("daily_return", 0.0))
    payload = {
        "date": date,
        "account_id": portfolio.get("account_id"),
        "portfolio_return": round(portfolio_return, 8),
        "benchmarks": results,
        "excess_return": {
            key: round(portfolio_return - value["return"], 8)
            for key, value in results.items()
        },
    }
    paths = paths or project_paths()
    write_json(paths.dated_json("benchmarks", "benchmark", date), payload)
    return payload
