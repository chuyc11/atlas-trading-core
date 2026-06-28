"""Dataset contracts and local source helpers for A-share refresh."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_refresh.data_refresh_config import CRITICAL_DATASETS, DATASET_IDS
from trading_core.storage.file_paths import ProjectPaths


@dataclass(frozen=True)
class DatasetContract:
    dataset_id: str
    source_path_parts: tuple[str, ...]
    required_fields: tuple[str, ...]
    primary_key: tuple[str, ...]
    date_field: str | None
    symbol_field: str | None
    criticality: str
    aliases: dict[str, tuple[str, ...]]

    def source_path(self, paths: ProjectPaths) -> Path:
        return paths.data_dir.joinpath(*self.source_path_parts)


def dataset_contracts() -> dict[str, DatasetContract]:
    contracts = {
        "equity_master": DatasetContract(
            "equity_master",
            ("equity_universe", "equity_master.parquet"),
            ("symbol", "name", "exchange", "list_date", "status"),
            ("symbol",),
            None,
            "symbol",
            "important",
            {"status": ("status", "is_active")},
        ),
        "daily_price": DatasetContract(
            "daily_price",
            ("equity_market", "history", "daily_price_history_panel.parquet"),
            ("symbol", "trade_date", "open", "high", "low", "close", "volume", "amount"),
            ("symbol", "trade_date"),
            "trade_date",
            "symbol",
            "critical",
            {"trade_date": ("trade_date", "date")},
        ),
        "adjusted_price": DatasetContract(
            "adjusted_price",
            ("equity_market", "history", "adjusted_price_history_panel.parquet"),
            ("symbol", "trade_date", "adjusted_close"),
            ("symbol", "trade_date"),
            "trade_date",
            "symbol",
            "critical",
            {"trade_date": ("trade_date", "date"), "adjusted_close": ("adjusted_close", "adj_close", "close")},
        ),
        "daily_basic": DatasetContract(
            "daily_basic",
            ("equity_market", "history", "daily_basic_history_panel.parquet"),
            ("symbol", "trade_date", "turnover_rate", "total_mv", "circ_mv"),
            ("symbol", "trade_date"),
            "trade_date",
            "symbol",
            "important",
            {"trade_date": ("trade_date", "date")},
        ),
        "index_price": DatasetContract(
            "index_price",
            ("equity_benchmarks", "history", "index_price_history_panel.parquet"),
            ("index_code", "trade_date", "close"),
            ("index_code", "trade_date"),
            "trade_date",
            "index_code",
            "critical",
            {"index_code": ("index_code", "benchmark_id", "symbol_or_index_code"), "trade_date": ("trade_date", "date")},
        ),
        "industry_classification": DatasetContract(
            "industry_classification",
            ("equity_industry", "industry_classification.parquet"),
            ("symbol", "industry_level_1"),
            ("symbol",),
            None,
            "symbol",
            "important",
            {},
        ),
        "financial_indicators": DatasetContract(
            "financial_indicators",
            ("equity_fundamental", "history", "basic_financials_history_panel.parquet"),
            ("symbol", "report_date"),
            ("symbol", "report_date"),
            "report_date",
            "symbol",
            "important",
            {"report_date": ("report_date", "period")},
        ),
        "trading_calendar": DatasetContract(
            "trading_calendar",
            ("equity_universe", "trading_calendar.parquet"),
            ("trade_date", "is_open"),
            ("trade_date",),
            "trade_date",
            None,
            "critical",
            {"trade_date": ("trade_date", "date"), "is_open": ("is_open", "is_trading_day")},
        ),
    }
    return {key: contracts[key] for key in DATASET_IDS}


def contract_payload() -> dict[str, Any]:
    return {
        dataset_id: {
            "dataset_id": contract.dataset_id,
            "source_path": "/".join(contract.source_path_parts),
            "required_fields": list(contract.required_fields),
            "primary_key": list(contract.primary_key),
            "date_field": contract.date_field,
            "symbol_field": contract.symbol_field,
            "criticality": contract.criticality,
            "aliases": {key: list(value) for key, value in contract.aliases.items()},
            "critical": dataset_id in CRITICAL_DATASETS,
        }
        for dataset_id, contract in dataset_contracts().items()
    }


def load_dataset_frame(paths: ProjectPaths, contract: DatasetContract) -> pd.DataFrame:
    path = contract.source_path(paths)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def resolve_column(frame: pd.DataFrame, contract: DatasetContract, canonical: str) -> str | None:
    candidates = (canonical, *contract.aliases.get(canonical, ()))
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    return None


def canonical_series(frame: pd.DataFrame, contract: DatasetContract, canonical: str) -> pd.Series | None:
    column = resolve_column(frame, contract, canonical)
    if column is None:
        return None
    return frame[column]


def dataset_source_paths(paths: ProjectPaths) -> dict[str, Path]:
    return {dataset_id: contract.source_path(paths) for dataset_id, contract in dataset_contracts().items()}
