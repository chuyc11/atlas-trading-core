"""Input loading for v0.7.10 A-share benchmark comparison."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_benchmarks.benchmark_config import DEFAULT_AS_OF_DATE, required_input_paths
from trading_core.equity_data_quality.common import read_frame
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


@dataclass(frozen=True)
class BenchmarkInputs:
    as_of_date: str
    input_paths: dict[str, Path]
    workflow_artifacts: dict[str, Any]
    tracking_artifacts: dict[str, Any]
    selection_artifacts: dict[str, Any]
    portfolio_artifacts: dict[str, Any]
    strict_tradable_rows: list[dict[str, Any]]
    candidate_rows: dict[str, list[dict[str, Any]]]
    strict_tradable_symbols: list[str]
    candidate_symbols: list[str]
    adjusted_prices: pd.DataFrame
    daily_prices: pd.DataFrame


def load_benchmark_inputs(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    lookback_trading_days: int = 250,
) -> BenchmarkInputs:
    paths = default_paths(paths)
    input_paths = required_input_paths(paths, as_of_date)
    missing = [str(path) for path in input_paths.values() if not path.exists()]
    if missing:
        raise ValueError("benchmark inputs missing: " + "; ".join(missing))

    workflow_artifacts = {key: _load_json(path) for key, path in input_paths.items() if key.startswith("workflow_")}
    workflow_artifacts["workflow_audit"] = _load_json(input_paths["workflow_audit"])
    tracking_artifacts = {
        key: _load_json(path)
        for key, path in input_paths.items()
        if key.endswith("paper_ledger")
        or key.endswith("holdings_snapshot")
        or key
        in {
            "tracking_config",
            "portfolio_nav_snapshot",
            "portfolio_performance_snapshot",
            "tracking_manifest",
            "tracking_source_trace",
            "tracking_summary",
        }
    }
    selection_artifacts = {
        "tradable_universe": _load_json(input_paths["tradable_universe"]),
        "candidate_manifest": _load_json(input_paths["candidate_manifest"]),
    }
    candidate_rows = {
        "long_candidates": _load_list(input_paths["long_candidates"]),
        "mid_candidates": _load_list(input_paths["mid_candidates"]),
        "short_candidates": _load_list(input_paths["short_candidates"]),
        "multi_horizon_candidates": _load_list(input_paths["multi_horizon_candidates"]),
    }
    portfolio_artifacts = {
        "long_virtual_portfolio": _load_list(input_paths["long_virtual_portfolio"]),
        "mid_virtual_portfolio": _load_list(input_paths["mid_virtual_portfolio"]),
        "short_virtual_portfolio": _load_list(input_paths["short_virtual_portfolio"]),
        "portfolio_manifest": _load_json(input_paths["portfolio_manifest"]),
    }
    strict_rows = _load_list(input_paths["tradable_universe"])
    strict_symbols = _strict_tradable_symbols(strict_rows)
    candidate_symbols = _candidate_symbols(candidate_rows)
    all_symbols = sorted(set(strict_symbols).union(candidate_symbols))
    adjusted_prices = read_equity_price_history(
        input_paths["adjusted_price_history"],
        symbols=all_symbols,
        as_of_date=as_of_date,
        lookback_trading_days=lookback_trading_days,
        adjusted=True,
    )
    adjusted_as_of_symbols = (
        set(adjusted_prices.loc[adjusted_prices["date"].astype(str) == as_of_date, "symbol"].astype(str))
        if not adjusted_prices.empty and "date" in adjusted_prices.columns
        else set()
    )
    daily_symbols = sorted(set(all_symbols).difference(adjusted_as_of_symbols))
    daily_prices = read_equity_price_history(
        input_paths["daily_price_history"],
        symbols=daily_symbols,
        as_of_date=as_of_date,
        lookback_trading_days=lookback_trading_days,
        adjusted=False,
    )
    return BenchmarkInputs(
        as_of_date=as_of_date,
        input_paths=input_paths,
        workflow_artifacts=workflow_artifacts,
        tracking_artifacts=tracking_artifacts,
        selection_artifacts=selection_artifacts,
        portfolio_artifacts=portfolio_artifacts,
        strict_tradable_rows=strict_rows,
        candidate_rows=candidate_rows,
        strict_tradable_symbols=strict_symbols,
        candidate_symbols=candidate_symbols,
        adjusted_prices=adjusted_prices,
        daily_prices=daily_prices,
    )


def read_equity_price_history(
    path: Path,
    *,
    symbols: list[str],
    as_of_date: str,
    lookback_trading_days: int,
    adjusted: bool,
) -> pd.DataFrame:
    if not path.exists() or not symbols:
        return pd.DataFrame()
    columns = ["date", "symbol", "adj_close", "source", "provider"] if adjusted else ["date", "symbol", "close", "source", "provider"]
    begin = _begin_date(as_of_date, lookback_trading_days)
    filters = [("date", ">=", begin), ("date", "<=", as_of_date)]
    if len(symbols) <= 200:
        filters.append(("symbol", "in", symbols))
    try:
        frame = pd.read_parquet(path, columns=[column for column in columns if column], filters=filters)
    except Exception:
        frame = read_frame(path)
        if not frame.empty:
            keep = [column for column in columns if column in frame.columns]
            frame = frame[keep]
            frame = frame[(frame["date"].astype(str) >= begin) & (frame["date"].astype(str) <= as_of_date)]
    if frame.empty:
        return frame
    price_column = "adj_close" if adjusted and "adj_close" in frame.columns else "close"
    frame = frame.dropna(subset=["date", "symbol", price_column]).copy()
    frame["date"] = frame["date"].astype(str)
    frame["symbol"] = frame["symbol"].astype(str)
    frame = frame[frame["symbol"].isin(set(symbols))]
    frame = frame.sort_values(["symbol", "date"])
    return frame.groupby("symbol", group_keys=False).tail(lookback_trading_days + 1).reset_index(drop=True)


def _begin_date(as_of_date: str, lookback_trading_days: int) -> str:
    return (date.fromisoformat(as_of_date) - timedelta(days=max(lookback_trading_days * 3, 90))).isoformat()


def _strict_tradable_symbols(rows: list[dict[str, Any]]) -> list[str]:
    symbols = []
    for row in rows:
        passed = row.get("filter_passed")
        bucket = str(row.get("bucket") or "")
        if passed is True or (passed is None and bucket == "strict_tradable_universe"):
            symbol = row.get("symbol")
            if symbol:
                symbols.append(str(symbol))
    return sorted(set(symbols))


def _candidate_symbols(rows_by_file: dict[str, list[dict[str, Any]]]) -> list[str]:
    symbols = []
    for rows in rows_by_file.values():
        symbols.extend(str(row.get("symbol")) for row in rows if row.get("symbol"))
    return sorted(set(symbols))


def _load_json(path: Path) -> Any:
    value = json.loads(path.read_text(encoding="utf-8"))
    return value


def _load_list(path: Path) -> list[dict[str, Any]]:
    value = _load_json(path)
    return value if isinstance(value, list) else []
