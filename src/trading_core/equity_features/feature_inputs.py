"""Input loading for A-share multi-horizon feature engineering."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import normalize_symbol, read_frame
from trading_core.equity_features.feature_config import DEFAULT_AS_OF_DATE
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


@dataclass(frozen=True)
class FeatureInputs:
    as_of_date: str
    requested_as_of_date: str
    tradable_universe_path: Path
    strict_universe: pd.DataFrame
    excluded_symbols: set[str]
    price_history: pd.DataFrame
    adjusted_price_history: pd.DataFrame
    daily_basic_history: pd.DataFrame
    daily_basic_snapshot: pd.DataFrame
    financial_history: pd.DataFrame
    industry_classification: pd.DataFrame
    source_dates: dict[str, str]


def load_feature_inputs(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_latest_tradable_universe: bool = False,
) -> FeatureInputs:
    paths = default_paths(paths)
    requested = as_of_date
    selected_date, universe_path = _resolve_universe_path(paths, as_of_date, allow_latest_tradable_universe)
    strict = _read_universe(universe_path)
    if strict.empty:
        raise ValueError(f"strict tradable universe is empty: {universe_path}")
    strict["symbol"] = strict["symbol"].map(normalize_symbol)
    excluded_path = paths.data_dir / "equity_selection" / "daily" / selected_date / "excluded_universe.json"
    excluded = {
        normalize_symbol(row.get("symbol"))
        for row in _read_json_list(excluded_path)
        if row.get("symbol")
    }
    price = _prepare_price(read_frame(paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet"), selected_date)
    adjusted = _prepare_adjusted(read_frame(paths.data_dir / "equity_market" / "history" / "adjusted_price_history_panel.parquet"), selected_date)
    basic_history = _prepare_date_symbol(read_frame(paths.data_dir / "equity_market" / "history" / "daily_basic_history_panel.parquet"), selected_date, "date")
    basic_snapshot = _prepare_date_symbol(read_frame(paths.data_dir / "equity_market" / "daily_basic_panel.parquet"), selected_date, "date")
    financial = _prepare_financial(read_frame(paths.data_dir / "equity_fundamental" / "history" / "basic_financials_history_panel.parquet"), selected_date)
    industry = _prepare_industry(read_frame(paths.data_dir / "equity_industry" / "industry_classification.parquet"), selected_date)
    source_dates = {
        "max_price_date_used": _max_date(price, "date"),
        "max_adjusted_price_date_used": _max_date(adjusted, "date"),
        "max_daily_basic_date_used": max(_max_date(basic_history, "date"), _max_date(basic_snapshot, "date")),
        "max_financial_ann_date_used": _max_date(financial, "ann_date"),
        "max_industry_effective_date_used": _max_date(industry, "effective_date"),
    }
    return FeatureInputs(
        as_of_date=selected_date,
        requested_as_of_date=requested,
        tradable_universe_path=universe_path,
        strict_universe=strict,
        excluded_symbols=excluded,
        price_history=price,
        adjusted_price_history=adjusted,
        daily_basic_history=basic_history,
        daily_basic_snapshot=basic_snapshot,
        financial_history=financial,
        industry_classification=industry,
        source_dates=source_dates,
    )


def feature_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_features" / "daily" / as_of_date


def feature_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_features" / "daily" / as_of_date


def _resolve_universe_path(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> tuple[str, Path]:
    base = paths.data_dir / "equity_selection" / "daily"
    exact = base / as_of_date / "strict_tradable_universe.json"
    if exact.exists():
        return as_of_date, exact
    parquet = base / as_of_date / "tradable_universe.parquet"
    if parquet.exists():
        return as_of_date, parquet
    if not allow_latest:
        raise ValueError(f"strict tradable universe not found for as_of_date={as_of_date}")
    candidates = sorted(path for path in base.glob("*/strict_tradable_universe.json") if path.parent.name <= as_of_date)
    if not candidates:
        raise ValueError(f"no strict tradable universe available on or before {as_of_date}")
    selected = candidates[-1]
    return selected.parent.name, selected


def _read_universe(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path) if path.suffix == ".parquet" else pd.DataFrame(_read_json_list(path))
    if "bucket" in frame.columns:
        frame = frame[frame["bucket"].astype(str) == "strict_tradable_universe"].copy()
    return frame.drop_duplicates("symbol").sort_values("symbol") if not frame.empty else frame


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else []


def _prepare_price(frame: pd.DataFrame, as_of_date: str) -> pd.DataFrame:
    frame = _prepare_date_symbol(frame, as_of_date, "date")
    for column in ["open", "high", "low", "close", "volume", "amount", "turnover", "pre_close", "pct_change"]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def _prepare_adjusted(frame: pd.DataFrame, as_of_date: str) -> pd.DataFrame:
    frame = _prepare_date_symbol(frame, as_of_date, "date")
    for column in ["adj_open", "adj_high", "adj_low", "adj_close", "adj_factor"]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def _prepare_financial(frame: pd.DataFrame, as_of_date: str) -> pd.DataFrame:
    frame = _prepare_date_symbol(frame, as_of_date, "ann_date")
    if "report_date" in frame.columns:
        frame = frame[frame["report_date"].astype(str) <= as_of_date].copy()
    for column in ["revenue", "net_profit", "roe", "gross_margin", "net_margin", "operating_cash_flow", "debt_to_asset", "eps", "bps"]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def _prepare_industry(frame: pd.DataFrame, as_of_date: str) -> pd.DataFrame:
    return _prepare_date_symbol(frame, as_of_date, "effective_date")


def _prepare_date_symbol(frame: pd.DataFrame, as_of_date: str, date_column: str) -> pd.DataFrame:
    if frame.empty:
        return frame
    data = frame.copy()
    if "symbol" in data.columns:
        data["symbol"] = data["symbol"].map(normalize_symbol)
    if date_column in data.columns:
        data[date_column] = data[date_column].astype(str).str[:10]
        data = data[data[date_column] <= as_of_date].copy()
    if "date" in data.columns:
        data["date"] = data["date"].astype(str).str[:10]
    return data


def _max_date(frame: pd.DataFrame, column: str) -> str:
    if frame.empty or column not in frame.columns:
        return ""
    values = frame[column].dropna().astype(str)
    return str(values.max())[:10] if not values.empty else ""

