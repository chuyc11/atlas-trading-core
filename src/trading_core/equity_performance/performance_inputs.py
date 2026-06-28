"""Input loading for v0.7.11 A-share performance tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trading_core.equity_performance.performance_config import (
    BENCHMARK_IDS,
    DEFAULT_AS_OF_DATE,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


TRACKING_FILES = {
    "tracking_config": "tracking_config.json",
    "long_paper_ledger": "long_paper_ledger.json",
    "mid_paper_ledger": "mid_paper_ledger.json",
    "short_paper_ledger": "short_paper_ledger.json",
    "long_holdings_snapshot": "long_holdings_snapshot.json",
    "mid_holdings_snapshot": "mid_holdings_snapshot.json",
    "short_holdings_snapshot": "short_holdings_snapshot.json",
    "portfolio_nav_snapshot": "portfolio_nav_snapshot.json",
    "portfolio_performance_snapshot": "portfolio_performance_snapshot.json",
    "portfolio_drawdown_snapshot": "portfolio_drawdown_snapshot.json",
    "portfolio_exposure_snapshot": "portfolio_exposure_snapshot.json",
    "tracking_manifest": "tracking_manifest.json",
    "tracking_source_trace": "tracking_source_trace.json",
    "tracking_summary": "tracking_summary.json",
}

BENCHMARK_FILES = {
    "benchmark_config": "benchmark_config.json",
    "benchmark_data_availability": "benchmark_data_availability.json",
    "benchmark_return_snapshot": "benchmark_return_snapshot.json",
    "benchmark_nav_snapshot": "benchmark_nav_snapshot.json",
    "portfolio_benchmark_comparison": "portfolio_benchmark_comparison.json",
    "relative_performance_snapshot": "relative_performance_snapshot.json",
    "benchmark_source_trace": "benchmark_source_trace.json",
    "benchmark_manifest": "benchmark_manifest.json",
    "benchmark_boundary_check": "benchmark_boundary_check.json",
    "benchmark_summary": "benchmark_summary.json",
}

WORKFLOW_FILES = {
    "workflow_config": "workflow_config.json",
    "workflow_run_manifest": "workflow_run_manifest.json",
    "workflow_stage_manifest": "workflow_stage_manifest.json",
    "workflow_source_trace": "workflow_source_trace.json",
    "workflow_boundary_check": "workflow_boundary_check.json",
    "workflow_summary": "workflow_summary.json",
}


@dataclass(frozen=True)
class PerformanceInputs:
    as_of_date: str
    tracking_artifacts: dict[str, Any]
    benchmark_artifacts: dict[str, Any]
    workflow_artifacts: dict[str, Any]
    audits: dict[str, Any]
    input_paths: dict[str, Path]
    price_panel_paths: dict[str, Path]

    @property
    def price_panels_available(self) -> dict[str, bool]:
        return {key: path.exists() for key, path in self.price_panel_paths.items()}


def load_performance_inputs(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
) -> PerformanceInputs:
    paths = default_paths(paths)
    tracking_paths = _daily_paths(paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date, TRACKING_FILES)
    benchmark_paths = _daily_paths(paths.data_dir / "equity_benchmarks" / "daily" / as_of_date, BENCHMARK_FILES)
    workflow_paths = _daily_paths(paths.data_dir / "equity_workflows" / "daily" / as_of_date, WORKFLOW_FILES)
    audit_paths = {
        "tracking_audit": paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_tracking_audit.json",
        "workflow_audit": paths.data_dir / "equity_data_quality" / "a_share_daily_workflow_audit.json",
        "benchmark_audit": paths.data_dir / "equity_data_quality" / "a_share_benchmark_comparison_audit.json",
    }
    price_panel_paths = {
        "adjusted_price_history_panel": paths.data_dir / "equity_market" / "history" / "adjusted_price_history_panel.parquet",
        "daily_price_history_panel": paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet",
    }
    missing = [key for key, path in {**tracking_paths, **benchmark_paths, **workflow_paths, **audit_paths}.items() if not path.exists()]
    if missing:
        raise ValueError(f"missing required performance inputs: {missing}")

    tracking_artifacts = {key: _load_any(path) for key, path in tracking_paths.items()}
    benchmark_artifacts = {key: _load_any(path) for key, path in benchmark_paths.items()}
    workflow_artifacts = {key: _load_any(path) for key, path in workflow_paths.items()}
    audits = {key: _load_any(path) for key, path in audit_paths.items()}
    baseline_issues = validate_v0710_baseline(benchmark_artifacts=benchmark_artifacts, audits=audits)
    if baseline_issues:
        raise ValueError("; ".join(baseline_issues))
    return PerformanceInputs(
        as_of_date=as_of_date,
        tracking_artifacts=tracking_artifacts,
        benchmark_artifacts=benchmark_artifacts,
        workflow_artifacts=workflow_artifacts,
        audits=audits,
        input_paths={**tracking_paths, **benchmark_paths, **workflow_paths, **audit_paths},
        price_panel_paths=price_panel_paths,
    )


def validate_v0710_baseline(*, benchmark_artifacts: dict[str, Any], audits: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    benchmark_audit = audits.get("benchmark_audit", {})
    if benchmark_audit.get("overall_passed") is not True:
        issues.append("benchmark audit overall_passed must be true")
    if benchmark_audit.get("blocking_reasons") != []:
        issues.append("benchmark audit blocking_reasons must be []")
    if benchmark_audit.get("recommended_next_version") != "v0.7.11-a-share-multi-day-portfolio-performance-tracking":
        issues.append("benchmark audit recommended_next_version must point to v0.7.11")
    availability = benchmark_artifacts.get("benchmark_data_availability", {})
    if availability.get("placeholder_benchmarks_used") not in ([], None):
        issues.append("placeholder benchmarks must not be used")
    statuses = {row.get("benchmark_id"): row.get("status") for row in availability.get("benchmarks", [])}
    if set(statuses) != set(BENCHMARK_IDS):
        issues.append("all required benchmark ids must be present")
    unavailable = [key for key, status in statuses.items() if status != "available"]
    if unavailable:
        issues.append(f"all benchmark ids must be available: {unavailable}")
    if benchmark_artifacts.get("benchmark_summary", {}).get("recommended_next_version") != TARGET_VERSION:
        issues.append("benchmark summary recommended_next_version must point to v0.7.11")
    return issues


def load_tracking_snapshot_for_date(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    base = paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date
    required = _daily_paths(base, TRACKING_FILES)
    missing = [key for key, path in required.items() if not path.exists()]
    if missing:
        raise ValueError(f"missing tracking snapshot for {as_of_date}: {missing}")
    return {key: _load_any(path) for key, path in required.items()}


def available_tracking_snapshot_dates(paths: ProjectPaths, *, start_date: str, as_of_date: str) -> list[str]:
    base = paths.data_dir / "equity_portfolio_tracking" / "daily"
    if not base.exists():
        return []
    dates = []
    for child in base.iterdir():
        if child.is_dir() and start_date <= child.name <= as_of_date and (child / "portfolio_nav_snapshot.json").exists():
            dates.append(child.name)
    return sorted(set(dates))


def _daily_paths(base: Path, files: dict[str, str]) -> dict[str, Path]:
    return {key: base / filename for key, filename in files.items()}


def _load_any(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
