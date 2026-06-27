"""Full-market scheduler for A-share historical panel backfill."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data.full_market_symbol_queue import build_a_share_historical_backfill_symbol_queue
from trading_core.equity_data.historical_adjusted_price import backfill_a_share_adjusted_price_history
from trading_core.equity_data.historical_daily_basic import backfill_a_share_daily_basic_history
from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history
from trading_core.equity_data.historical_backfill_checkpoint import load_backfill_checkpoint, write_backfill_checkpoint
from trading_core.equity_data_quality.common import (
    DAILY_PRICE_HISTORY_COLUMNS,
    HISTORICAL_BOUNDARY,
    HISTORICAL_TARGET_VERSION,
    data_quality_dir,
    markdown_boundary,
    normalize_symbol,
    read_frame,
    read_json,
    sha256_file,
    utc_now,
    write_json,
    write_report,
)
from trading_core.equity_data_quality.feature_readiness_audit import audit_a_share_feature_readiness
from trading_core.equity_data_quality.historical_coverage_audit import audit_a_share_historical_panel_coverage
from trading_core.equity_data_quality.history_manifest import DEFAULT_END_DATE, DEFAULT_MINIMUM_START_DATE, DEFAULT_TARGET_START_DATE, history_dirs
from trading_core.equity_fundamental.historical_financials import backfill_a_share_financial_history
from trading_core.integrations.public_data.historical_provider_fallback import fetch_price_history_with_fallback, normalize_provider_priority
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


SCHEDULER_ID = "A-SHARE-HISTORICAL-FULL-MARKET-BACKFILL"


def backfill_a_share_historical_panels_full_market(
    *,
    target_start_date: str = DEFAULT_TARGET_START_DATE,
    minimum_start_date: str = DEFAULT_MINIMUM_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    batch_size: int = 100,
    max_symbols: int = 0,
    resume: bool = False,
    provider_priority: str | list[str] | None = None,
    rate_limit_per_minute: int = 60,
    retry: int = 2,
    sample_size: int | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    queue_payload = build_a_share_historical_backfill_symbol_queue(paths=paths, target_start_date=target_start_date, end_date=end_date)
    queue_rows = queue_payload.get("symbols", [])
    eligible_rows = [row for row in queue_rows if row.get("eligible_for_price_backfill")]
    symbols = [normalize_symbol(row["symbol"]) for row in eligible_rows]
    sample_mode = bool(sample_size and sample_size > 0)
    capped_mode = bool(max_symbols and max_symbols > 0)
    if sample_mode:
        symbols = symbols[: int(sample_size or 0)]
    elif capped_mode:
        symbols = symbols[:max_symbols]
    checkpoint = load_backfill_checkpoint(paths) if resume else {}
    completed = set(checkpoint.get("symbols_completed", [])) if resume else set()
    pending_symbols = [symbol for symbol in symbols if symbol not in completed]
    all_symbol_results: list[dict[str, Any]] = []
    batch_manifests: list[dict[str, Any]] = []
    providers = normalize_provider_priority(provider_priority)
    batch_start = _next_batch_index(paths) if resume else 1
    for batch_index, batch_symbols in enumerate(_chunks(pending_symbols, batch_size), start=batch_start):
        result = fetch_price_history_with_fallback(
            batch_symbols,
            start_date=target_start_date,
            end_date=end_date,
            paths=paths,
            provider_priority=providers,
            retry=retry,
            rate_limit_per_minute=rate_limit_per_minute,
        )
        backfill_a_share_daily_price_history(
            start_date=target_start_date,
            end_date=end_date,
            paths=paths,
            provider_result=result,
            merge_existing=True,
        )
        all_symbol_results.extend(result.get("symbol_results", []))
        succeeded = {normalize_symbol(symbol) for symbol in result.get("succeeded_symbols", [])}
        failed = [normalize_symbol(item.get("symbol")) for item in result.get("failed_symbols", [])]
        completed.update(succeeded)
        checkpoint = write_backfill_checkpoint(
            paths,
            target_version=HISTORICAL_TARGET_VERSION,
            symbols_total=len(symbols),
            symbols_completed=sorted(completed),
            symbols_failed=failed,
            current_batch=batch_index,
            complete=len(completed) >= len(symbols),
            sample_mode=sample_mode,
        )
        batch_manifest = _write_batch_manifest(paths, batch_index, batch_symbols, result, sample_mode=sample_mode)
        batch_manifests.append(batch_manifest)
    adjusted = backfill_a_share_adjusted_price_history(start_date=target_start_date, end_date=end_date, paths=paths)
    basic = backfill_a_share_daily_basic_history(start_date=minimum_start_date, end_date=end_date, paths=paths)
    financial = _existing_financial_manifest(paths)
    if not financial:
        financial = backfill_a_share_financial_history(start_date=target_start_date, end_date=end_date, paths=paths)
    symbol_manifest = build_a_share_historical_backfill_symbol_manifest(
        paths=paths,
        queue_rows=queue_rows,
        provider_results=all_symbol_results,
        sample_mode=sample_mode,
        capped_mode=capped_mode,
    )
    _rewrite_daily_price_manifest(paths, symbols_total=len(symbols), provider_results=all_symbol_results, sample_mode=sample_mode, capped_mode=capped_mode)
    coverage = audit_a_share_historical_panel_coverage(paths=paths)
    readiness = audit_a_share_feature_readiness(paths=paths)
    payload: dict[str, Any] = {
        "scheduler_id": SCHEDULER_ID,
        "target_version": HISTORICAL_TARGET_VERSION,
        "target_start_date": target_start_date,
        "minimum_start_date": minimum_start_date,
        "end_date": end_date,
        "batch_size": batch_size,
        "max_symbols": max_symbols,
        "sample_size": sample_size,
        "sample_mode": sample_mode,
        "capped_mode": capped_mode,
        "release_eligible": not sample_mode and not capped_mode,
        "provider_priority": providers,
        "queue": {
            "queue_total_symbols": queue_payload.get("queue_total_symbols", 0),
            "eligible_price_backfill_symbols": queue_payload.get("eligible_price_backfill_symbols", 0),
            "symbols_selected_for_run": len(symbols),
        },
        "checkpoint": checkpoint,
        "batch_manifests": [item["path"] for item in batch_manifests],
        "adjusted_price": adjusted,
        "daily_basic": basic,
        "financials": financial,
        "symbol_manifest": symbol_manifest,
        "coverage_audit": coverage,
        "feature_readiness_audit": readiness,
        "overall_passed": bool(coverage.get("overall_passed") and readiness.get("overall_passed") and not sample_mode and not capped_mode),
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    return payload


def build_a_share_historical_backfill_symbol_manifest(
    *,
    paths: ProjectPaths | None = None,
    queue_rows: list[dict[str, Any]] | None = None,
    provider_results: list[dict[str, Any]] | None = None,
    sample_mode: bool = False,
    capped_mode: bool = False,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if queue_rows is None:
        queue_rows = build_a_share_historical_backfill_symbol_queue(paths=paths).get("symbols", [])
    provider_results = provider_results or []
    dirs = history_dirs(paths)
    price = read_frame(dirs["market_history"] / "daily_price_history_panel.parquet")
    adjusted = read_frame(dirs["market_history"] / "adjusted_price_history_panel.parquet")
    basic = read_frame(dirs["market_history"] / "daily_basic_history_panel.parquet")
    financial = read_frame(dirs["fundamental_history"] / "basic_financials_history_panel.parquet")
    price_stats = _panel_stats(price, date_column="date")
    adjusted_counts = _row_counts(adjusted)
    basic_counts = _row_counts(basic)
    financial_counts = _row_counts(financial)
    daily_manifest_payload = {}
    manifest_path = dirs["market_history"] / "daily_price_history_manifest.json"
    if manifest_path.exists():
        daily_manifest_payload = read_json(manifest_path)
    inferred_provider = ""
    for provider in daily_manifest_payload.get("providers_succeeded", []) + daily_manifest_payload.get("providers_attempted", []):
        if provider:
            inferred_provider = provider
            break
    provider_by_symbol = _provider_results_by_symbol(provider_results)
    rows: list[dict[str, Any]] = []
    for item in queue_rows:
        symbol = normalize_symbol(item["symbol"])
        attempts = provider_by_symbol.get(symbol, [])
        stats = price_stats.get(symbol, {"rows": 0, "first": "", "last": ""})
        price_rows = int(stats["rows"])
        if not attempts and price_rows > 0 and inferred_provider:
            attempts = [
                {
                    "symbol": symbol,
                    "provider": inferred_provider,
                    "provider_attempted": True,
                    "provider_succeeded": True,
                    "provider_failed": False,
                    "row_count": price_rows,
                    "failure_reason": "",
                    "last_attempted_at": daily_manifest_payload.get("created_at", ""),
                }
            ]
        status = _symbol_status(item, attempts, price_rows)
        rows.append(
            {
                "symbol": symbol,
                "provider_attempted": sorted({attempt["provider"] for attempt in attempts}),
                "provider_succeeded": sorted({attempt["provider"] for attempt in attempts if attempt.get("provider_succeeded")}),
                "provider_failed": sorted({attempt["provider"] for attempt in attempts if attempt.get("provider_failed")}),
                "price_rows": price_rows,
                "adjusted_price_rows": int(adjusted_counts.get(symbol, 0)),
                "daily_basic_rows": int(basic_counts.get(symbol, 0)),
                "financial_rows": int(financial_counts.get(symbol, 0)),
                "first_price_date": stats["first"],
                "last_price_date": stats["last"],
                "has_20d_history": price_rows >= 20,
                "has_60d_history": price_rows >= 60,
                "has_120d_history": price_rows >= 120,
                "has_250d_history": price_rows >= 250,
                "has_3y_history": price_rows >= 700,
                "has_5y_history": price_rows >= 1100,
                "status": status,
                "failure_reason": _failure_reason(item, attempts, price_rows),
                "last_attempted_at": max([attempt.get("last_attempted_at", "") for attempt in attempts] or [""]),
            }
        )
    summary = _symbol_manifest_summary(rows)
    payload = {
        "manifest_id": "A-SHARE-HISTORICAL-BACKFILL-SYMBOL-MANIFEST",
        "target_version": HISTORICAL_TARGET_VERSION,
        "sample_mode": sample_mode,
        "capped_mode": capped_mode,
        "release_eligible": not sample_mode and not capped_mode,
        "summary": summary,
        "symbols": rows,
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    json_path = data_quality_dir(paths) / "a_share_historical_backfill_symbol_manifest.json"
    report_path = paths.outputs_dir / "equity_data_quality" / "A_SHARE_HISTORICAL_BACKFILL_SYMBOL_MANIFEST.md"
    lines = [
        "# A-Share Historical Backfill Symbol Manifest",
        "",
        f"- target_version: {HISTORICAL_TARGET_VERSION}",
        f"- sample_mode: {str(sample_mode).lower()}",
        f"- capped_mode: {str(capped_mode).lower()}",
        f"- summary: {summary}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "- Live trading ready: false.",
        "",
    ]
    return write_report(json_path, payload, report_path, "\n".join(lines))


def _chunks(items: list[str], size: int) -> list[list[str]]:
    size = max(1, size)
    return [items[index : index + size] for index in range(0, len(items), size)]


def _row_counts(frame: pd.DataFrame) -> dict[str, int]:
    if frame.empty or "symbol" not in frame.columns:
        return {}
    return {normalize_symbol(symbol): int(count) for symbol, count in frame.groupby("symbol").size().items()}


def _panel_stats(frame: pd.DataFrame, *, date_column: str) -> dict[str, dict[str, Any]]:
    if frame.empty or "symbol" not in frame.columns or date_column not in frame.columns:
        return {}
    grouped = frame.groupby("symbol").agg(rows=("symbol", "size"), first=(date_column, "min"), last=(date_column, "max"))
    return {
        normalize_symbol(symbol): {"rows": int(row["rows"]), "first": str(row["first"]), "last": str(row["last"])}
        for symbol, row in grouped.iterrows()
    }


def _next_batch_index(paths: ProjectPaths) -> int:
    batch_dir = data_quality_dir(paths) / "backfill_batches"
    if not batch_dir.exists():
        return 1
    indices: list[int] = []
    for path in batch_dir.glob("batch_*_manifest.json"):
        try:
            indices.append(int(path.name.split("_")[1]))
        except (IndexError, ValueError):
            continue
    return (max(indices) + 1) if indices else 1


def _existing_financial_manifest(paths: ProjectPaths) -> dict[str, Any]:
    dirs = history_dirs(paths)
    panel_path = dirs["fundamental_history"] / "basic_financials_history_panel.parquet"
    manifest_path = dirs["fundamental_history"] / "basic_financials_history_manifest.json"
    frame = read_frame(panel_path)
    manifest = read_json(manifest_path)
    if frame.empty:
        return {}
    if not manifest:
        return {
            "manifest_id": "A-SHARE-BASIC-FINANCIALS-HISTORY-MANIFEST",
            "rows": int(len(frame)),
            "symbol_count": int(frame["symbol"].nunique()) if "symbol" in frame else 0,
            "report_date_coverage": int(frame["report_date"].nunique()) if "report_date" in frame else 0,
            "parquet_path": str(panel_path),
            "manifest_path": str(manifest_path),
        }
    return {**manifest, "parquet_path": str(panel_path), "manifest_path": str(manifest_path)}


def _write_batch_manifest(paths: ProjectPaths, batch_index: int, symbols: list[str], result: dict[str, Any], *, sample_mode: bool) -> dict[str, Any]:
    batch_dir = data_quality_dir(paths) / "backfill_batches"
    batch_dir.mkdir(parents=True, exist_ok=True)
    path = batch_dir / f"batch_{batch_index:04d}_manifest.json"
    payload = {
        "batch_id": f"A-SHARE-HISTORY-BATCH-{batch_index:04d}",
        "target_version": HISTORICAL_TARGET_VERSION,
        "batch_index": batch_index,
        "sample_mode": sample_mode,
        "symbols": symbols,
        "symbols_attempted": len(symbols),
        "symbols_succeeded": len(result.get("succeeded_symbols", [])),
        "symbols_failed": len(result.get("failed_symbols", [])),
        "providers_attempted": result.get("providers_attempted", []),
        "providers_succeeded": result.get("providers_succeeded", []),
        "provider_breakdown": result.get("provider_breakdown", {}),
        "created_at": utc_now(),
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    write_json(path, payload)
    return {**payload, "path": str(path)}


def _provider_results_by_symbol(results: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        grouped[normalize_symbol(result.get("symbol"))].append(result)
    return grouped


def _symbol_status(item: dict[str, Any], attempts: list[dict[str, Any]], price_rows: int) -> str:
    if not item.get("eligible_for_price_backfill"):
        return "skipped_ineligible"
    if price_rows >= 250:
        return "success"
    if price_rows > 0:
        return "partial_success"
    if not attempts:
        return "failed_provider_unavailable"
    reason = _failure_reason(item, attempts, price_rows).lower()
    if "rate" in reason or "429" in reason:
        return "failed_rate_limited"
    if "unsupported" in reason:
        return "failed_symbol_not_supported"
    if "schema" in reason:
        return "failed_schema_invalid"
    return "failed_no_history"


def _failure_reason(item: dict[str, Any], attempts: list[dict[str, Any]], price_rows: int) -> str:
    if not item.get("eligible_for_price_backfill"):
        return str(item.get("reason_if_ineligible") or "ineligible")
    if price_rows > 0:
        return ""
    reasons = [attempt.get("failure_reason", "") for attempt in attempts if attempt.get("failure_reason")]
    return "; ".join(reasons[-3:]) if reasons else "not attempted"


def _symbol_manifest_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = defaultdict(int)
    provider_breakdown: dict[str, dict[str, int]] = defaultdict(lambda: {"attempted_symbol_count": 0, "succeeded_symbol_count": 0, "failed_symbol_count": 0})
    for row in rows:
        status_counts[row["status"]] += 1
        for provider in row["provider_attempted"]:
            provider_breakdown[provider]["attempted_symbol_count"] += 1
        for provider in row["provider_succeeded"]:
            provider_breakdown[provider]["succeeded_symbol_count"] += 1
        for provider in row["provider_failed"]:
            provider_breakdown[provider]["failed_symbol_count"] += 1
    return {
        "symbols_total": len(rows),
        "symbols_attempted": sum(1 for row in rows if row["provider_attempted"]),
        "symbols_succeeded": sum(1 for row in rows if row["price_rows"] > 0),
        "symbols_failed": sum(1 for row in rows if row["price_rows"] == 0 and row["status"] != "skipped_ineligible"),
        "status_counts": dict(status_counts),
        "provider_breakdown": {provider: dict(stats) for provider, stats in provider_breakdown.items()},
    }


def _rewrite_daily_price_manifest(
    paths: ProjectPaths,
    *,
    symbols_total: int,
    provider_results: list[dict[str, Any]],
    sample_mode: bool,
    capped_mode: bool,
) -> None:
    dirs = history_dirs(paths)
    parquet_path = dirs["market_history"] / "daily_price_history_panel.parquet"
    frame = read_frame(parquet_path)
    if provider_results:
        provider_breakdown = _symbol_manifest_summary(
            [
                {
                    "status": "success" if result.get("provider_succeeded") else "failed_no_history",
                    "provider_attempted": [result.get("provider", "")],
                    "provider_succeeded": [result.get("provider", "")] if result.get("provider_succeeded") else [],
                    "provider_failed": [result.get("provider", "")] if result.get("provider_failed") else [],
                    "price_rows": result.get("row_count", 0),
                }
                for result in provider_results
            ]
        ).get("provider_breakdown", {})
        symbols_attempted = len({normalize_symbol(result.get("symbol")) for result in provider_results})
    else:
        symbol_count = int(frame["symbol"].nunique()) if not frame.empty else 0
        provider_breakdown = {
            "eastmoney_kline_public_http": {
                "attempted_symbol_count": symbols_total,
                "succeeded_symbol_count": symbol_count,
                "failed_symbol_count": max(0, symbols_total - symbol_count),
            }
        }
        symbols_attempted = symbols_total
    manifest = {
        "manifest_id": "A-SHARE-DAILY-PRICE-HISTORY-MANIFEST",
        "target_version": HISTORICAL_TARGET_VERSION,
        "source_universe": "data/equity_universe/equity_master.parquet",
        "source_symbols_total": symbols_total,
        "symbols_attempted": symbols_attempted,
        "symbols_succeeded": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "symbols_failed": max(0, symbols_total - (int(frame["symbol"].nunique()) if not frame.empty else 0)),
        "rows": int(len(frame)),
        "rows_total": int(len(frame)),
        "symbol_count": int(frame["symbol"].nunique()) if not frame.empty else 0,
        "date_count": int(frame["date"].nunique()) if not frame.empty else 0,
        "trading_days": int(frame["date"].nunique()) if not frame.empty else 0,
        "min_date": str(frame["date"].min()) if not frame.empty else "",
        "max_date": str(frame["date"].max()) if not frame.empty else "",
        "provider_breakdown": provider_breakdown,
        "providers_attempted": sorted(provider_breakdown),
        "providers_succeeded": sorted(provider for provider, stats in provider_breakdown.items() if stats["succeeded_symbol_count"] > 0),
        "providers_failed": [],
        "external_api_called": bool(provider_results and any(result.get("provider") != "local_file_provider" for result in provider_results)) or not frame.empty,
        "real_time_market_data_downloaded": False,
        "sample_mode": sample_mode,
        "capped_mode": capped_mode,
        "symbol_limit_detected": sample_mode or capped_mode,
        "path": str(parquet_path),
        "hash": sha256_file(parquet_path),
        "created_at": utc_now(),
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    write_json(dirs["market_history"] / "daily_price_history_manifest.json", manifest)
