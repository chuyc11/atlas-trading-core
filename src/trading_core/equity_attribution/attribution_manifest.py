"""Manifest, boundary, and summary builders for attribution diagnostics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_attribution.attribution_config import (
    ATTRIBUTION_BOUNDARY,
    BENCHMARK_IDS,
    PORTFOLIO_IDS,
    PORTFOLIO_KEYS,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_attribution_boundary_check(*, as_of_date: str, warnings: list[str] | None = None, blocking_reasons: list[str] | None = None) -> dict[str, Any]:
    blocking = blocking_reasons or []
    return {
        "boundary_id": "A-SHARE-PERFORMANCE-ATTRIBUTION-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **ATTRIBUTION_BOUNDARY,
        "forbidden_artifacts_present": [],
        "forbidden_wording_positive_hits": [],
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings or [],
    }


def build_attribution_manifest(*, paths: ProjectPaths, config: Any, generated_at: str, artifacts: dict[str, Path], data_availability: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-PERFORMANCE-ATTRIBUTION-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "generated_at": generated_at,
        "mode": config.mode,
        "portfolio_ids": [PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS],
        "benchmark_ids": list(BENCHMARK_IDS),
        "structural_diagnostics_available": True,
        "realized_performance_attribution_available": False,
        "limited_history": True,
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        "output_artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        "source_artifacts": {},
        "boundary": boundary,
        "data_availability": {
            "portfolio_observation_counts": data_availability.get("portfolio_observation_counts"),
            "all_required_sources_available": data_availability.get("all_required_sources_available"),
        },
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_attribution_summary(*, config: Any, holding: dict[str, Any], industry: dict[str, Any], score_bucket: dict[str, Any], risk_bucket: dict[str, Any], liquidity_bucket: dict[str, Any], benchmark_relative: dict[str, Any], concentration: dict[str, Any], boundary: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-PERFORMANCE-ATTRIBUTION-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "portfolio_ids": [PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS],
        "benchmark_ids": list(BENCHMARK_IDS),
        "limited_history": True,
        "structural_diagnostics_available": True,
        "realized_performance_attribution_available": False,
        "performance_not_yet_observed": True,
        "holding_count": len(holding.get("records", [])),
        "portfolio_weight_sums": holding.get("portfolio_weight_sums", {}),
        "industry_portfolios": list(industry.get("portfolios", {})),
        "score_bucket_edges": score_bucket.get("bucket_edges"),
        "risk_downgraded_symbols_in_portfolio": risk_bucket.get("risk_downgraded_symbols_in_portfolio", []),
        "liquidity_portfolios": list(liquidity_bucket.get("portfolios", {})),
        "benchmark_relative_records": len(benchmark_relative.get("records", [])),
        "diagnostic_flags": {pid: row.get("diagnostic_flags", {}) for pid, row in concentration.get("portfolios", {}).items()},
        "boundary": boundary,
        "warnings": warnings,
        "disclaimer": "Structural attribution diagnostics are research-only virtual outputs and are not investment advice.",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
