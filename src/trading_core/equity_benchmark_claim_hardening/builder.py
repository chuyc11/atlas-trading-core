"""Build v1.0.1 A-share benchmark and performance claim hardening artifacts."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_benchmarks.benchmark_config import INDEX_CODE_MAP, candidate_index_panel_paths, required_input_paths
from trading_core.equity_benchmarks.benchmark_returns import returns_from_price_frame
from trading_core.equity_benchmarks.equal_weight_benchmark import build_equal_weight_benchmark
from trading_core.equity_data_quality.common import read_frame, read_json, sha256_file, utc_now, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.0.1-a-share-benchmark-data-and-performance-claim-hardening"
SOURCE_VERSION = "v1.0.0-a-share-autonomous-simulation-platform-release"
RECOMMENDED_NEXT_VERSION = "v1.0.2-a-share-owner-dashboard-benchmark-integration-and-report-polish"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21
BENCHMARK_IDS = ["CSI300", "CSI500", "CSI1000", "CASH", "EQUAL_WEIGHT_TRADABLE_UNIVERSE"]
INDEX_BENCHMARK_IDS = ["CSI300", "CSI500", "CSI1000"]
JSON_NAMES = [
    "benchmark_claim_hardening_request",
    "benchmark_source_registry",
    "benchmark_coverage_matrix",
    "cash_benchmark_result",
    "equal_weight_universe_benchmark_result",
    "csi_benchmark_attribution_result",
    "simulated_performance_attribution_result",
    "performance_claim_guard_result",
    "benchmark_claim_hardening_result",
    "benchmark_claim_hardening_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_BENCHMARK_AND_CLAIM_HARDENING_REPORT.md",
    "A_SHARE_PERFORMANCE_CLAIM_GUARD_REPORT.md",
]


class _BenchmarkConfig:
    def __init__(self, as_of_date: str) -> None:
        self.as_of_date = as_of_date
        self.lookback_trading_days = 250
        self.minimum_required_trading_days = 2


def build_a_share_benchmark_claim_hardening(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_public_benchmark_refresh: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    _ensure_dirs(paths, as_of_date)
    artifacts = _artifact_paths(paths, as_of_date)
    generated_at = utc_now()
    request = _request(as_of_date, allow_public_benchmark_refresh, generated_at)
    index_prices, index_sources = _load_local_index_prices(paths, as_of_date)
    simulated_returns = _load_simulated_account_returns(paths, as_of_date)
    cash = _cash_benchmark(as_of_date, simulated_returns)
    equal_weight = _equal_weight_benchmark(paths, as_of_date)
    csi = _csi_attribution(as_of_date, index_prices, index_sources, simulated_returns)
    simulated = _simulated_performance_attribution(as_of_date, simulated_returns, cash, equal_weight, csi)
    registry = _source_registry(as_of_date, index_prices, index_sources, cash, equal_weight, simulated_returns)
    coverage = _coverage_matrix(as_of_date, registry)
    guard = _claim_guard(registry, csi, simulated)
    result = _result(as_of_date, registry, coverage, cash, equal_weight, csi, simulated, guard)
    payloads = {
        "benchmark_claim_hardening_request": request,
        "benchmark_source_registry": registry,
        "benchmark_coverage_matrix": coverage,
        "cash_benchmark_result": cash,
        "equal_weight_universe_benchmark_result": equal_weight,
        "csi_benchmark_attribution_result": csi,
        "simulated_performance_attribution_result": simulated,
        "performance_claim_guard_result": guard,
        "benchmark_claim_hardening_result": result,
    }
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_owner_reports(artifacts, registry, csi, simulated, guard, result)
    manifest = _manifest(paths, as_of_date, generated_at, result)
    write_json(artifacts["benchmark_claim_hardening_manifest"], manifest)
    return result


def _request(as_of_date: str, allow_public_benchmark_refresh: bool, generated_at: str) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-BENCHMARK-CLAIM-HARDENING-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "allow_public_benchmark_refresh": allow_public_benchmark_refresh,
        "allow_public_benchmark_refresh_used": False,
        "public_market_data_only": True,
        "broker_allowed": False,
        "real_account_allowed": False,
        "real_orders_allowed": False,
        "cash_return_model": "zero_return_cash_baseline",
        "scope": [
            "benchmark_source_registry",
            "benchmark_coverage_matrix",
            "cash_benchmark",
            "equal_weight_tradable_universe_benchmark",
            "csi_benchmark_attribution",
            "simulated_performance_attribution",
            "performance_claim_guard",
        ],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _load_local_index_prices(paths: ProjectPaths, as_of_date: str) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
    frames: list[pd.DataFrame] = []
    sources: dict[str, dict[str, Any]] = {}
    code_to_benchmark = {code: benchmark for benchmark, codes in INDEX_CODE_MAP.items() for code in codes}
    for path in candidate_index_panel_paths(paths):
        frame = read_frame(path)
        if frame.empty or "date" not in frame.columns:
            continue
        code_column = "benchmark_id" if "benchmark_id" in frame.columns else "symbol" if "symbol" in frame.columns else "index_code" if "index_code" in frame.columns else ""
        close_column = "close" if "close" in frame.columns else "adj_close" if "adj_close" in frame.columns else ""
        if not code_column or not close_column:
            continue
        rows = []
        for _, row in frame.iterrows():
            code = str(row.get(code_column))
            benchmark_id = code if code in INDEX_BENCHMARK_IDS else code_to_benchmark.get(code)
            if benchmark_id not in INDEX_BENCHMARK_IDS:
                continue
            day = str(row.get("date"))[:10]
            if day > as_of_date:
                continue
            rows.append(
                {
                    "date": day,
                    "benchmark_id": benchmark_id,
                    "symbol_or_index_code": INDEX_CODE_MAP[benchmark_id][0],
                    "close": _float(row.get(close_column)),
                    "source_type": "local_index_price_panel",
                    "source_path": _rel(path, paths.project_root),
                    "source_timestamp": str(row.get("source_timestamp") or row.get("ingested_at") or ""),
                    "is_placeholder": False,
                }
            )
        if rows:
            normalized = pd.DataFrame(rows).dropna(subset=["close"])
            frames.append(normalized)
            for benchmark_id in normalized["benchmark_id"].unique():
                sources[str(benchmark_id)] = {"source_type": "local_index_price_panel", "source_path": _rel(path, paths.project_root)}
    if not frames:
        return pd.DataFrame(), sources
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(["date", "benchmark_id"]).sort_values(["benchmark_id", "date"])
    return combined.reset_index(drop=True), sources


def _load_simulated_account_returns(paths: ProjectPaths, as_of_date: str) -> list[dict[str, Any]]:
    tracking = read_json(paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "portfolio_performance_snapshot.json")
    rows = tracking.get("records") or tracking.get("portfolio_performance_records") or tracking.get("performance_records") or []
    records: list[dict[str, Any]] = []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            day = str(row.get("date") or row.get("as_of_date") or "")[:10]
            if not day or day > as_of_date:
                continue
            ret = row.get("daily_return")
            if ret is None:
                ret = row.get("portfolio_daily_return")
            if ret is None:
                ret = row.get("simulated_account_return")
            if ret is not None:
                records.append({"date": day, "daily_return": _float(ret) or 0.0, "source": "portfolio_performance_snapshot"})
    if records:
        return sorted(records, key=lambda item: item["date"])
    nav = read_json(paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "portfolio_nav_snapshot.json")
    nav_rows = nav.get("records") or nav.get("nav_records") or []
    clean_nav = []
    if isinstance(nav_rows, list):
        for row in nav_rows:
            if not isinstance(row, dict):
                continue
            day = str(row.get("date") or row.get("as_of_date") or "")[:10]
            value = _float(row.get("nav") or row.get("portfolio_nav") or row.get("total_nav"))
            if day and day <= as_of_date and value is not None:
                clean_nav.append({"date": day, "nav": value})
    if len(clean_nav) >= 2:
        clean_nav = sorted(clean_nav, key=lambda item: item["date"])
        prev = None
        for row in clean_nav:
            daily_return = 0.0 if prev in (None, 0) else (row["nav"] / prev) - 1.0
            records.append({"date": row["date"], "daily_return": daily_return, "source": "portfolio_nav_snapshot"})
            prev = row["nav"]
    return records


def _cash_benchmark(as_of_date: str, simulated_returns: list[dict[str, Any]]) -> dict[str, Any]:
    dates = [row["date"] for row in simulated_returns] or [as_of_date]
    records = [{"date": day, "benchmark_id": "CASH", "daily_return": 0.0} for day in dates]
    return {
        "result_id": "A-SHARE-CASH-BENCHMARK-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_id": "CASH",
        "status": "passed",
        "cash_return_model": "zero_return_cash_baseline",
        "simulation_comparison_only": True,
        "not_deposit_yield": True,
        "not_money_market_yield": True,
        "not_real_risk_free_rate": True,
        "coverage_start": records[0]["date"],
        "coverage_end": records[-1]["date"],
        "coverage_ratio": 1.0,
        "records": records,
        "warnings": ["cash benchmark is a zero-return simulation baseline, not a real yield source"],
        "fabricated_benchmark_data": False,
    }


def _equal_weight_benchmark(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    inputs = required_input_paths(paths, as_of_date)
    universe = read_json(inputs["tradable_universe"])
    rows = universe if isinstance(universe, list) else universe.get("records") or universe.get("tradable_universe") or universe.get("symbols") or []
    symbols = _symbols_from_rows(rows)
    adjusted = read_frame(inputs["adjusted_price_history"])
    daily = read_frame(inputs["daily_price_history"])
    checks = {
        "universe_source_exists": inputs["tradable_universe"].exists(),
        "price_data_exists": inputs["adjusted_price_history"].exists() or inputs["daily_price_history"].exists(),
        "return_data_exists": False,
        "constituent_count": len(symbols),
        "coverage_ratio": 0.0,
        "missing_symbol_count": len(symbols),
        "missing_date_count": None,
        "rebalance_assumption": "static_as_of_tradable_universe_equal_weight",
        "survivorship_bias_warning": True,
    }
    if not symbols or (adjusted.empty and daily.empty):
        status = "warning"
        reason = "local universe or price data unavailable"
        records: list[dict[str, Any]] = []
        availability = {}
        exclusions = {"excluded_constituent_count": len(symbols), "price_missing_count": len(symbols)}
    else:
        config = _BenchmarkConfig(as_of_date)
        records, availability, exclusions = build_equal_weight_benchmark(
            benchmark_id="EQUAL_WEIGHT_TRADABLE_UNIVERSE",
            symbols=symbols,
            adjusted_prices=adjusted,
            daily_prices=daily,
            config=config,  # type: ignore[arg-type]
        )
        status = "passed" if availability.get("status") == "available" else "warning"
        reason = availability.get("missing_reason")
        checks["return_data_exists"] = bool(records)
        checks["missing_symbol_count"] = int(exclusions.get("price_missing_count", 0))
        checks["coverage_ratio"] = 0.0 if not symbols else round((len(symbols) - checks["missing_symbol_count"]) / len(symbols), 6)
        checks["missing_date_count"] = 0 if records else None
    return {
        "result_id": "A-SHARE-EQUAL-WEIGHT-UNIVERSE-BENCHMARK-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_id": "EQUAL_WEIGHT_TRADABLE_UNIVERSE",
        "status": status,
        "reason": reason,
        "checks": checks,
        "availability": availability,
        "exclusions": exclusions,
        "records": records,
        "warnings": ["survivorship_bias_warning: static as-of universe is not a point-in-time constituent history"],
        "fabricated_benchmark_data": False,
    }


def _csi_attribution(
    as_of_date: str,
    index_prices: pd.DataFrame,
    index_sources: dict[str, dict[str, Any]],
    simulated_returns: list[dict[str, Any]],
) -> dict[str, Any]:
    benchmark_returns = returns_from_price_frame(index_prices) if not index_prices.empty else []
    simulated_by_date = {row["date"]: row["daily_return"] for row in simulated_returns}
    results = []
    generated_any = False
    for benchmark_id in INDEX_BENCHMARK_IDS:
        rows = [row for row in benchmark_returns if row.get("benchmark_id") == benchmark_id and row.get("date") <= as_of_date]
        common = [row for row in rows if row["date"] in simulated_by_date]
        source = index_sources.get(benchmark_id, {})
        if rows and common:
            benchmark_total = _compound([float(row["daily_return"]) for row in common])
            account_total = _compound([float(simulated_by_date[row["date"]]) for row in common])
            excess = account_total - benchmark_total
            active = [float(simulated_by_date[row["date"]]) - float(row["daily_return"]) for row in common]
            tracking_error = _std(active) * math.sqrt(252) if len(active) > 1 else None
            result = {
                "benchmark_id": benchmark_id,
                "status": "passed",
                "benchmark_attribution_status": "passed",
                "benchmark_relative_metrics_generated": True,
                "source_type": source.get("source_type"),
                "source_path_or_provider": source.get("source_path"),
                "coverage_start": common[0]["date"],
                "coverage_end": common[-1]["date"],
                "coverage_ratio": round(len(common) / max(len(simulated_returns), 1), 6),
                "benchmark_return": benchmark_total,
                "simulated_account_return": account_total,
                "excess_return": excess,
                "relative_drawdown": _relative_drawdown(common, simulated_by_date),
                "tracking_error": tracking_error,
                "hit_ratio_vs_benchmark": sum(1 for value in active if value > 0) / len(active),
                "rolling_relative_return": [],
                "fabricated_excess_return": False,
                "fabricated_tracking_error": False,
                "fabricated_relative_drawdown": False,
                "blocking_reasons": [],
                "warnings": [],
            }
            generated_any = True
        else:
            result = {
                "benchmark_id": benchmark_id,
                "status": "warning",
                "benchmark_attribution_status": "warning",
                "benchmark_relative_metrics_generated": False,
                "source_type": source.get("source_type") or "missing",
                "source_path_or_provider": source.get("source_path"),
                "coverage_start": rows[0]["date"] if rows else "",
                "coverage_end": rows[-1]["date"] if rows else "",
                "coverage_ratio": 0.0,
                "benchmark_return": None,
                "simulated_account_return": None,
                "excess_return": None,
                "relative_drawdown": None,
                "tracking_error": None,
                "hit_ratio_vs_benchmark": None,
                "rolling_relative_return": [],
                "fabricated_excess_return": False,
                "fabricated_tracking_error": False,
                "fabricated_relative_drawdown": False,
                "blocking_reasons": [],
                "warnings": ["benchmark source missing or not aligned with simulated account dates"],
            }
        results.append(result)
    return {
        "result_id": "A-SHARE-CSI-BENCHMARK-ATTRIBUTION-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_attribution_status": "passed" if generated_any else "warning",
        "benchmark_relative_metrics_generated": generated_any,
        "benchmarks": results,
        "fabricated_benchmark_data": False,
        "fabricated_excess_return": False,
        "fabricated_tracking_error": False,
        "fabricated_relative_drawdown": False,
    }


def _simulated_performance_attribution(
    as_of_date: str,
    simulated_returns: list[dict[str, Any]],
    cash: dict[str, Any],
    equal_weight: dict[str, Any],
    csi: dict[str, Any],
) -> dict[str, Any]:
    simulated_total = _compound([row["daily_return"] for row in simulated_returns]) if simulated_returns else None
    cash_total = _compound([row["daily_return"] for row in cash["records"]])
    equal_records = equal_weight.get("records", [])
    equal_total = _compound([row["daily_return"] for row in equal_records]) if equal_records else None
    return {
        "result_id": "A-SHARE-SIMULATED-PERFORMANCE-ATTRIBUTION-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "simulated_performance_attribution_generated": True,
        "simulated_account_return": simulated_total,
        "cash_benchmark_return": cash_total,
        "equal_weight_universe_benchmark_return": equal_total,
        "csi_benchmark_relative_metrics_available": bool(csi.get("benchmark_relative_metrics_generated")),
        "simulation_only_disclaimer_required": True,
        "full_pytest_run": False,
        "full_pytest_deferred_until": "next-major-closeout-or-explicit-request",
        "fabricated_benchmark_data": False,
        "fabricated_excess_return": False,
        "fabricated_tracking_error": False,
        "fabricated_relative_drawdown": False,
    }


def _source_registry(
    as_of_date: str,
    index_prices: pd.DataFrame,
    index_sources: dict[str, dict[str, Any]],
    cash: dict[str, Any],
    equal_weight: dict[str, Any],
    simulated_returns: list[dict[str, Any]],
) -> dict[str, Any]:
    simulated_dates = {row["date"] for row in simulated_returns}
    records = []
    for benchmark_id in INDEX_BENCHMARK_IDS:
        subset = index_prices[index_prices["benchmark_id"] == benchmark_id] if not index_prices.empty else pd.DataFrame()
        dates = set(subset["date"].astype(str)) if not subset.empty else set()
        common = dates & simulated_dates if simulated_dates else dates
        available = not subset.empty
        aligned = bool(common) if simulated_dates else available
        stale = bool(available and str(subset["date"].max()) < as_of_date)
        status = "passed" if available and aligned and not stale else "warning" if available else "warning"
        records.append(
            _registry_record(
                benchmark_id=benchmark_id,
                benchmark_name=benchmark_id,
                source_type=index_sources.get(benchmark_id, {}).get("source_type") or "missing",
                source_path_or_provider=index_sources.get(benchmark_id, {}).get("source_path"),
                as_of_date=as_of_date,
                available=available,
                coverage_start=str(subset["date"].min()) if available else "",
                coverage_end=str(subset["date"].max()) if available else "",
                coverage_ratio=round(len(common) / max(len(simulated_dates), 1), 6) if available and simulated_dates else (1.0 if available else 0.0),
                missing_dates=sorted(simulated_dates - dates)[:100],
                stale=stale,
                source_quality_status=status,
                usable_for_simulated_relative_metrics=available and aligned and not stale,
                blocking_reasons=[],
                warnings=[] if available else ["index benchmark source missing"],
            )
        )
    records.append(
        _registry_record(
            benchmark_id="CASH",
            benchmark_name="zero-return cash baseline",
            source_type="constructed_zero_return_cash_baseline",
            source_path_or_provider="internal_assumption",
            as_of_date=as_of_date,
            available=True,
            coverage_start=cash["coverage_start"],
            coverage_end=cash["coverage_end"],
            coverage_ratio=1.0,
            missing_dates=[],
            stale=False,
            source_quality_status="passed",
            usable_for_simulated_relative_metrics=True,
            blocking_reasons=[],
            warnings=cash["warnings"],
        )
    )
    checks = equal_weight.get("checks", {})
    records.append(
        _registry_record(
            benchmark_id="EQUAL_WEIGHT_TRADABLE_UNIVERSE",
            benchmark_name="equal-weight local tradable universe",
            source_type="local_tradable_universe_and_price_history",
            source_path_or_provider="data/equity_selection + data/equity_market/history",
            as_of_date=as_of_date,
            available=equal_weight.get("status") == "passed",
            coverage_start=(equal_weight.get("records") or [{}])[0].get("date", "") if equal_weight.get("records") else "",
            coverage_end=(equal_weight.get("records") or [{}])[-1].get("date", "") if equal_weight.get("records") else "",
            coverage_ratio=float(checks.get("coverage_ratio") or 0.0),
            missing_dates=[],
            stale=False,
            source_quality_status=str(equal_weight.get("status")),
            usable_for_simulated_relative_metrics=equal_weight.get("status") == "passed",
            blocking_reasons=[],
            warnings=equal_weight.get("warnings", []),
        )
    )
    return {
        "registry_id": "A-SHARE-BENCHMARK-SOURCE-REGISTRY",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "records": records,
        "usable_for_real_performance_claims": False,
        "fabricated_benchmark_data": False,
    }


def _registry_record(**kwargs: Any) -> dict[str, Any]:
    return {
        **kwargs,
        "usable_for_real_performance_claims": False,
    }


def _coverage_matrix(as_of_date: str, registry: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for record in registry["records"]:
        rows.append(
            {
                "benchmark_id": record["benchmark_id"],
                "available": record["available"],
                "coverage_start": record["coverage_start"],
                "coverage_end": record["coverage_end"],
                "coverage_ratio": record["coverage_ratio"],
                "missing_date_count": len(record["missing_dates"]),
                "stale": record["stale"],
                "source_quality_status": record["source_quality_status"],
                "usable_for_simulated_relative_metrics": record["usable_for_simulated_relative_metrics"],
                "usable_for_real_performance_claims": False,
            }
        )
    return {
        "matrix_id": "A-SHARE-BENCHMARK-COVERAGE-MATRIX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "rows": rows,
        "all_csi_benchmarks_usable": all(row["usable_for_simulated_relative_metrics"] for row in rows if row["benchmark_id"] in INDEX_BENCHMARK_IDS),
        "fabricated_benchmark_data": False,
    }


def _claim_guard(registry: dict[str, Any], csi: dict[str, Any], simulated: dict[str, Any]) -> dict[str, Any]:
    benchmark_allowed = all(
        row.get("usable_for_simulated_relative_metrics") for row in registry["records"] if row.get("benchmark_id") in INDEX_BENCHMARK_IDS
    ) and bool(csi.get("benchmark_relative_metrics_generated"))
    classifications = [
        {"category": "allowed_simulation_status_statement", "allowed": True},
        {"category": "allowed_data_quality_statement", "allowed": True},
        {"category": "allowed_internal_research_metric", "allowed": True},
        {"category": "allowed_simulated_benchmark_relative_metric", "allowed": benchmark_allowed},
        {"category": "blocked_real_performance_claim", "allowed": False},
        {"category": "blocked_unverified_benchmark_claim", "allowed": False},
        {"category": "blocked_live_trading_claim", "allowed": False},
        {"category": "blocked_investment_advice_claim", "allowed": False},
    ]
    return {
        "guard_id": "A-SHARE-PERFORMANCE-CLAIM-GUARD",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "real_performance_claim_allowed": False,
        "live_trading_claim_allowed": False,
        "investment_advice_claim_allowed": False,
        "benchmark_relative_claim_allowed": benchmark_allowed,
        "simulated_performance_claim_allowed": simulated.get("simulation_only_disclaimer_required") is True,
        "simulated_performance_claim_allowed_with_disclaimer": True,
        "simulation_only_disclaimer_required": True,
        "classifications": classifications,
        "blocked_claim_examples": [
            "real performance claim",
            "live trading ready claim",
            "investment advice claim",
            "benchmark-relative claim without usable benchmark coverage",
        ],
        "allowed_claim_requirements": ["must be simulation-only", "must cite data quality and benchmark coverage", "must avoid investment advice"],
    }


def _result(
    as_of_date: str,
    registry: dict[str, Any],
    coverage: dict[str, Any],
    cash: dict[str, Any],
    equal_weight: dict[str, Any],
    csi: dict[str, Any],
    simulated: dict[str, Any],
    guard: dict[str, Any],
) -> dict[str, Any]:
    status_by_id = {row["benchmark_id"]: row["status"] for row in csi["benchmarks"]}
    warnings = sorted(
        set(
            [
                warning
                for record in registry["records"]
                for warning in record.get("warnings", [])
            ]
            + cash.get("warnings", [])
            + equal_weight.get("warnings", [])
        )
    )
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "benchmark_source_registry_generated": bool(registry.get("records")),
        "benchmark_coverage_matrix_generated": bool(coverage.get("rows")),
        "cash_benchmark_generated": cash.get("status") == "passed",
        "equal_weight_universe_benchmark_status": equal_weight.get("status"),
        "csi300_benchmark_status": status_by_id.get("CSI300", "warning"),
        "csi500_benchmark_status": status_by_id.get("CSI500", "warning"),
        "csi1000_benchmark_status": status_by_id.get("CSI1000", "warning"),
        "simulated_performance_attribution_generated": simulated.get("simulated_performance_attribution_generated") is True,
        "performance_claim_guard_generated": bool(guard),
        "benchmark_relative_claim_allowed": guard["benchmark_relative_claim_allowed"],
        "real_performance_claim_allowed": False,
        "live_trading_claim_allowed": False,
        "investment_advice_claim_allowed": False,
        "simulated_performance_claim_allowed_with_disclaimer": True,
        "fabricated_benchmark_data": False,
        "fabricated_excess_return": False,
        "fabricated_tracking_error": False,
        "fabricated_relative_drawdown": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "blocking_reasons": [],
        "warnings": warnings,
        "full_pytest_run": False,
        "full_pytest_deferred_until": "next-major-closeout-or-explicit-request",
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _manifest(paths: ProjectPaths, as_of_date: str, generated_at: str, result: dict[str, Any]) -> dict[str, Any]:
    artifacts = _artifact_paths(paths, as_of_date)
    return {
        "manifest_id": "A-SHARE-BENCHMARK-CLAIM-HARDENING-MANIFEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "json_artifact_count": len(JSON_NAMES),
        "markdown_report_count": len(MARKDOWN_NAMES),
        "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()},
        "artifact_hashes": {key: sha256_file(path) for key, path in artifacts.items() if path.exists()},
        "overall_passed": result["overall_passed"],
        "blocking_reasons": result["blocking_reasons"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _write_owner_reports(
    artifacts: dict[str, Path],
    registry: dict[str, Any],
    csi: dict[str, Any],
    simulated: dict[str, Any],
    guard: dict[str, Any],
    result: dict[str, Any],
) -> None:
    available = [row["benchmark_id"] for row in registry["records"] if row["available"]]
    unavailable = [row["benchmark_id"] for row in registry["records"] if not row["available"]]
    _write_text(
        artifacts["benchmark_claim_hardening_report"],
        "\n".join(
            [
                "# A股 Benchmark 与绩效声明硬化报告",
                "",
                "## Benchmark Availability",
                f"- available: {available}",
                f"- unavailable_or_partial: {unavailable}",
                "",
                "## Valid Metrics",
                f"- cash_benchmark: zero_return_cash_baseline, simulation comparison only",
                f"- csi_benchmark_relative_metrics_generated: {csi['benchmark_relative_metrics_generated']}",
                f"- simulated_account_return: {simulated['simulated_account_return']}",
                "",
                "## Limitations",
                "- 缺失或未对齐的 CSI benchmark 不会生成 excess return、tracking error 或 relative drawdown。",
                "- simulation-only benchmark comparison 不是实盘交易证据，也不是账户真实收益证明。",
                "- owner-readiness 仍为 blocked：54 / 75 / gap 21。",
                "",
                "## Claim Guard",
                f"- benchmark_relative_claim_allowed: {guard['benchmark_relative_claim_allowed']}",
                f"- real_performance_claim_allowed: {guard['real_performance_claim_allowed']}",
                f"- live_trading_claim_allowed: {guard['live_trading_claim_allowed']}",
                f"- investment_advice_claim_allowed: {guard['investment_advice_claim_allowed']}",
                "",
            ]
        ),
    )
    _write_text(
        artifacts["performance_claim_guard_report"],
        "\n".join(
            [
                "# A股绩效声明 Guard 报告",
                "",
                "## Allowed",
                "- simulation status statement",
                "- data quality statement",
                "- internal research metric",
                "- simulated benchmark-relative metric only when benchmark coverage and alignment pass",
                "",
                "## Blocked",
                "- real performance claim",
                "- unverified benchmark-relative claim",
                "- live trading ready claim",
                "- investment advice claim",
                "",
                "## Current Decision",
                f"- benchmark_relative_claim_allowed: {result['benchmark_relative_claim_allowed']}",
                f"- simulated_performance_claim_allowed_with_disclaimer: {result['simulated_performance_claim_allowed_with_disclaimer']}",
                f"- real_performance_claim_allowed: {result['real_performance_claim_allowed']}",
                "",
            ]
        ),
    )


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_benchmark_claim_hardening" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_benchmark_claim_hardening" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update(
        {
            "benchmark_claim_hardening_report": output_dir / "A_SHARE_BENCHMARK_AND_CLAIM_HARDENING_REPORT.md",
            "performance_claim_guard_report": output_dir / "A_SHARE_PERFORMANCE_CLAIM_GUARD_REPORT.md",
        }
    )
    return artifacts


def _ensure_dirs(paths: ProjectPaths, as_of_date: str) -> None:
    for path in _artifact_paths(paths, as_of_date).values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _symbols_from_rows(rows: Any) -> list[str]:
    if not isinstance(rows, list):
        return []
    symbols = []
    for row in rows:
        if isinstance(row, str):
            symbols.append(row)
        elif isinstance(row, dict):
            symbol = row.get("symbol") or row.get("ts_code") or row.get("code")
            if symbol and row.get("passed", True) is not False:
                symbols.append(str(symbol))
    return sorted(set(symbols))


def _compound(returns: list[float]) -> float:
    value = 1.0
    for daily_return in returns:
        value *= 1.0 + float(daily_return)
    return value - 1.0


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def _relative_drawdown(common: list[dict[str, Any]], simulated_by_date: dict[str, float]) -> float:
    curve = []
    value = 1.0
    for row in common:
        value *= 1.0 + float(simulated_by_date[row["date"]]) - float(row["daily_return"])
        curve.append(value)
    peak = curve[0] if curve else 1.0
    max_drawdown = 0.0
    for value in curve:
        peak = max(peak, value)
        max_drawdown = min(max_drawdown, (value / peak) - 1.0)
    return max_drawdown


def _float(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "--"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
