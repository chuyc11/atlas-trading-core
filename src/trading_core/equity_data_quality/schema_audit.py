"""Audit A-share data schemas."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import (
    ADJUSTED_PRICE_COLUMNS,
    DAILY_BASIC_COLUMNS,
    DAILY_PRICE_COLUMNS,
    EQUITY_MASTER_COLUMNS,
    FINANCIAL_COLUMNS,
    INDUSTRY_COLUMNS,
    PROTECTED_BOUNDARY,
    TARGET_VERSION,
    TRADING_CALENDAR_COLUMNS,
    data_quality_dir,
    markdown_boundary,
    read_frame,
    write_report,
)
from trading_core.equity_data_quality.coverage_audit import audit_a_share_data_coverage
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


SYMBOL_RE = re.compile(r"^\d{6}\.(SH|SZ|BJ)$")


def audit_a_share_data_schema(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    if not (paths.data_dir / "equity_market" / "daily_price_panel.parquet").exists():
        audit_a_share_data_coverage(paths=paths)
    specs = {
        "equity_master": (paths.data_dir / "equity_universe" / "equity_master.parquet", EQUITY_MASTER_COLUMNS, ["symbol"]),
        "trading_calendar": (paths.data_dir / "equity_universe" / "trading_calendar.parquet", TRADING_CALENDAR_COLUMNS, ["date", "exchange"]),
        "daily_price_panel": (paths.data_dir / "equity_market" / "daily_price_panel.parquet", DAILY_PRICE_COLUMNS, ["date", "symbol"]),
        "adjusted_price_panel": (paths.data_dir / "equity_market" / "adjusted_price_panel.parquet", ADJUSTED_PRICE_COLUMNS, ["date", "symbol", "adjustment_type"]),
        "daily_basic_panel": (paths.data_dir / "equity_market" / "daily_basic_panel.parquet", DAILY_BASIC_COLUMNS, ["date", "symbol"]),
        "industry_classification": (paths.data_dir / "equity_industry" / "industry_classification.parquet", INDUSTRY_COLUMNS, ["symbol"]),
        "basic_financials_panel": (paths.data_dir / "equity_fundamental" / "basic_financials_panel.parquet", FINANCIAL_COLUMNS, ["report_date", "symbol"]),
    }
    checks: dict[str, Any] = {}
    blocking: list[str] = []
    for name, (path, columns, primary_key) in specs.items():
        frame = read_frame(path)
        table_checks = _table_checks(frame, columns, primary_key)
        checks[name] = table_checks
        for check_name, passed in table_checks.items():
            if passed is False:
                blocking.append(f"{name}.{check_name}=false")
    payload: dict[str, Any] = {
        "audit_id": "A-SHARE-DATA-SCHEMA-AUDIT",
        "target_version": TARGET_VERSION,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "checks": checks,
        "boundary": dict(PROTECTED_BOUNDARY),
    }
    json_path = data_quality_dir(paths) / "a_share_data_schema_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_DATA_SCHEMA_AUDIT.md"
    lines = [
        "# A-Share Data Schema Audit",
        "",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {blocking}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return write_report(json_path, payload, report_path, "\n".join(lines))


def _table_checks(frame: pd.DataFrame, columns: list[str], primary_key: list[str]) -> dict[str, bool]:
    checks = {
        "exists_and_non_empty": not frame.empty,
        "required_columns_present": all(column in frame.columns for column in columns),
        "no_duplicate_primary_keys": not frame.duplicated(primary_key).any() if not frame.empty and all(column in frame.columns for column in primary_key) else False,
        "source_present": "source" in frame.columns and frame["source"].notna().all() if "source" in frame.columns and not frame.empty else False,
        "source_timestamp_present": "source_timestamp" in frame.columns and frame["source_timestamp"].notna().all() if "source_timestamp" in frame.columns and not frame.empty else False,
    }
    symbol_columns = [column for column in ["symbol"] if column in frame.columns]
    if symbol_columns and not frame.empty:
        checks["symbol_format_valid"] = bool(frame["symbol"].astype(str).map(lambda value: bool(SYMBOL_RE.match(value))).all())
    if "date" in frame.columns and not frame.empty:
        checks["date_format_valid"] = bool(frame["date"].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}$").all())
    if "report_date" in frame.columns and not frame.empty:
        checks["report_date_format_valid"] = bool(frame["report_date"].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}$").all())
    if {"open", "high", "low", "close"}.issubset(frame.columns) and not frame.empty:
        checks["price_sanity_valid"] = bool(((frame[["open", "high", "low", "close"]] > 0).all(axis=1)).all() and (frame["high"] >= frame["low"]).all())
    if {"volume", "amount"}.issubset(frame.columns) and not frame.empty:
        checks["volume_amount_non_negative"] = bool((frame["volume"].dropna() >= 0).all() and (frame["amount"].dropna() >= 0).all())
    for column in ["total_mv", "circ_mv"]:
        if column in frame.columns and not frame.empty:
            checks[f"{column}_non_negative"] = bool((frame[column].dropna() >= 0).all())
    return checks

