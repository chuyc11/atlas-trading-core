"""v0.9.3 public A-share data freshness refresh."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any
from collections.abc import Callable

import pandas as pd

from trading_core.equity_data.adjusted_price import ingest_a_share_adjusted_prices
from trading_core.equity_data.daily_basic import ingest_a_share_daily_basic
from trading_core.equity_data.daily_price import ingest_a_share_daily_prices
from trading_core.equity_data_quality.common import json_safe, snapshot_cache_path, utc_now, write_json
from trading_core.equity_universe.calendar import build_a_share_trading_calendar
from trading_core.equity_universe.master import build_a_share_equity_master
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v0.9.3-a-share-data-freshness-refresh"
SOURCE_VERSION = "v0.9.2-a-share-owner-daily-runbook-cli-entry-and-staleness-awareness"
RECOMMENDED_NEXT_VERSION = "v0.9.4-a-share-research-pipeline-rerun-from-refreshed-data"
DEFAULT_TARGET_AS_OF_DATE = "2026-07-01"
PREVIOUS_SOURCE_DATA_DATE = "2026-06-26"
MINIMUM_REQUIRED_COVERAGE_RATIO = 0.95
REFRESH_SCOPE = ["trading_calendar", "equity_master", "a_share_universe", "daily_price", "daily_volume", "adjustment_factors"]
EXCLUDED_SCOPE = [
    "research_pipeline_rerun",
    "build_from_existing_data",
    "candidate_generation",
    "scoring",
    "virtual_portfolio",
    "owner_readiness_gate",
    "broker",
    "orders",
    "signals",
]

ProviderFetcher = Callable[[], dict[str, Any]]


def refresh_a_share_data_freshness(
    *,
    target_as_of_date: str = DEFAULT_TARGET_AS_OF_DATE,
    dry_run: bool = False,
    paths: ProjectPaths | None = None,
    provider_fetcher: ProviderFetcher | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    provider_fetcher = provider_fetcher or _fetch_public_snapshot_fast
    started = time.perf_counter()
    started_at = utc_now()
    date_resolution = resolve_actual_data_date(paths=paths, target_as_of_date=target_as_of_date)
    actual_date = date_resolution["resolved_actual_data_date"]
    provider_snapshot = provider_fetcher()
    provider_status = _provider_status(provider_snapshot, target_as_of_date, actual_date)
    rows = provider_snapshot.get("rows", []) or []
    coverage = _coverage_summary(rows=rows, snapshot=provider_snapshot, target_as_of_date=target_as_of_date, actual_date=actual_date)
    blocking_reasons = []
    warnings = []
    if provider_status["overall_provider_status"] == "failed":
        blocking_reasons.append("public_provider_refresh_failed")
    if coverage["coverage_blocking_reasons"]:
        blocking_reasons.extend(coverage["coverage_blocking_reasons"])
    warnings.extend(provider_status["partial_provider_failures"])
    warnings.extend(coverage["coverage_warnings"])
    updated_data_paths: list[str] = []
    if not dry_run and not blocking_reasons:
        updated_data_paths = _write_refreshed_research_data(paths=paths, actual_date=actual_date, provider_snapshot=provider_snapshot)
    boundary = _boundary_check(actual_date=actual_date, data_refresh_executed=not dry_run and not blocking_reasons, blocking_reasons=blocking_reasons, warnings=warnings)
    completed_at = utc_now()
    result = _refresh_result(
        target_as_of_date=target_as_of_date,
        actual_date=actual_date,
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=round(time.perf_counter() - started, 3),
        dry_run=dry_run,
        provider_status=provider_status,
        coverage=coverage,
        blocking_reasons=blocking_reasons,
        warnings=warnings,
    )
    request = _refresh_request(target_as_of_date=target_as_of_date, actual_date=actual_date, reason=date_resolution["date_resolution_reason"], dry_run=dry_run)
    artifact_paths = _artifact_paths(paths, actual_date)
    manifest = _manifest(
        paths=paths,
        target_as_of_date=target_as_of_date,
        actual_date=actual_date,
        artifact_paths=artifact_paths,
        updated_data_paths=updated_data_paths,
        overall_passed=result["overall_passed"],
        blocking_reasons=blocking_reasons,
    )
    payloads = {
        "data_freshness_refresh_request": request,
        "data_freshness_provider_status": provider_status,
        "data_freshness_coverage_summary": coverage,
        "data_freshness_refresh_result": result,
        "data_freshness_boundary_check": boundary,
        "data_freshness_manifest": manifest,
    }
    for key, payload in payloads.items():
        write_json(artifact_paths[key], payload)
    artifact_paths["markdown_report"].parent.mkdir(parents=True, exist_ok=True)
    artifact_paths["markdown_report"].write_text(_markdown_report(result, provider_status, coverage, request), encoding="utf-8")
    return json_safe(
        {
            "builder_id": "A-SHARE-DATA-FRESHNESS-REFRESH",
            "target_version": TARGET_VERSION,
            "requested_target_as_of_date": target_as_of_date,
            "resolved_actual_data_date": actual_date,
            "date_resolution_reason": date_resolution["date_resolution_reason"],
            "dry_run": dry_run,
            "overall_passed": result["overall_passed"],
            "blocking_reasons": blocking_reasons,
            "warnings": warnings,
            "provider_status": provider_status["overall_provider_status"],
            "coverage_ratio": coverage["coverage_ratio"],
            "coverage_passed": coverage["coverage_passed"],
            "missing_symbol_count": coverage["missing_symbol_count"],
            "data_refresh_executed": result["data_refresh_executed"],
            "public_network_refresh_run": result["public_network_refresh_run"],
            "artifacts": {key: _rel(path, paths.project_root) for key, path in artifact_paths.items()},
            "refresh_result": result,
            "boundary": boundary,
            "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        }
    )


def resolve_actual_data_date(*, paths: ProjectPaths, target_as_of_date: str) -> dict[str, str]:
    target = date.fromisoformat(target_as_of_date)
    calendar_path = paths.data_dir / "equity_universe" / "trading_calendar.parquet"
    if calendar_path.exists():
        frame = pd.read_parquet(calendar_path)
        column = "date" if "date" in frame.columns else "trade_date" if "trade_date" in frame.columns else ""
        if column:
            dates = sorted({str(item)[:10] for item in frame[column].dropna().tolist() if str(item)[:10] <= target_as_of_date})
            if target_as_of_date in dates:
                return {"resolved_actual_data_date": target_as_of_date, "date_resolution_reason": "target_date_available_in_local_trading_calendar"}
            if dates:
                return {"resolved_actual_data_date": dates[-1], "date_resolution_reason": "resolved_to_nearest_prior_local_trading_calendar_date"}
    current = target
    while current.weekday() >= 5:
        current = current.fromordinal(current.toordinal() - 1)
    reason = "target_date_weekday_fallback" if current == target else "resolved_to_nearest_prior_weekday_fallback"
    return {"resolved_actual_data_date": current.isoformat(), "date_resolution_reason": reason}


def _write_refreshed_research_data(*, paths: ProjectPaths, actual_date: str, provider_snapshot: dict[str, Any]) -> list[str]:
    snapshot_payload = {
        "snapshot_id": "A-SHARE-PUBLIC-DATA-SNAPSHOT",
        "provider": provider_snapshot.get("provider", "qstock_reference_public_http"),
        "source_timestamp": utc_now(),
        "rows": provider_snapshot.get("rows", []),
        "attempts": [provider_snapshot],
        "external_api_called": True,
        "real_time_market_data_downloaded": False,
        "provider_reason": provider_snapshot.get("reason", ""),
        "raw_total": provider_snapshot.get("raw_total"),
        "raw_coverage_ratio": provider_snapshot.get("raw_coverage_ratio"),
        "blocking_reasons": [],
    }
    write_json(snapshot_cache_path(paths), snapshot_payload)
    outputs = [
        build_a_share_trading_calendar(paths=paths, end_date=actual_date),
        build_a_share_equity_master(paths=paths),
        ingest_a_share_daily_prices(paths=paths, as_of_date=actual_date),
        ingest_a_share_daily_basic(paths=paths, as_of_date=actual_date),
        ingest_a_share_adjusted_prices(paths=paths),
    ]
    updated: list[str] = [_rel(snapshot_cache_path(paths), paths.project_root)]
    for output in outputs:
        for key in ("parquet_path", "json_path", "manifest_path", "report_path"):
            if output.get(key):
                updated.append(_rel(Path(output[key]), paths.project_root))
    return sorted(set(updated))


def _fetch_public_snapshot_fast(timeout: int = 4) -> dict[str, Any]:
    urls = ["https://push2.eastmoney.com/api/qt/clist/get", "https://push2delay.eastmoney.com/api/qt/clist/get"]
    segments = [("SSE", "m:1+t:2,m:1+t:23"), ("SZSE", "m:0+t:6,m:0+t:80"), ("BSE", "m:0+t:81+s:2048")]
    rows: list[dict[str, Any]] = []
    raw_total = 0
    reasons: list[str] = []
    for segment, fs in segments:
        segment_rows: list[dict[str, Any]] = []
        segment_total = 0
        last_error = ""
        first_rows, segment_total, last_error = _fetch_eastmoney_page(urls=urls, fs=fs, segment=segment, page=1, timeout=timeout)
        segment_rows.extend(first_rows)
        if segment_total and first_rows:
            page_count = (segment_total + 99) // 100
            failed_pages: list[int] = []
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = {
                    executor.submit(_fetch_eastmoney_page, urls=urls, fs=fs, segment=segment, page=page, timeout=timeout): page
                    for page in range(2, page_count + 1)
                }
                for future in as_completed(futures):
                    page = futures[future]
                    page_rows, _, page_error = future.result()
                    if page_rows:
                        segment_rows.extend(page_rows)
                    elif page_error:
                        last_error = page_error
                        failed_pages.append(page)
            for _attempt in range(2):
                if not failed_pages:
                    break
                retry_pages = failed_pages
                failed_pages = []
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = {
                        executor.submit(_fetch_eastmoney_page, urls=urls, fs=fs, segment=segment, page=page, timeout=timeout + 2): page
                        for page in retry_pages
                    }
                    for future in as_completed(futures):
                        page = futures[future]
                        page_rows, _, page_error = future.result()
                        if page_rows:
                            segment_rows.extend(page_rows)
                        else:
                            last_error = page_error
                            failed_pages.append(page)
        rows.extend(segment_rows)
        raw_total += segment_total
        if not segment_rows:
            reasons.append(f"{segment}_fetch_failed:{last_error or 'empty response'}")
        elif segment_total and len(segment_rows) < segment_total:
            reasons.append(f"{segment}_partial_fetch_{len(segment_rows)}_of_{segment_total}")
    rows = _dedupe_rows(rows)
    if not rows:
        return {
            "provider": "qstock_reference_public_http_fast",
            "succeeded": False,
            "rows": [],
            "external_api_called": True,
            "real_time_market_data_downloaded": False,
            "reason": "; ".join(reasons) or "empty response",
            "raw_total": raw_total,
        }
    return {
        "provider": "qstock_reference_public_http_fast",
        "succeeded": True,
        "rows": rows,
        "external_api_called": True,
        "real_time_market_data_downloaded": False,
        "reason": "; ".join(reasons),
        "raw_total": raw_total or len(rows),
        "raw_coverage_ratio": round(len(rows) / raw_total, 6) if raw_total else 1.0,
    }


def _dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for row in rows:
        key = f"{row.get('_segment', '')}:{row.get('f12', '')}"
        if not row.get("f12") or key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _fetch_eastmoney_page(*, urls: list[str], fs: str, segment: str, page: int, timeout: int) -> tuple[list[dict[str, Any]], int, str]:
    last_error = ""
    for attempt in range(3):
        for url in urls:
            query = urllib.parse.urlencode(
                {
                    "pn": str(page),
                    "pz": "100",
                    "po": "1",
                    "np": "1",
                    "fltt": "2",
                    "invt": "2",
                    "fid": "f3",
                    "fs": fs,
                    "fields": "f12,f13,f14,f2,f3,f4,f5,f6,f8,f9,f15,f16,f17,f18,f20,f21,f23,f26",
                }
            )
            request = urllib.request.Request(
                f"{url}?{query}",
                headers={"User-Agent": "Mozilla/5.0 trading-core data-freshness/0.9.3", "Referer": "https://quote.eastmoney.com/"},
            )
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                data = payload.get("data") or {}
                rows = data.get("diff") or []
                for row in rows:
                    row["_segment"] = segment
                return rows, int(data.get("total") or 0), ""
            except Exception as exc:  # pragma: no cover - public network behavior varies
                last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(0.4 * (attempt + 1))
    return [], 0, last_error


def _provider_status(snapshot: dict[str, Any], target_as_of_date: str, actual_date: str) -> dict[str, Any]:
    succeeded = bool(snapshot.get("succeeded") and snapshot.get("rows"))
    reason = str(snapshot.get("reason") or "")
    status = "failed"
    partial_failures: list[str] = []
    if succeeded and reason:
        status = "partial"
        partial_failures.append(reason)
    elif succeeded:
        status = "passed"
    return {
        "status_id": "A-SHARE-DATA-FRESHNESS-PROVIDER-STATUS",
        "target_version": TARGET_VERSION,
        "requested_target_as_of_date": target_as_of_date,
        "resolved_actual_data_date": actual_date,
        "providers_attempted": [snapshot.get("provider", "qstock_reference_public_http")],
        "providers_succeeded": [snapshot.get("provider", "qstock_reference_public_http")] if succeeded else [],
        "providers_failed": [] if succeeded else [snapshot.get("provider", "qstock_reference_public_http")],
        "provider_call_count": 1,
        "network_refresh_executed": True,
        "public_network_refresh_only": True,
        "broker_network_access": False,
        "real_account_access": False,
        "provider_errors": [] if succeeded else [str(snapshot.get("reason") or "provider returned no rows")],
        "partial_provider_failures": partial_failures,
        "overall_provider_status": status,
    }


def _coverage_summary(*, rows: list[dict[str, Any]], snapshot: dict[str, Any], target_as_of_date: str, actual_date: str) -> dict[str, Any]:
    symbols = {str(row.get("f12") or "") for row in rows if row.get("f12")}
    refreshed = len(symbols)
    missing_quote_count = len([row for row in rows if row.get("f12") and row.get("f2") in (None, "", "-", "--")])
    raw_total = int(snapshot.get("raw_total") or len(symbols) or 0)
    missing = max(raw_total - refreshed, 0) if raw_total else 0
    ratio = round(refreshed / raw_total, 6) if raw_total else 0.0
    warnings = []
    blocking = []
    partial = bool(snapshot.get("reason")) or missing > 0
    if partial:
        warnings.append("partial_data_detected")
    if missing_quote_count:
        warnings.append(f"missing_quote_symbol_count={missing_quote_count}")
    if ratio < MINIMUM_REQUIRED_COVERAGE_RATIO:
        blocking.append("coverage_below_minimum_required_ratio")
    return {
        "coverage_id": "A-SHARE-DATA-FRESHNESS-COVERAGE-SUMMARY",
        "requested_target_as_of_date": target_as_of_date,
        "resolved_actual_data_date": actual_date,
        "universe_symbol_count": raw_total,
        "refreshed_symbol_count": refreshed,
        "missing_symbol_count": missing,
        "missing_symbols_sample": [],
        "missing_quote_symbol_count": missing_quote_count,
        "coverage_ratio": ratio,
        "minimum_required_coverage_ratio": MINIMUM_REQUIRED_COVERAGE_RATIO,
        "coverage_passed": ratio >= MINIMUM_REQUIRED_COVERAGE_RATIO,
        "partial_data_detected": partial,
        "stale_data_remaining": False,
        "coverage_warnings": warnings,
        "coverage_blocking_reasons": blocking,
    }


def _refresh_request(*, target_as_of_date: str, actual_date: str, reason: str, dry_run: bool) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-DATA-FRESHNESS-REFRESH-REQUEST",
        "target_version": TARGET_VERSION,
        "requested_target_as_of_date": target_as_of_date,
        "resolved_actual_data_date": actual_date,
        "date_resolution_reason": reason,
        "dry_run": dry_run,
        "refresh_scope": list(REFRESH_SCOPE),
        "excluded_scope": list(EXCLUDED_SCOPE),
        "public_market_data_only": True,
        "broker_connection_allowed": False,
        "real_account_read_allowed": False,
        "real_order_allowed": False,
        "order_preview_allowed": False,
        "buy_sell_signal_allowed": False,
    }


def _refresh_result(
    *,
    target_as_of_date: str,
    actual_date: str,
    started_at: str,
    completed_at: str,
    duration_seconds: float,
    dry_run: bool,
    provider_status: dict[str, Any],
    coverage: dict[str, Any],
    blocking_reasons: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    executed = not dry_run and not blocking_reasons
    return {
        "result_id": "A-SHARE-DATA-FRESHNESS-REFRESH-RESULT",
        "target_version": TARGET_VERSION,
        "requested_target_as_of_date": target_as_of_date,
        "resolved_actual_data_date": actual_date,
        "refresh_started_at": started_at,
        "refresh_completed_at": completed_at,
        "refresh_duration_seconds": duration_seconds,
        "overall_passed": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "dry_run": dry_run,
        "data_refresh_executed": executed,
        "public_network_refresh_run": True,
        "public_market_data_only": True,
        "provider_status_passed": provider_status["overall_provider_status"] in {"passed", "partial"},
        "coverage_passed": coverage["coverage_passed"],
        "staleness_before_refresh": {"source_data_date": PREVIOUS_SOURCE_DATA_DATE, "calendar_days_stale": _days_between(PREVIOUS_SOURCE_DATA_DATE, target_as_of_date), "trading_days_stale": None},
        "staleness_after_refresh": {"source_data_date": actual_date, "calendar_days_stale": _days_between(actual_date, target_as_of_date), "trading_days_stale": 0 if actual_date == target_as_of_date else None},
        "research_pipeline_rerun": False,
        "build_from_existing_data_run": False,
        "owner_daily_pack_run": False,
        "owner_readiness_gate_rerun": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "not_investment_advice": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _boundary_check(*, actual_date: str, data_refresh_executed: bool, blocking_reasons: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "boundary_id": "A-SHARE-DATA-FRESHNESS-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "resolved_actual_data_date": actual_date,
        "public_market_data_refresh_only": True,
        "data_refresh_executed": data_refresh_executed,
        "public_network_refresh_run": True,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "research_pipeline_rerun": False,
        "build_from_existing_data_run": False,
        "owner_daily_pack_run": False,
        "owner_readiness_gate_rerun": False,
        "controlled_gate_reevaluation_run": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "model_profit_guaranteed": False,
        "data_freshness_used_as_trade_instruction": False,
        "overall_passed": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
    }


def _manifest(
    *,
    paths: ProjectPaths,
    target_as_of_date: str,
    actual_date: str,
    artifact_paths: dict[str, Path],
    updated_data_paths: list[str],
    overall_passed: bool,
    blocking_reasons: list[str],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-DATA-FRESHNESS-MANIFEST",
        "target_version": TARGET_VERSION,
        "requested_target_as_of_date": target_as_of_date,
        "resolved_actual_data_date": actual_date,
        "generated_at": utc_now(),
        "source_version": SOURCE_VERSION,
        "refresh_result_path": _rel(artifact_paths["data_freshness_refresh_result"], paths.project_root),
        "provider_status_path": _rel(artifact_paths["data_freshness_provider_status"], paths.project_root),
        "coverage_summary_path": _rel(artifact_paths["data_freshness_coverage_summary"], paths.project_root),
        "boundary_check_path": _rel(artifact_paths["data_freshness_boundary_check"], paths.project_root),
        "markdown_report_path": _rel(artifact_paths["markdown_report"], paths.project_root),
        "updated_data_paths": updated_data_paths,
        "overall_passed": overall_passed,
        "blocking_reasons": blocking_reasons,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _artifact_paths(paths: ProjectPaths, actual_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_data_freshness" / "daily" / actual_date
    output_dir = paths.outputs_dir / "equity_data_freshness" / "daily" / actual_date
    return {
        "data_freshness_refresh_request": data_dir / "data_freshness_refresh_request.json",
        "data_freshness_provider_status": data_dir / "data_freshness_provider_status.json",
        "data_freshness_coverage_summary": data_dir / "data_freshness_coverage_summary.json",
        "data_freshness_refresh_result": data_dir / "data_freshness_refresh_result.json",
        "data_freshness_boundary_check": data_dir / "data_freshness_boundary_check.json",
        "data_freshness_manifest": data_dir / "data_freshness_manifest.json",
        "markdown_report": output_dir / "A_SHARE_DATA_FRESHNESS_REFRESH_RESULT.md",
    }


def _markdown_report(result: dict[str, Any], provider: dict[str, Any], coverage: dict[str, Any], request: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Data Freshness Refresh Result",
            "",
            "## 1. Refresh Summary",
            f"- overall_passed: {result['overall_passed']}",
            f"- data_refresh_executed: {result['data_refresh_executed']}",
            f"- dry_run: {result['dry_run']}",
            "",
            "## 2. Requested Date vs Actual Data Date",
            f"- requested_target_as_of_date: {request['requested_target_as_of_date']}",
            f"- resolved_actual_data_date: {request['resolved_actual_data_date']}",
            f"- date_resolution_reason: {request['date_resolution_reason']}",
            "",
            "## 3. Provider Status",
            f"- overall_provider_status: {provider['overall_provider_status']}",
            f"- providers_attempted: {', '.join(provider['providers_attempted'])}",
            f"- provider_errors: {provider['provider_errors']}",
            "",
            "## 4. Coverage Summary",
            f"- coverage_ratio: {coverage['coverage_ratio']}",
            f"- coverage_passed: {coverage['coverage_passed']}",
            f"- missing_symbol_count: {coverage['missing_symbol_count']}",
            "",
            "## 5. Staleness Before / After",
            f"- before: {result['staleness_before_refresh']}",
            f"- after: {result['staleness_after_refresh']}",
            "",
            "## 6. Explicit Non-Trading Boundary",
            "This refresh updates public market research data only.",
            "This is not investment advice.",
            "This is not live trading ready.",
            "",
            "## 7. What This Does Not Do",
            "This does not rerun research pipeline.",
            "This does not generate candidates, scores, virtual portfolios, or trade signals.",
            "This does not rerun owner-readiness gate.",
            "This does not change owner-readiness blocked state.",
            "",
            "## 8. Recommended Next Version",
            f"- {RECOMMENDED_NEXT_VERSION}",
            "",
        ]
    )


def _days_between(start: str, end: str) -> int | None:
    try:
        return (date.fromisoformat(end) - date.fromisoformat(start)).days
    except ValueError:
        return None


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
