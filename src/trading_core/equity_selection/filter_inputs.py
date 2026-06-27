"""Input loading and as-of date handling for A-share tradable universe filtering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import data_quality_dir, read_frame, read_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


@dataclass(frozen=True)
class AsOfResolution:
    requested_as_of_date: str
    as_of_date: str
    used_previous_trading_day: bool
    previous_trading_day_reason: str


@dataclass(frozen=True)
class TradableUniverseInputs:
    equity_master: pd.DataFrame
    trading_calendar: pd.DataFrame
    daily_price_history: pd.DataFrame
    adjusted_price_history: pd.DataFrame
    daily_basic_history: pd.DataFrame
    daily_basic_snapshot: pd.DataFrame
    industry_classification: pd.DataFrame
    basic_financials_history: pd.DataFrame
    historical_symbol_manifest: dict[str, Any]
    coverage_audit: dict[str, Any]
    readiness_audit: dict[str, Any]


def load_tradable_universe_inputs(*, paths: ProjectPaths | None = None) -> TradableUniverseInputs:
    paths = default_paths(paths)
    return TradableUniverseInputs(
        equity_master=read_frame(paths.data_dir / "equity_universe" / "equity_master.parquet"),
        trading_calendar=read_frame(paths.data_dir / "equity_universe" / "trading_calendar.parquet"),
        daily_price_history=read_frame(paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet"),
        adjusted_price_history=read_frame(paths.data_dir / "equity_market" / "history" / "adjusted_price_history_panel.parquet"),
        daily_basic_history=read_frame(paths.data_dir / "equity_market" / "history" / "daily_basic_history_panel.parquet"),
        daily_basic_snapshot=read_frame(paths.data_dir / "equity_market" / "daily_basic_panel.parquet"),
        industry_classification=read_frame(paths.data_dir / "equity_industry" / "industry_classification.parquet"),
        basic_financials_history=read_frame(paths.data_dir / "equity_fundamental" / "history" / "basic_financials_history_panel.parquet"),
        historical_symbol_manifest=read_json(data_quality_dir(paths) / "a_share_historical_backfill_symbol_manifest.json"),
        coverage_audit=read_json(data_quality_dir(paths) / "a_share_historical_panel_coverage_audit.json"),
        readiness_audit=read_json(data_quality_dir(paths) / "a_share_feature_readiness_audit.json"),
    )


def resolve_as_of_date(calendar: pd.DataFrame, requested_as_of_date: str, *, allow_previous_trading_day: bool = False) -> AsOfResolution:
    if calendar.empty or "date" not in calendar.columns:
        raise ValueError("trading calendar is missing")
    trading_days = sorted(set(calendar.loc[calendar["is_trading_day"].fillna(False).astype(bool), "date"].astype(str)))
    if requested_as_of_date in trading_days:
        return AsOfResolution(
            requested_as_of_date=requested_as_of_date,
            as_of_date=requested_as_of_date,
            used_previous_trading_day=False,
            previous_trading_day_reason="",
        )
    if not allow_previous_trading_day:
        raise ValueError(f"as_of_date is not a trading day: {requested_as_of_date}")
    previous = [day for day in trading_days if day < requested_as_of_date]
    if not previous:
        raise ValueError(f"no previous trading day available before {requested_as_of_date}")
    resolved = previous[-1]
    return AsOfResolution(
        requested_as_of_date=requested_as_of_date,
        as_of_date=resolved,
        used_previous_trading_day=True,
        previous_trading_day_reason=f"{requested_as_of_date} is not a trading day; used previous trading day {resolved}",
    )


def selection_data_dir(paths: ProjectPaths, as_of_date: str):
    return paths.data_dir / "equity_selection" / "daily" / as_of_date


def selection_output_dir(paths: ProjectPaths, as_of_date: str):
    return paths.outputs_dir / "equity_selection" / "daily" / as_of_date

