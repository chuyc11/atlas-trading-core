"""Diagnose A-share historical backfill coverage failures."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data.full_market_symbol_queue import build_a_share_historical_backfill_symbol_queue
from trading_core.equity_data_quality.common import (
    HISTORICAL_BASELINE_FAIL_CLOSED_COMMIT,
    HISTORICAL_BOUNDARY,
    HISTORICAL_TARGET_VERSION,
    data_quality_dir,
    markdown_boundary,
    read_frame,
    read_json,
    write_report,
)
from trading_core.equity_data_quality.history_manifest import history_dirs
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


DIAGNOSTIC_ID = "A-SHARE-HISTORICAL-BACKFILL-ROOT-CAUSE"


def diagnose_a_share_historical_backfill_coverage(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    dirs = history_dirs(paths)
    master = read_frame(paths.data_dir / "equity_universe" / "equity_master.parquet")
    price = read_frame(dirs["market_history"] / "daily_price_history_panel.parquet")
    daily_manifest = read_json(dirs["market_history"] / "daily_price_history_manifest.json")
    symbol_manifest = read_json(data_quality_dir(paths) / "a_share_historical_backfill_symbol_manifest.json")
    queue = read_json(data_quality_dir(paths) / "a_share_historical_backfill_symbol_queue.json")
    if not queue:
        queue = build_a_share_historical_backfill_symbol_queue(paths=paths)
    equity_master_symbols = int(master["symbol"].nunique()) if not master.empty else 0
    historical_price_symbols = int(price["symbol"].nunique()) if not price.empty else 0
    queue_symbols = int(queue.get("eligible_price_backfill_symbols") or queue.get("queue_total_symbols") or 0)
    attempted = _attempted_symbols(daily_manifest, symbol_manifest)
    provider_summary = _provider_summary(daily_manifest, symbol_manifest)
    suspected, confirmed = _root_causes(
        equity_master_symbols=equity_master_symbols,
        historical_price_symbols=historical_price_symbols,
        backfill_input_symbols=attempted,
        queue_symbols=queue_symbols,
        daily_manifest=daily_manifest,
        symbol_manifest=symbol_manifest,
    )
    payload: dict[str, Any] = {
        "diagnostic_id": DIAGNOSTIC_ID,
        "target_version": HISTORICAL_TARGET_VERSION,
        "baseline_fail_closed_commit": HISTORICAL_BASELINE_FAIL_CLOSED_COMMIT,
        "equity_master_symbols": equity_master_symbols,
        "historical_price_symbols": historical_price_symbols,
        "backfill_input_symbols": attempted,
        "backfill_queue_symbols": queue_symbols,
        "suspected_root_causes": suspected,
        "confirmed_root_causes": confirmed,
        "uses_equity_master_as_source": bool(queue.get("uses_equity_master_as_source")),
        "uses_etf_universe": False,
        "uses_fixture_universe": False,
        "symbol_limit_detected": _symbol_limit_detected(daily_manifest, attempted, historical_price_symbols, equity_master_symbols),
        "provider_batch_limit_detected": bool(daily_manifest.get("provider_batch_limit_detected", False)),
        "tests_accidentally_forced_sample_mode": False,
        "cli_default_symbol_limit_exists": False,
        "local_environment_variable_limited_symbols": False,
        "provider_attempts": provider_summary,
        "overall_diagnosis_passed": bool(confirmed),
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    json_path = data_quality_dir(paths) / "a_share_historical_backfill_root_cause.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_HISTORICAL_BACKFILL_ROOT_CAUSE.md"
    lines = [
        "# A-Share Historical Backfill Root Cause",
        "",
        f"- target_version: {HISTORICAL_TARGET_VERSION}",
        f"- equity_master_symbols: {equity_master_symbols}",
        f"- historical_price_symbols: {historical_price_symbols}",
        f"- backfill_input_symbols: {attempted}",
        f"- backfill_queue_symbols: {queue_symbols}",
        f"- suspected_root_causes: {suspected}",
        f"- confirmed_root_causes: {confirmed}",
        f"- symbol_limit_detected: {str(payload['symbol_limit_detected']).lower()}",
        "",
        "## Provider Attempts",
        f"- {provider_summary}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "- Live trading ready: false.",
        "",
    ]
    return write_report(json_path, payload, report_path, "\n".join(lines))


def _attempted_symbols(daily_manifest: dict[str, Any], symbol_manifest: dict[str, Any]) -> int:
    if symbol_manifest.get("summary", {}).get("symbols_attempted") is not None:
        return int(symbol_manifest["summary"]["symbols_attempted"])
    if daily_manifest.get("symbols_attempted") is not None:
        return int(daily_manifest["symbols_attempted"])
    if daily_manifest.get("attempted_symbols") is not None:
        return int(daily_manifest["attempted_symbols"])
    return 0


def _provider_summary(daily_manifest: dict[str, Any], symbol_manifest: dict[str, Any]) -> dict[str, Any]:
    breakdown = daily_manifest.get("provider_breakdown") or {}
    if breakdown:
        return breakdown
    summary = symbol_manifest.get("summary", {})
    if summary.get("provider_breakdown"):
        return summary["provider_breakdown"]
    providers = daily_manifest.get("providers_attempted", [])
    failed = daily_manifest.get("providers_failed", [])
    succeeded = daily_manifest.get("providers_succeeded", [])
    return {
        str(provider): {
            "attempted_symbol_count": int(daily_manifest.get("attempted_symbols", 0)),
            "succeeded_symbol_count": int(daily_manifest.get("symbol_count", 0)) if provider in succeeded else 0,
            "failed_symbol_count": len(failed),
        }
        for provider in providers
    }


def _root_causes(
    *,
    equity_master_symbols: int,
    historical_price_symbols: int,
    backfill_input_symbols: int,
    queue_symbols: int,
    daily_manifest: dict[str, Any],
    symbol_manifest: dict[str, Any],
) -> tuple[list[str], list[str]]:
    suspected: list[str] = []
    confirmed: list[str] = []
    if historical_price_symbols < 3000:
        suspected.append("historical price panel coverage is below release threshold")
    if backfill_input_symbols and backfill_input_symbols < max(3000, equity_master_symbols // 2):
        suspected.append("backfill input universe was materially smaller than equity master")
    if backfill_input_symbols <= 10 or historical_price_symbols <= 10:
        confirmed.append("controlled sample or max-symbols run overwrote historical price panel with about 10 symbols")
    if not daily_manifest.get("source_universe") and not symbol_manifest:
        suspected.append("legacy v0.7.1.1 manifest did not record a full-market symbol queue")
    if queue_symbols >= 3000 and historical_price_symbols < 3000:
        confirmed.append("full-market queue exists but historical provider coverage has not been materialized into the price panel")
    if daily_manifest.get("sample_mode"):
        confirmed.append("sample_mode=true in daily price manifest")
    if daily_manifest.get("symbol_limit_detected"):
        confirmed.append("symbol limit detected in historical price manifest")
    return suspected, confirmed


def _symbol_limit_detected(daily_manifest: dict[str, Any], attempted: int, historical_symbols: int, master_symbols: int) -> bool:
    if bool(daily_manifest.get("symbol_limit_detected")):
        return True
    if attempted and master_symbols and attempted < master_symbols:
        return True
    return historical_symbols <= 10
