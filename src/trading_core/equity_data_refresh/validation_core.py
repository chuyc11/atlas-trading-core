"""Shared validation helpers for data refresh artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast, Any

import pandas as pd

from trading_core.equity_data_refresh.data_refresh_config import CRITICAL_DATASETS, REQUIRED_INDEX_IDS
from trading_core.equity_data_refresh.dataset_contracts import DatasetContract, canonical_series, dataset_contracts, load_dataset_frame, resolve_column
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


@dataclass
class DatasetSnapshot:
    contract: DatasetContract
    frame: pd.DataFrame
    source_path: str


def load_dataset_snapshots(paths: ProjectPaths) -> dict[str, DatasetSnapshot]:
    snapshots = {}
    for dataset_id, contract in dataset_contracts().items():
        snapshots[dataset_id] = DatasetSnapshot(
            contract=contract,
            frame=load_dataset_frame(paths, contract),
            source_path=relative(contract.source_path(paths), paths.project_root),
        )
    return snapshots


def dataset_summary(snapshot: DatasetSnapshot, as_of_date: str) -> dict[str, Any]:
    frame = snapshot.frame
    contract = snapshot.contract
    date_values = _date_values(frame, contract)
    symbol_values = _symbol_values(frame, contract)
    required_present, missing = required_field_status(frame, contract)
    return {
        "dataset_id": contract.dataset_id,
        "as_of_date": as_of_date,
        "source_provider": "local_file_provider",
        "source_path": snapshot.source_path,
        "record_count": int(len(frame)),
        "symbol_count": int(symbol_values.nunique()) if symbol_values is not None else 0,
        "date_count": int(date_values.nunique()) if date_values is not None else 0,
        "first_available_date": _min(date_values),
        "last_available_date": _max(date_values),
        "as_of_date_available": _contains(date_values, as_of_date),
        "required_fields_present": required_present,
        "missing_required_fields": missing,
        "duplicate_key_count": duplicate_key_count(frame, contract),
        "null_rate_summary": null_rate_summary(frame, contract),
    }


def required_field_status(frame: pd.DataFrame, contract: DatasetContract) -> tuple[bool, list[str]]:
    missing = [field for field in contract.required_fields if resolve_column(frame, contract, field) is None]
    return not missing, missing


def duplicate_key_count(frame: pd.DataFrame, contract: DatasetContract) -> int:
    if frame.empty:
        return 0
    if contract.dataset_id == "trading_calendar":
        return 0
    columns = [resolve_column(frame, contract, field) for field in contract.primary_key]
    if any(column is None for column in columns):
        return 0
    return int(frame.duplicated([str(column) for column in columns]).sum())


def null_rate_summary(frame: pd.DataFrame, contract: DatasetContract) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for field in contract.required_fields:
        column = resolve_column(frame, contract, field)
        result[field] = None if column is None or frame.empty else float(frame[column].isna().mean())
    return result


def validate_schema(snapshot: DatasetSnapshot, as_of_date: str) -> dict[str, Any]:
    frame = snapshot.frame
    contract = snapshot.contract
    summary = dataset_summary(snapshot, as_of_date)
    checks = {
        "required_columns_present": bool(summary["required_fields_present"]),
        "dates_parseable": _dates_parseable(frame, contract),
        "symbol_format_valid": _symbol_format_valid(frame, contract),
        "duplicate_primary_keys": summary["duplicate_key_count"],
        "non_negative_volume_amount": _non_negative(frame, ["volume", "amount"]),
        "ohlc_sanity": _ohlc_sanity(frame) if contract.dataset_id == "daily_price" else True,
        "close_positive": _positive(frame, "close") if contract.dataset_id in {"daily_price", "index_price"} else True,
        "adjusted_close_positive": _positive(frame, resolve_column(frame, contract, "adjusted_close")) if contract.dataset_id == "adjusted_price" else True,
        "market_cap_positive_where_present": _positive_where_present(frame, ["total_mv", "circ_mv"]) if contract.dataset_id == "daily_basic" else True,
    }
    blocking = []
    if contract.dataset_id in CRITICAL_DATASETS and not checks["required_columns_present"]:
        blocking.append("missing_required_fields")
    if contract.dataset_id in CRITICAL_DATASETS and checks["duplicate_primary_keys"]:
        blocking.append("duplicate_primary_keys")
    for name in ["dates_parseable", "symbol_format_valid", "non_negative_volume_amount", "ohlc_sanity", "close_positive", "adjusted_close_positive", "market_cap_positive_where_present"]:
        if checks[name] is False:
            blocking.append(name)
    warnings = []
    if not checks["required_columns_present"]:
        warnings.append("missing_noncritical_required_fields")
    if any(rate == 1.0 for rate in summary["null_rate_summary"].values() if rate is not None):
        warnings.append("required_field_all_null")
    if contract.dataset_id == "trading_calendar" and _raw_calendar_duplicate_count(frame, contract) > 0:
        warnings.append("exchange_level_calendar_collapsed_to_trade_date")
    return {
        **summary,
        "schema_status": "passed" if not blocking else "failed",
        "checks": checks,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }


def validate_freshness(snapshot: DatasetSnapshot, as_of_date: str, trading_dates: list[str]) -> dict[str, Any]:
    contract = snapshot.contract
    date_values = _date_values(snapshot.frame, contract)
    latest = _max(date_values)
    available = _contains(date_values, as_of_date)
    lag = _trading_lag(latest, as_of_date, trading_dates)
    blocking: list[str] = []
    stale_reason = None
    status = "fresh" if available else "missing"
    if contract.dataset_id in {"daily_price", "index_price", "trading_calendar"} and not available:
        status = "stale_blocking"
        stale_reason = "critical dataset does not include target as_of_date"
        blocking.append("as_of_date_missing")
    elif contract.dataset_id == "adjusted_price" and not available:
        status = "stale_warning"
        stale_reason = "adjusted price is lagged"
    elif contract.dataset_id in {"industry_classification", "financial_indicators", "equity_master"}:
        status = "lagged_allowed" if not available else "fresh"
    elif not available:
        status = "stale_warning"
        stale_reason = "noncritical dataset is lagged"
    return {
        "dataset_id": contract.dataset_id,
        "target_as_of_date": as_of_date,
        "latest_available_date": latest,
        "as_of_date_available": available,
        "freshness_lag_trading_days": lag,
        "freshness_status": status,
        "is_stale": status not in {"fresh", "lagged_allowed"},
        "stale_reason": stale_reason,
        "blocking_reasons": blocking,
        "warnings": [stale_reason] if stale_reason and not blocking else [],
    }


def coverage_metrics(snapshots: dict[str, DatasetSnapshot], as_of_date: str) -> dict[str, Any]:
    equity_symbols = _symbols(snapshots["equity_master"])
    tradable_symbols = _tradable_symbols(snapshots, as_of_date)
    datasets = {}
    thresholds = {
        "daily_price": 0.90,
        "adjusted_price": 0.90,
        "daily_basic": 0.85,
        "industry_classification": 0.80,
    }
    for dataset_id, snapshot in snapshots.items():
        symbols = _symbols(snapshot)
        coverage_equity = _ratio(len(symbols & equity_symbols), len(equity_symbols))
        coverage_tradable = _ratio(len(symbols & tradable_symbols), len(tradable_symbols)) if tradable_symbols else None
        threshold = thresholds.get(dataset_id)
        threshold_passed = True if threshold is None else coverage_equity >= threshold
        if dataset_id == "index_price":
            ids = _index_ids(snapshot)
            threshold_passed = set(REQUIRED_INDEX_IDS).issubset(ids)
        if dataset_id == "trading_calendar":
            date_values = _date_values(snapshot.frame, snapshot.contract)
            dates = set(date_values.astype(str).str[:10]) if date_values is not None else set()
            threshold_passed = as_of_date in dates
        datasets[dataset_id] = {
            "symbol_count": len(symbols),
            "coverage_vs_equity_master": coverage_equity,
            "coverage_vs_tradable_universe": coverage_tradable,
            "field_coverage": _field_coverage(snapshot),
            "null_rate_summary": null_rate_summary(snapshot.frame, snapshot.contract),
            "threshold": threshold,
            "threshold_passed": threshold_passed,
            "critical_missing_count": 0 if threshold_passed else 1 if dataset_id in CRITICAL_DATASETS else 0,
        }
    return {
        "equity_master_symbols": len(equity_symbols),
        "daily_price_symbols": datasets["daily_price"]["symbol_count"],
        "adjusted_price_symbols": datasets["adjusted_price"]["symbol_count"],
        "daily_basic_symbols": datasets["daily_basic"]["symbol_count"],
        "index_price_ids": sorted(_index_ids(snapshots["index_price"])),
        "industry_symbols": datasets["industry_classification"]["symbol_count"],
        "financial_symbols": datasets["financial_indicators"]["symbol_count"],
        "tradable_universe_symbols_if_available": len(tradable_symbols),
        "coverage_vs_equity_master": {key: value["coverage_vs_equity_master"] for key, value in datasets.items()},
        "coverage_vs_tradable_universe": {key: value["coverage_vs_tradable_universe"] for key, value in datasets.items()},
        "field_coverage": {key: value["field_coverage"] for key, value in datasets.items()},
        "null_rate_summary": {key: value["null_rate_summary"] for key, value in datasets.items()},
        "critical_missing_count": sum(int(cast(Any, value["critical_missing_count"]) or 0) for value in datasets.values()),
        "datasets": datasets,
    }


def _date_values(frame: pd.DataFrame, contract: DatasetContract) -> pd.Series | None:
    if contract.date_field is None:
        return None
    series = canonical_series(frame, contract, contract.date_field)
    if series is None:
        return None
    return series.astype(str).str[:10]


def _symbol_values(frame: pd.DataFrame, contract: DatasetContract) -> pd.Series | None:
    if contract.symbol_field is None:
        return None
    series = canonical_series(frame, contract, contract.symbol_field)
    return series.astype(str) if series is not None else None


def _symbols(snapshot: DatasetSnapshot) -> set[str]:
    values = _symbol_values(snapshot.frame, snapshot.contract)
    return set(values.dropna()) if values is not None else set()


def _index_ids(snapshot: DatasetSnapshot) -> set[str]:
    series = canonical_series(snapshot.frame, snapshot.contract, "index_code")
    return set(series.dropna().astype(str)) if series is not None else set()


def _tradable_symbols(snapshots: dict[str, DatasetSnapshot], as_of_date: str) -> set[str]:
    return _symbols(snapshots["daily_price"]) if snapshots.get("daily_price") else set()


def _field_coverage(snapshot: DatasetSnapshot) -> dict[str, float | None]:
    frame = snapshot.frame
    result = {}
    for field in snapshot.contract.required_fields:
        column = resolve_column(frame, snapshot.contract, field)
        result[field] = None if column is None or frame.empty else float(frame[column].notna().mean())
    return result


def _min(series: pd.Series | None) -> str:
    return "" if series is None or series.empty else str(series.min())[:10]


def _max(series: pd.Series | None) -> str:
    return "" if series is None or series.empty else str(series.max())[:10]


def _contains(series: pd.Series | None, value: str) -> bool:
    return False if series is None else value in set(series.astype(str).str[:10])


def _dates_parseable(frame: pd.DataFrame, contract: DatasetContract) -> bool:
    series = _date_values(frame, contract)
    if series is None:
        return True
    return bool(pd.to_datetime(series, errors="coerce").notna().all())


def _symbol_format_valid(frame: pd.DataFrame, contract: DatasetContract) -> bool:
    if contract.dataset_id == "index_price":
        return True
    series = _symbol_values(frame, contract)
    if series is None:
        return True
    return bool(series.str.match(r"^[0-9]{6}\.(SH|SZ|BJ)$").fillna(False).all())


def _raw_calendar_duplicate_count(frame: pd.DataFrame, contract: DatasetContract) -> int:
    column = resolve_column(frame, contract, "trade_date")
    if column is None or frame.empty:
        return 0
    return int(frame.duplicated([column]).sum())


def _non_negative(frame: pd.DataFrame, columns: list[str]) -> bool:
    present = [column for column in columns if column in frame.columns]
    return True if not present else bool((frame[present].fillna(0) >= 0).all().all())


def _positive(frame: pd.DataFrame, column: str | None) -> bool:
    if column is None or column not in frame.columns:
        return True
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    return True if values.empty else bool((values > 0).all())


def _positive_where_present(frame: pd.DataFrame, columns: list[str]) -> bool:
    for column in columns:
        if column in frame.columns:
            values = pd.to_numeric(frame[column], errors="coerce").dropna()
            if not values.empty and not bool((values > 0).all()):
                return False
    return True


def _ohlc_sanity(frame: pd.DataFrame) -> bool:
    columns = ["open", "high", "low", "close"]
    if any(column not in frame.columns for column in columns):
        return True
    numeric = frame[columns].apply(pd.to_numeric, errors="coerce")
    return bool(((numeric["low"] <= numeric[["open", "close", "high"]].min(axis=1)) & (numeric["high"] >= numeric[["open", "close", "low"]].max(axis=1))).fillna(True).all())


def _trading_lag(latest: str, target: str, trading_dates: list[str]) -> int | None:
    if not latest or not target or latest == target:
        return 0 if latest == target else None
    ordered = [day for day in trading_dates if latest < day <= target]
    return len(ordered)


def _ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else float(numerator) / float(denominator)
