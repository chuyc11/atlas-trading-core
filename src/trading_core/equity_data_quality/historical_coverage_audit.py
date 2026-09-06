"""Audit A-share historical panel coverage."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import HISTORICAL_BOUNDARY, HISTORICAL_DATA_SOURCE_UPGRADE_VERSION, HISTORICAL_TARGET_VERSION, RECOMMENDED_NEXT_VERSION, artifact_record, data_quality_dir, markdown_boundary, read_frame, read_json, sha256_file, write_report
from trading_core.equity_data_quality.history_manifest import history_dirs
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_historical_panel_coverage(
    *,
    paths: ProjectPaths | None = None,
    minimum_price_symbols: int = 3000,
    minimum_trading_days: int = 700,
    minimum_120d_symbols: int = 3000,
    minimum_250d_symbols: int = 2500,
    minimum_master_coverage_ratio: float = 0.50,
) -> dict[str, Any]:
    paths = default_paths(paths)
    dirs = history_dirs(paths)
    artifacts = {
        "daily_price_history_panel": dirs["market_history"] / "daily_price_history_panel.parquet",
        "adjusted_price_history_panel": dirs["market_history"] / "adjusted_price_history_panel.parquet",
        "daily_basic_history_panel": dirs["market_history"] / "daily_basic_history_panel.parquet",
        "basic_financials_history_panel": dirs["fundamental_history"] / "basic_financials_history_panel.parquet",
    }
    price = read_frame(artifacts["daily_price_history_panel"])
    adjusted = read_frame(artifacts["adjusted_price_history_panel"])
    basic = read_frame(artifacts["daily_basic_history_panel"])
    financial = read_frame(artifacts["basic_financials_history_panel"])
    master = read_frame(paths.data_dir / "equity_universe" / "equity_master.parquet")
    queue_payload = read_json(data_quality_dir(paths) / "a_share_historical_backfill_symbol_queue.json")
    price_counts = price.groupby("symbol")["date"].nunique() if not price.empty else pd.Series(dtype=int)
    financial_counts = financial.groupby("symbol")["report_date"].nunique() if not financial.empty else pd.Series(dtype=int)
    price_rows = len(price)
    adjusted_rows = len(adjusted)
    basic_rows = len(basic)
    price_symbols = int(price["symbol"].nunique()) if not price.empty else 0
    master_symbols = int(master["symbol"].nunique()) if not master.empty else price_symbols
    queue_symbols = int(queue_payload.get("eligible_price_backfill_symbols") or queue_payload.get("queue_total_symbols") or master_symbols)
    target_financial_quarters = max(1, master_symbols * 12)
    coverage: dict[str, Any] = {
        "price_history_min_date": str(price["date"].min()) if not price.empty else "",
        "price_history_max_date": str(price["date"].max()) if not price.empty else "",
        "price_history_trading_days": int(price["date"].nunique()) if not price.empty else 0,
        "price_history_symbols": price_symbols,
        "adjusted_price_symbols": int(adjusted["symbol"].nunique()) if not adjusted.empty else 0,
        "daily_basic_symbols": int(basic["symbol"].nunique()) if not basic.empty else 0,
        "financial_symbols": int(financial["symbol"].nunique()) if not financial.empty else 0,
        "symbols_with_20d_history": int((price_counts >= 20).sum()),
        "symbols_with_60d_history": int((price_counts >= 60).sum()),
        "symbols_with_120d_history": int((price_counts >= 120).sum()),
        "symbols_with_250d_history": int((price_counts >= 250).sum()),
        "symbols_with_3y_history": int((price_counts >= 700).sum()),
        "symbols_with_5y_history": int((price_counts >= 1100).sum()),
        "adjusted_price_coverage_ratio": round(adjusted_rows / price_rows, 6) if price_rows else 0.0,
        "daily_basic_history_coverage_ratio": round(basic_rows / price_rows, 6) if price_rows else 0.0,
        "financial_quarter_coverage_ratio": round(min(1.0, len(financial) / target_financial_quarters), 6) if target_financial_quarters else 0.0,
        "symbols_with_12_financial_quarters": int((financial_counts >= 12).sum()),
        "financial_quarter_target_symbol_count": master_symbols,
    }
    coverage_global = {
        "equity_master_symbols": master_symbols,
        "backfill_queue_symbols": queue_symbols,
        "price_history_symbols": price_symbols,
        "price_history_coverage_vs_equity_master": round(price_symbols / master_symbols, 6) if master_symbols else 0.0,
        "price_history_coverage_vs_queue": round(price_symbols / queue_symbols, 6) if queue_symbols else 0.0,
        "daily_basic_coverage_vs_equity_master": round(coverage["daily_basic_symbols"] / master_symbols, 6) if master_symbols else 0.0,
        "financial_coverage_vs_equity_master": round(coverage["financial_symbols"] / master_symbols, 6) if master_symbols else 0.0,
    }
    checks = {
        "daily_price_history_panel_exists": artifacts["daily_price_history_panel"].exists() and not price.empty,
        "price_history_symbols_minimum": coverage["price_history_symbols"] >= minimum_price_symbols,
        "price_history_trading_days_minimum": coverage["price_history_trading_days"] >= minimum_trading_days,
        "symbols_with_120d_history_minimum": coverage["symbols_with_120d_history"] >= minimum_120d_symbols,
        "symbols_with_250d_history_minimum": coverage["symbols_with_250d_history"] >= minimum_250d_symbols,
        "price_history_coverage_vs_equity_master_minimum": coverage_global["price_history_coverage_vs_equity_master"] >= minimum_master_coverage_ratio,
        "adjusted_price_coverage_recorded": coverage["adjusted_price_coverage_ratio"] >= 0.0,
        "daily_basic_history_coverage_recorded": coverage["daily_basic_history_coverage_ratio"] >= 0.0,
        "financial_quarter_coverage_recorded": coverage["financial_quarter_coverage_ratio"] >= 0.0,
        "duplicate_daily_price_rows_zero": int(price.duplicated(["date", "symbol"]).sum()) == 0 if not price.empty else False,
        "price_sanity_passed": _price_sanity(price),
        "volume_sanity_passed": _non_negative(price, ["volume", "amount"]),
    }
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    warnings = _warnings(coverage)
    providers = _providers(paths)
    recommended_next_version = RECOMMENDED_NEXT_VERSION if not blocking else HISTORICAL_DATA_SOURCE_UPGRADE_VERSION
    payload: dict[str, Any] = {
        "audit_id": "A-SHARE-HISTORICAL-PANEL-COVERAGE-AUDIT",
        "target_version": HISTORICAL_TARGET_VERSION,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "checks": checks,
        "coverage": coverage,
        "coverage_global": coverage_global,
        "providers": providers,
        "provider_failure_summary": _provider_failure_summary(providers.get("failed", [])),
        "artifact_hashes": {name: sha256_file(path) for name, path in artifacts.items()},
        "artifacts": {name: artifact_record(path, paths.project_root) for name, path in artifacts.items()},
        "boundary": dict(HISTORICAL_BOUNDARY),
        "recommended_next_version": recommended_next_version,
    }
    json_path = data_quality_dir(paths) / "a_share_historical_panel_coverage_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_HISTORICAL_PANEL_COVERAGE_AUDIT.md"
    lines = [
        "# A-Share Historical Panel Coverage Audit",
        "",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {len(warnings)}",
        f"- coverage: {coverage}",
        f"- coverage_global: {coverage_global}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "- Live trading ready: false.",
        "",
    ]
    return write_report(json_path, payload, report_path, "\n".join(lines))


def _providers(paths: ProjectPaths) -> dict[str, Any]:
    dirs = history_dirs(paths)
    manifests = [
        read_json(dirs["market_history"] / "daily_price_history_manifest.json"),
        read_json(dirs["fundamental_history"] / "basic_financials_history_manifest.json"),
    ]
    attempted = []
    succeeded = []
    failed = []
    for manifest in manifests:
        attempted.extend(manifest.get("providers_attempted", []))
        succeeded.extend(manifest.get("providers_succeeded", []))
        failed.extend(manifest.get("providers_failed", []))
    return {"attempted": sorted(set(attempted)), "succeeded": sorted(set(succeeded)), "failed": failed}


def _provider_failure_summary(failed: list[Any]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for item in failed:
        provider = "unknown"
        reason = str(item)
        if isinstance(item, dict):
            provider = str(item.get("provider") or item.get("report_date") or "unknown")
            reason = str(item.get("reason") or item)
        key = provider if provider != "unknown" else reason.split(":", 1)[0][:80]
        summary[key] = summary.get(key, 0) + 1
    return summary


def _warnings(coverage: dict[str, Any]) -> list[str]:
    warnings = []
    if coverage["symbols_with_5y_history"] < coverage["price_history_symbols"]:
        warnings.append("some symbols do not have 5-year price history")
    if coverage["adjusted_price_coverage_ratio"] > 0:
        warnings.append("adjusted price history may use raw fallback when true adjustment data is unavailable")
    if coverage["financial_quarter_coverage_ratio"] < 1:
        warnings.append("financial quarter history coverage is partial")
    return warnings


def _price_sanity(frame: pd.DataFrame) -> bool:
    if frame.empty:
        return False
    price_cols = ["open", "high", "low", "close"]
    return bool(((frame[price_cols] >= 0).all(axis=1)).all() and (frame["high"] >= frame["low"]).all())


def _non_negative(frame: pd.DataFrame, columns: list[str]) -> bool:
    if frame.empty:
        return False
    return all(bool((frame[column].dropna() >= 0).all()) for column in columns if column in frame)
