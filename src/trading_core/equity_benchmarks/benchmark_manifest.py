"""Manifest, summary, and boundary helpers for benchmark comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_benchmarks.benchmark_config import (
    BENCHMARK_BOUNDARY,
    BENCHMARK_FLAGS,
    BENCHMARK_IDS,
    FORBIDDEN_ARTIFACTS,
    PORTFOLIO_IDS,
    PORTFOLIO_KEYS,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_benchmark_boundary_check(*, paths: ProjectPaths, as_of_date: str, warnings: list[str], blocking_reasons: list[str]) -> dict[str, Any]:
    forbidden = _forbidden_artifacts_present(paths, as_of_date)
    blocking = list(blocking_reasons)
    if forbidden:
        blocking.append("forbidden_artifacts_present")
    return {
        "boundary_id": "A-SHARE-BENCHMARK-COMPARISON-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **BENCHMARK_BOUNDARY,
        "forbidden_artifacts_present": forbidden,
        "forbidden_wording_positive_hits": [],
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
    }


def build_benchmark_manifest(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    generated_at: str,
    artifacts: dict[str, Path],
    availability: list[dict[str, Any]],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    status = {
        row["benchmark_id"]: row["status"]
        for row in availability
    }
    return {
        "manifest_id": "A-SHARE-BENCHMARK-COMPARISON-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "benchmark_ids": list(BENCHMARK_IDS),
        "portfolio_ids": [PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS],
        "output_artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        "source_artifacts": {
            "workflow": f"data/equity_workflows/daily/{as_of_date}",
            "tracking": f"data/equity_portfolio_tracking/daily/{as_of_date}",
            "selection": f"data/equity_selection/daily/{as_of_date}",
            "portfolios": f"data/equity_portfolios/daily/{as_of_date}",
            "price_panels": "data/equity_market/history",
        },
        "benchmark_availability": status,
        "comparison_status": {
            row["portfolio_id"]: row["comparison_status"]
            for row in comparison.get("comparisons", [])
        },
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        **BENCHMARK_FLAGS,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_benchmark_summary(
    *,
    as_of_date: str,
    availability: list[dict[str, Any]],
    comparison: dict[str, Any],
    boundary_check: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    status = {row["benchmark_id"]: row["status"] for row in availability}
    return {
        "summary_id": "A-SHARE-BENCHMARK-COMPARISON-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_ids": list(BENCHMARK_IDS),
        "benchmark_availability": status,
        "portfolio_ids": sorted({row["portfolio_id"] for row in comparison.get("comparisons", [])}),
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        "relative_performance_available": False,
        "limited_history_flagged": True,
        "placeholder_benchmarks_used": [row["benchmark_id"] for row in availability if row.get("is_placeholder")],
        "boundary_overall_passed": boundary_check.get("overall_passed"),
        "warnings": sorted(set(warnings)),
        **BENCHMARK_FLAGS,
        "boundary": dict(BENCHMARK_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _forbidden_artifacts_present(paths: ProjectPaths, as_of_date: str) -> list[str]:
    hits = []
    explicit_files = [
        "BROKER_ORDER.json",
        "REAL_ORDER.json",
        "ORDER_PREVIEW.md",
        "BUY_LIST.md",
        "SELL_LIST.md",
        f"data/orders/orders-{as_of_date}.jsonl",
        f"data/trades/trades-{as_of_date}.jsonl",
        f"data/accounts/account-{as_of_date}.json",
        f"outputs/orders/orders-{as_of_date}.md",
        f"outputs/trades/trades-{as_of_date}.md",
        f"outputs/accounts/account-{as_of_date}.md",
    ]
    benchmark_dirs = [
        paths.data_dir / "equity_benchmarks" / "daily" / as_of_date,
        paths.outputs_dir / "equity_benchmarks" / "daily" / as_of_date,
    ]
    for directory in benchmark_dirs:
        for name in ["BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"]:
            path = directory / name
            if path.exists():
                hits.append(relative(path, paths.project_root))
    for item in explicit_files:
        path = paths.project_root / item
        if path.exists():
            hits.append(relative(path, paths.project_root))
    return sorted(set(hits))
