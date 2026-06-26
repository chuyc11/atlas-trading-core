"""Audit A-share data coverage."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data.adjusted_price import ingest_a_share_adjusted_prices
from trading_core.equity_data.daily_basic import ingest_a_share_daily_basic
from trading_core.equity_data.daily_price import ingest_a_share_daily_prices
from trading_core.equity_data_quality.common import PROTECTED_BOUNDARY, RECOMMENDED_NEXT_VERSION, TARGET_VERSION, artifact_record, data_quality_dir, markdown_boundary, read_frame, read_json, sha256_file, write_report
from trading_core.equity_fundamental.basic_financials import ingest_a_share_basic_financials
from trading_core.equity_industry.classification import ingest_a_share_industry_classification
from trading_core.equity_universe.calendar import build_a_share_trading_calendar
from trading_core.equity_universe.master import build_a_share_equity_master
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_data_coverage(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    _ensure_foundation(paths)
    artifacts = _artifact_paths(paths)
    frames = {name: read_frame(path) for name, path in artifacts.items() if path.suffix == ".parquet"}
    master = frames.get("equity_master", pd.DataFrame())
    daily = frames.get("daily_price_panel", pd.DataFrame())
    adjusted = frames.get("adjusted_price_panel", pd.DataFrame())
    basic = frames.get("daily_basic_panel", pd.DataFrame())
    industry = frames.get("industry_classification", pd.DataFrame())
    financial = frames.get("basic_financials_panel", pd.DataFrame())
    calendar = frames.get("trading_calendar", pd.DataFrame())
    warnings = []
    source_manifest = read_json(paths.data_dir / "equity_data_quality" / "a_share_data_source_manifest.json")
    warnings.extend(source_manifest.get("warnings", []))
    if not adjusted.empty and set(adjusted.get("adjustment_type", [])) == {"raw"}:
        warnings.append("adjusted_price_panel uses raw fallback with adj_factor=1.0")
    if not industry.empty and set(industry.get("industry_standard", [])) == {"board_fallback"}:
        warnings.append("industry classification uses board-level fallback")
    financial_manifest = read_json(paths.data_dir / "equity_fundamental" / "basic_financials_manifest.json")
    if financial_manifest.get("field_coverage") and all(value == 0 for value in financial_manifest["field_coverage"].values()):
        warnings.append("basic financial numeric fields are nullable placeholders in v0.7.1")
    raw_total = source_manifest.get("raw_total")
    rows_available = int(source_manifest.get("rows_available") or 0)
    raw_coverage_ratio = source_manifest.get("raw_coverage_ratio")
    required_exchanges = {"SSE", "SZSE", "BSE"}
    exchange_set = set(master["exchange"].dropna().tolist()) if not master.empty and "exchange" in master else set()
    source_rows_cover_raw_total = True
    if raw_total:
        source_rows_cover_raw_total = rows_available >= int(int(raw_total) * 0.8)
    daily_symbols = set(daily["symbol"].dropna().tolist()) if not daily.empty and "symbol" in daily else set()
    master_symbols = set(master["symbol"].dropna().tolist()) if not master.empty and "symbol" in master else set()
    daily_missing_symbols = sorted(master_symbols - daily_symbols)
    if daily_missing_symbols:
        warnings.append(f"daily_price_panel missing {len(daily_missing_symbols)} master symbols")
    checks = {
        "equity_master_exists": artifacts["equity_master"].exists() and not master.empty,
        "equity_master_supports_required_exchanges": required_exchanges.issubset(exchange_set) if not master.empty else False,
        "trading_calendar_exists": artifacts["trading_calendar"].exists() and not calendar.empty,
        "daily_price_panel_exists": artifacts["daily_price_panel"].exists() and not daily.empty,
        "daily_price_supports_scan": int(daily["symbol"].nunique()) >= max(1, int(master["symbol"].nunique() * 0.8)) if not master.empty and not daily.empty else False,
        "source_rows_cover_raw_total": source_rows_cover_raw_total,
        "duplicate_daily_price_rows_zero": int(daily.duplicated(["date", "symbol"]).sum()) == 0 if not daily.empty else False,
        "price_sanity_passed": _price_sanity(daily),
        "volume_sanity_passed": _non_negative(daily, ["volume", "amount"]),
        "market_cap_sanity_passed": _non_negative(basic, ["total_mv", "circ_mv"]) if not basic.empty else True,
    }
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    coverage = {
        "equity_master_symbols": int(master["symbol"].nunique()) if not master.empty else 0,
        "daily_price_symbols": int(daily["symbol"].nunique()) if not daily.empty else 0,
        "adjusted_price_symbols": int(adjusted["symbol"].nunique()) if not adjusted.empty else 0,
        "daily_basic_symbols": int(basic["symbol"].nunique()) if not basic.empty else 0,
        "industry_symbols": int(industry["symbol"].nunique()) if not industry.empty else 0,
        "financial_symbols": int(financial["symbol"].nunique()) if not financial.empty else 0,
        "min_date": str(daily["date"].min()) if not daily.empty else "",
        "max_date": str(daily["date"].max()) if not daily.empty else "",
        "trading_days": int(calendar["date"].nunique()) if not calendar.empty else 0,
        "source_rows_available": rows_available,
        "source_raw_total": int(raw_total) if raw_total else None,
        "source_raw_coverage_ratio": raw_coverage_ratio,
        "required_exchanges": sorted(required_exchanges),
        "observed_exchanges": sorted(exchange_set),
        "daily_price_missing_symbols_count": len(daily_missing_symbols),
        "daily_price_missing_symbols_sample": daily_missing_symbols[:50],
    }
    payload: dict[str, Any] = {
        "audit_id": "A-SHARE-DATA-COVERAGE-AUDIT",
        "target_version": TARGET_VERSION,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "checks": checks,
        "coverage": coverage,
        "artifact_hashes": {name: sha256_file(path) for name, path in artifacts.items()},
        "artifacts": {name: artifact_record(path, paths.project_root) for name, path in artifacts.items()},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "boundary": dict(PROTECTED_BOUNDARY),
    }
    json_path = data_quality_dir(paths) / "a_share_data_coverage_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_DATA_COVERAGE_AUDIT.md"
    lines = [
        "# A-Share Data Coverage Audit",
        "",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {len(warnings)}",
        f"- coverage: {coverage}",
        f"- recommended_next_version: {RECOMMENDED_NEXT_VERSION}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return write_report(json_path, payload, report_path, "\n".join(lines))


def _ensure_foundation(paths: ProjectPaths) -> None:
    if not (paths.data_dir / "equity_universe" / "equity_master.parquet").exists():
        build_a_share_equity_master(paths=paths)
    if not (paths.data_dir / "equity_universe" / "trading_calendar.parquet").exists():
        build_a_share_trading_calendar(paths=paths)
    if not (paths.data_dir / "equity_market" / "daily_price_panel.parquet").exists():
        ingest_a_share_daily_prices(paths=paths)
    if not (paths.data_dir / "equity_market" / "adjusted_price_panel.parquet").exists():
        ingest_a_share_adjusted_prices(paths=paths)
    if not (paths.data_dir / "equity_market" / "daily_basic_panel.parquet").exists():
        ingest_a_share_daily_basic(paths=paths)
    if not (paths.data_dir / "equity_industry" / "industry_classification.parquet").exists():
        ingest_a_share_industry_classification(paths=paths)
    if not (paths.data_dir / "equity_fundamental" / "basic_financials_panel.parquet").exists():
        ingest_a_share_basic_financials(paths=paths)


def _artifact_paths(paths: ProjectPaths):
    return {
        "equity_master": paths.data_dir / "equity_universe" / "equity_master.parquet",
        "trading_calendar": paths.data_dir / "equity_universe" / "trading_calendar.parquet",
        "daily_price_panel": paths.data_dir / "equity_market" / "daily_price_panel.parquet",
        "adjusted_price_panel": paths.data_dir / "equity_market" / "adjusted_price_panel.parquet",
        "daily_basic_panel": paths.data_dir / "equity_market" / "daily_basic_panel.parquet",
        "industry_classification": paths.data_dir / "equity_industry" / "industry_classification.parquet",
        "basic_financials_panel": paths.data_dir / "equity_fundamental" / "basic_financials_panel.parquet",
        "source_manifest": paths.data_dir / "equity_data_quality" / "a_share_data_source_manifest.json",
    }


def _price_sanity(frame: pd.DataFrame) -> bool:
    if frame.empty:
        return False
    price_cols = ["open", "high", "low", "close"]
    return bool(((frame[price_cols] > 0).all(axis=1)).all() and (frame["high"] >= frame["low"]).all())


def _non_negative(frame: pd.DataFrame, columns: list[str]) -> bool:
    if frame.empty:
        return True
    return all(bool((frame[column].dropna() >= 0).all()) for column in columns if column in frame)
