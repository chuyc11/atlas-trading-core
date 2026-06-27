"""Audit the v0.7.2 A-share tradable universe artifacts."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import json_safe, read_frame, read_json, write_report
from trading_core.equity_selection.filter_config import RECOMMENDED_NEXT_VERSION, REMEDIATION_VERSION, TARGET_VERSION, TRADABLE_UNIVERSE_BOUNDARY, TradableUniverseFilterConfig
from trading_core.equity_selection.filter_inputs import resolve_as_of_date, selection_data_dir
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


FORBIDDEN_POSITIVE_WORDING = [
    '"scores_generated": true',
    '"candidates_generated": true',
    '"watchlist_generated": true',
    '"virtual_portfolio_generated": true',
    '"day2_executed": true',
    '"run_daily_called": true',
    '"broker_connected": true',
    '"real_orders_placed": true',
    '"model_profit_guaranteed": true',
    '"live_trading_ready": true',
    "scores generated: true",
    "candidates generated: true",
    "watchlist generated: true",
    "virtual portfolios generated: true",
    "broker connected: true",
    "real orders placed: true",
    "live trading ready: true",
    "guaranteed profit",
    "model can make money",
    "保证盈利",
    "实盘就绪",
]


def audit_a_share_tradable_universe(
    *,
    as_of_date: str = "2026-06-26",
    min_listing_trading_days: int = 120,
    min_avg_amount_20d: float = 50_000_000,
    min_avg_amount_60d: float = 30_000_000,
    min_total_mv: float = 3_000_000_000,
    min_circ_mv: float = 2_000_000_000,
    min_close_price: float = 2.0,
    minimum_strict_count: int = 500,
    allow_previous_trading_day: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    calendar = read_frame(paths.data_dir / "equity_universe" / "trading_calendar.parquet")
    try:
        resolution = resolve_as_of_date(calendar, as_of_date, allow_previous_trading_day=allow_previous_trading_day)
        effective_as_of_date = resolution.as_of_date
        as_of_valid = True
        date_error = ""
    except ValueError as exc:
        effective_as_of_date = as_of_date
        as_of_valid = False
        date_error = str(exc)
    data_dir = selection_data_dir(paths, effective_as_of_date)
    artifact_paths = _artifact_paths(data_dir)
    config_payload = _load_any(artifact_paths["filter_config"], {})
    strict_rows = _load_any(artifact_paths["strict_tradable_universe_json"], [])
    tradable_rows = _load_any(artifact_paths["tradable_universe_json"], [])
    caution_rows = _load_any(artifact_paths["caution_universe"], [])
    excluded_rows = _load_any(artifact_paths["excluded_universe"], [])
    unknown_rows = _load_any(artifact_paths["unknown_status_universe"], [])
    breakdown = _load_any(artifact_paths["filter_reason_breakdown"], {})
    manifest = _load_any(artifact_paths["manifest"], {})
    all_bucket_rows = list(strict_rows) + list(caution_rows) + list(excluded_rows) + list(unknown_rows)
    counts = {
        "equity_master_symbols": int(breakdown.get("equity_master_symbols") or 0),
        "input_symbols": int(breakdown.get("input_symbols") or 0),
        "strict_tradable_count": len(strict_rows),
        "caution_count": len(caution_rows),
        "excluded_count": len(excluded_rows),
        "unknown_status_count": len(unknown_rows),
    }
    forbidden_hits = _forbidden_wording_hits(artifact_paths)
    checks = _checks(
        artifact_paths=artifact_paths,
        as_of_valid=as_of_valid,
        date_error=date_error,
        config_payload=config_payload,
        manifest=manifest,
        strict_rows=strict_rows,
        tradable_rows=tradable_rows,
        excluded_rows=excluded_rows,
        all_bucket_rows=all_bucket_rows,
        counts=counts,
        thresholds={
            "min_listing_trading_days": min_listing_trading_days,
            "min_avg_amount_20d": min_avg_amount_20d,
            "min_avg_amount_60d": min_avg_amount_60d,
            "min_total_mv": min_total_mv,
            "min_circ_mv": min_circ_mv,
            "min_close_price": min_close_price,
            "minimum_strict_count": minimum_strict_count,
        },
        forbidden_hits=forbidden_hits,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    warnings = _warnings(config_payload, counts)
    payload = {
        "audit_id": "A-SHARE-TRADABLE-UNIVERSE-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": effective_as_of_date,
        "requested_as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "checks": checks,
        "counts": counts,
        "thresholds": {
            "min_listing_trading_days": min_listing_trading_days,
            "min_avg_amount_20d": min_avg_amount_20d,
            "min_avg_amount_60d": min_avg_amount_60d,
            "min_total_mv": min_total_mv,
            "min_circ_mv": min_circ_mv,
            "min_close_price": min_close_price,
        },
        "top_exclusion_reasons": _top_exclusion_reasons(excluded_rows),
        "reason_counts": breakdown.get("reason_counts", {}),
        "stage_counts": breakdown.get("stage_counts", {}),
        "forbidden_wording_hits": forbidden_hits,
        "artifacts": {key: str(path) for key, path in artifact_paths.items()},
        "boundary": dict(TRADABLE_UNIVERSE_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    json_path = paths.data_dir / "equity_data_quality" / "a_share_tradable_universe_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_TRADABLE_UNIVERSE_AUDIT.md"
    lines = [
        "# A-Share Tradable Universe Audit",
        "",
        f"- target_version: {TARGET_VERSION}",
        f"- as_of_date: {effective_as_of_date}",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {len(warnings)}",
        f"- counts: {counts}",
        f"- top_exclusion_reasons: {payload['top_exclusion_reasons']}",
        "",
        "## Boundary",
        "- Tradable universe filter only.",
        "- No stock scores generated.",
        "- No candidates generated.",
        "- No watchlist generated.",
        "- No virtual portfolios generated.",
        "- Official forward dry-run status unchanged.",
        "- Day2 was not executed.",
        "- run-daily was not called.",
        "- No broker is connected.",
        "- No real orders were placed.",
        "- This is not a model profit guarantee.",
        "- Live trading ready: false.",
        "",
    ]
    return write_report(json_path, json_safe(payload), report_path, "\n".join(lines))


def _artifact_paths(data_dir: Path) -> dict[str, Path]:
    return {
        "filter_config": data_dir / "filter_config.json",
        "tradable_universe_json": data_dir / "tradable_universe.json",
        "tradable_universe_parquet": data_dir / "tradable_universe.parquet",
        "strict_tradable_universe_json": data_dir / "strict_tradable_universe.json",
        "caution_universe": data_dir / "caution_universe.json",
        "excluded_universe": data_dir / "excluded_universe.json",
        "unknown_status_universe": data_dir / "unknown_status_universe.json",
        "filter_reason_breakdown": data_dir / "filter_reason_breakdown.json",
        "manifest": data_dir / "tradable_universe_manifest.json",
    }


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifact_paths: dict[str, Path] = kwargs["artifact_paths"]
    strict_rows: list[dict[str, Any]] = kwargs["strict_rows"]
    tradable_rows: list[dict[str, Any]] = kwargs["tradable_rows"]
    excluded_rows: list[dict[str, Any]] = kwargs["excluded_rows"]
    all_bucket_rows: list[dict[str, Any]] = kwargs["all_bucket_rows"]
    counts: dict[str, int] = kwargs["counts"]
    thresholds: dict[str, Any] = kwargs["thresholds"]
    symbols = [row.get("symbol") for row in all_bucket_rows]
    bucket_sum = counts["strict_tradable_count"] + counts["caution_count"] + counts["excluded_count"] + counts["unknown_status_count"]
    return {
        "filter_config_exists": artifact_paths["filter_config"].exists(),
        "tradable_universe_exists": artifact_paths["tradable_universe_json"].exists() and artifact_paths["tradable_universe_parquet"].exists(),
        "excluded_universe_exists": artifact_paths["excluded_universe"].exists(),
        "reason_breakdown_exists": artifact_paths["filter_reason_breakdown"].exists(),
        "manifest_exists": artifact_paths["manifest"].exists(),
        "input_data_from_v0_7_1_2_historical_panels": bool(kwargs["manifest"].get("input_data_from_v0_7_1_2")),
        "as_of_date_valid": bool(kwargs["as_of_valid"]),
        "strict_tradable_universe_count_positive": counts["strict_tradable_count"] > 0,
        "strict_tradable_count_minimum": counts["strict_tradable_count"] > thresholds["minimum_strict_count"],
        "excluded_universe_count_positive": counts["excluded_count"] > 0,
        "bucket_counts_sum_to_input_symbols": bucket_sum == counts["input_symbols"],
        "no_duplicate_symbols_across_buckets": len(symbols) == len(set(symbols)),
        "no_st_symbols_in_strict_tradable_universe": _none_with_reason(strict_rows, {"st_stock", "name_contains_st", "risk_warning_stock", "delisting_board", "st_status_unknown"}),
        "no_delisted_symbols_in_strict_tradable_universe": _none_with_reason(strict_rows, {"delisted", "inactive"}),
        "no_new_listings_lt_120_trading_days_in_strict_tradable_universe": all((row.get("listing_trading_days") or 0) >= thresholds["min_listing_trading_days"] for row in strict_rows),
        "no_symbols_with_lt_250d_history_in_strict_tradable_universe": all(bool(row.get("has_250d_history")) for row in strict_rows),
        "no_missing_as_of_date_price_in_strict_tradable_universe": all(row.get("close") is not None for row in strict_rows),
        "no_avg_amount_20d_below_threshold_in_strict_tradable_universe": all(float(row.get("avg_amount_20d") or 0) >= thresholds["min_avg_amount_20d"] for row in strict_rows),
        "no_avg_amount_60d_below_threshold_in_strict_tradable_universe": all(float(row.get("avg_amount_60d") or 0) >= thresholds["min_avg_amount_60d"] for row in strict_rows),
        "no_total_mv_below_threshold_in_strict_tradable_universe": all(float(row.get("total_mv") or 0) >= thresholds["min_total_mv"] for row in strict_rows),
        "no_circ_mv_below_threshold_in_strict_tradable_universe": all(float(row.get("circ_mv") or 0) >= thresholds["min_circ_mv"] for row in strict_rows),
        "no_close_price_below_threshold_in_strict_tradable_universe": all(float(row.get("close") or 0) >= thresholds["min_close_price"] for row in strict_rows),
        "no_one_word_limit_up_down_risk_in_strict_tradable_universe": _none_with_reason(strict_rows, {"one_word_limit_up_risk", "one_word_limit_down_risk", "limit_status_unknown"}),
        "filter_reasons_present_for_all_excluded_symbols": all(row.get("primary_exclusion_reason") and row.get("all_exclusion_reasons") for row in excluded_rows),
        "scores_generated_false": kwargs["config_payload"].get("boundary", {}).get("scores_generated") is False,
        "candidates_generated_false": kwargs["config_payload"].get("boundary", {}).get("candidates_generated") is False,
        "watchlist_generated_false": kwargs["config_payload"].get("boundary", {}).get("watchlist_generated") is False,
        "virtual_portfolio_generated_false": kwargs["config_payload"].get("boundary", {}).get("virtual_portfolio_generated") is False,
        "official_forward_dry_run_status_unchanged_true": kwargs["config_payload"].get("boundary", {}).get("official_forward_dry_run_status_unchanged") is True,
        "day2_executed_false": kwargs["config_payload"].get("boundary", {}).get("day2_executed") is False,
        "run_daily_called_false": kwargs["config_payload"].get("boundary", {}).get("run_daily_called") is False,
        "broker_connected_false": kwargs["config_payload"].get("boundary", {}).get("broker_connected") is False,
        "real_orders_placed_false": kwargs["config_payload"].get("boundary", {}).get("real_orders_placed") is False,
        "model_profit_guaranteed_false": kwargs["config_payload"].get("boundary", {}).get("model_profit_guaranteed") is False,
        "live_trading_ready_false": kwargs["config_payload"].get("boundary", {}).get("live_trading_ready") is False,
        "tradable_universe_default_excludes_caution": not kwargs["config_payload"].get("include_caution", False) and len(tradable_rows) == len(strict_rows),
        "forbidden_positive_wording_absent": not kwargs["forbidden_hits"],
    }


def _none_with_reason(rows: list[dict[str, Any]], reasons: set[str]) -> bool:
    for row in rows:
        if reasons.intersection(set(row.get("filter_reasons") or [])):
            return False
    return True


def _top_exclusion_reasons(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        for reason in row.get("all_exclusion_reasons", []):
            counter[reason] += 1
    return dict(counter.most_common(15))


def _warnings(config_payload: dict[str, Any], counts: dict[str, int]) -> list[str]:
    warnings = []
    if config_payload.get("daily_basic_snapshot_market_cap_fallback_used"):
        warnings.append("market cap used daily_basic_panel fallback because historical daily_basic market cap is unavailable")
    if counts["caution_count"] > 0:
        warnings.append("caution universe is observation-only and excluded from default tradable output")
    if counts["unknown_status_count"] > 0:
        warnings.append("unknown status universe requires data-quality follow-up before scoring")
    return warnings


def _load_any(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _forbidden_wording_hits(artifact_paths: dict[str, Path]) -> list[str]:
    hits: list[str] = []
    for path in artifact_paths.values():
        if not path.exists() or path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            if phrase.lower() in text:
                hits.append(f"{path.name}:{phrase}")
    return hits
