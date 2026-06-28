"""Manifest, summary, and boundary helpers for performance tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_performance.performance_config import (
    BENCHMARK_IDS,
    FORBIDDEN_DATE_SCOPED_ARTIFACTS,
    FORBIDDEN_EXPLICIT_FILES,
    PERFORMANCE_BOUNDARY,
    PERFORMANCE_FLAGS,
    PORTFOLIO_IDS,
    PORTFOLIO_KEYS,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_performance_boundary_check(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    warnings: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    forbidden = _forbidden_artifacts_present(paths, as_of_date)
    blocking = list(blocking_reasons)
    if forbidden:
        blocking.append("forbidden_artifacts_present")
    return {
        "boundary_id": "A-SHARE-MULTI-DAY-PERFORMANCE-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **PERFORMANCE_BOUNDARY,
        "forbidden_artifacts_present": forbidden,
        "forbidden_wording_positive_hits": [],
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
    }


def build_performance_manifest(
    *,
    paths: ProjectPaths,
    config,
    generated_at: str,
    artifacts: dict[str, Path],
    data_availability: dict[str, Any],
    boundary_check: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-MULTI-DAY-PERFORMANCE-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "generated_at": generated_at,
        "mode": config.mode,
        "portfolio_ids": [PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS],
        "benchmark_ids": list(BENCHMARK_IDS),
        "observation_counts": data_availability.get("portfolio_observation_counts", {}),
        "sufficient_history": bool(data_availability.get("sufficient_history")),
        "first_day_initialization": int(data_availability.get("portfolio_observation_count") or 0) == 1,
        "performance_not_yet_observed": not bool(data_availability.get("sufficient_history")),
        "output_artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        "source_artifacts": {
            "tracking": f"data/equity_portfolio_tracking/daily/{config.as_of_date}",
            "workflow": f"data/equity_workflows/daily/{config.as_of_date}",
            "benchmark": f"data/equity_benchmarks/daily/{config.as_of_date}",
            "price_panels": "data/equity_market/history",
        },
        "boundary": {key: boundary_check.get(key) for key in PERFORMANCE_BOUNDARY},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        **PERFORMANCE_FLAGS,
    }


def build_performance_summary(
    *,
    config,
    nav_series: dict[str, Any],
    return_series: dict[str, Any],
    drawdown_series: dict[str, Any],
    relative_series: dict[str, Any],
    data_availability: dict[str, Any],
    boundary_check: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    portfolios: dict[str, Any] = {}
    nav_latest = _latest_by_portfolio(nav_series.get("records", []))
    return_latest = _latest_by_portfolio(return_series.get("records", []))
    drawdown_latest = _latest_by_portfolio(drawdown_series.get("records", []))
    for key in PORTFOLIO_KEYS:
        portfolio_id = PORTFOLIO_IDS[key]
        portfolios[portfolio_id] = {
            "nav": nav_latest.get(portfolio_id, {}).get("nav"),
            "daily_return": return_latest.get(portfolio_id, {}).get("daily_return"),
            "cumulative_return": return_latest.get(portfolio_id, {}).get("cumulative_return"),
            "drawdown": drawdown_latest.get(portfolio_id, {}).get("drawdown"),
            "max_drawdown": drawdown_latest.get(portfolio_id, {}).get("max_drawdown"),
            "holding_count": nav_latest.get(portfolio_id, {}).get("holding_count"),
            "benchmark_relative_status": relative_series.get("comparison_status", {}).get(portfolio_id, {}),
        }
    sufficient = bool(data_availability.get("sufficient_history"))
    return {
        "summary_id": "A-SHARE-MULTI-DAY-PERFORMANCE-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "mode": config.mode,
        "portfolio_ids": [PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS],
        "benchmark_ids": list(BENCHMARK_IDS),
        "portfolio_observation_count": data_availability.get("portfolio_observation_count"),
        "minimum_required_observations": config.minimum_required_observations,
        "sufficient_history": sufficient,
        "insufficient_history": not sufficient,
        "multi_day_performance_available": sufficient,
        "first_day_initialization": int(data_availability.get("portfolio_observation_count") or 0) == 1,
        "performance_not_yet_observed": not sufficient,
        "portfolios": portfolios,
        "source_trace_summary": "v0.7.8 tracking, v0.7.9 workflow, and v0.7.10 benchmark artifacts are traced.",
        "boundary_overall_passed": boundary_check.get("overall_passed"),
        "warnings": sorted(set(warnings)),
        "disclaimer": "Research-only virtual tracking output. It is not investment advice, not an order instruction, and not a profit guarantee.",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        **PERFORMANCE_FLAGS,
        "boundary": {key: boundary_check.get(key) for key in PERFORMANCE_BOUNDARY},
    }


def _latest_by_portfolio(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in sorted(records, key=lambda item: (item.get("portfolio_id"), item.get("as_of_date"))):
        latest[str(row.get("portfolio_id"))] = row
    return latest


def _forbidden_artifacts_present(paths: ProjectPaths, as_of_date: str) -> list[str]:
    hits = []
    scoped = [item.format(as_of_date=as_of_date) for item in FORBIDDEN_DATE_SCOPED_ARTIFACTS]
    for item in scoped:
        path = paths.project_root / item
        if path.exists():
            hits.append(relative(path, paths.project_root))
    scoped_dirs = [
        paths.data_dir / "equity_performance" / "daily" / as_of_date,
        paths.outputs_dir / "equity_performance" / "daily" / as_of_date,
    ]
    for directory in scoped_dirs:
        for name in FORBIDDEN_EXPLICIT_FILES:
            path = directory / name
            if path.exists():
                hits.append(relative(path, paths.project_root))
    for name in FORBIDDEN_EXPLICIT_FILES:
        path = paths.project_root / name
        if path.exists():
            hits.append(relative(path, paths.project_root))
    return sorted(set(hits))
