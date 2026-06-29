"""Benchmark summary card."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.equity_owner_dashboard.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_benchmark_summary_card(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    summary = load_json(paths.data_dir / "equity_benchmarks" / "daily" / as_of_date / "benchmark_summary.json")
    availability = summary.get("benchmark_availability", {})
    placeholders = summary.get("placeholder_benchmarks_used", [])
    return {
        "card_id": "BENCHMARK_SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "status": "available" if summary else "missing_optional",
        "CSI300_status": availability.get("CSI300"),
        "CSI500_status": availability.get("CSI500"),
        "CSI1000_status": availability.get("CSI1000"),
        "CASH_status": availability.get("CASH"),
        "EQUAL_WEIGHT_STRICT_TRADABLE_status": availability.get("EQUAL_WEIGHT_STRICT_TRADABLE"),
        "EQUAL_WEIGHT_CANDIDATE_POOL_status": availability.get("EQUAL_WEIGHT_CANDIDATE_POOL"),
        "first_day_initialization": bool(summary.get("first_day_initialization")),
        "performance_not_yet_observed": bool(summary.get("performance_not_yet_observed")),
        "relative_performance_available": bool(summary.get("relative_performance_available")),
        "placeholder_benchmarks_used": placeholders,
        "limited_history_status": "limited_history" if summary.get("limited_history_flagged") else "available",
        "warnings": list(summary.get("warnings", [])) + (["placeholder_benchmarks_used"] if placeholders else []),
    }
