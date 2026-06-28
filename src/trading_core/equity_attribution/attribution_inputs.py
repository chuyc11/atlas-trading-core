"""Input loading for v0.7.12 attribution diagnostics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trading_core.equity_attribution.attribution_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


PERFORMANCE_FILES = {
    "performance_config": "performance_config.json",
    "performance_data_availability": "performance_data_availability.json",
    "portfolio_nav_series": "portfolio_nav_series.json",
    "portfolio_return_series": "portfolio_return_series.json",
    "portfolio_drawdown_series": "portfolio_drawdown_series.json",
    "portfolio_relative_performance_series": "portfolio_relative_performance_series.json",
    "portfolio_benchmark_relative_series": "portfolio_benchmark_relative_series.json",
    "holding_mark_to_market_series": "holding_mark_to_market_series.json",
    "performance_metric_snapshot": "performance_metric_snapshot.json",
    "performance_limitations": "performance_limitations.json",
    "performance_append_log": "performance_append_log.json",
    "performance_source_trace": "performance_source_trace.json",
    "performance_manifest": "performance_manifest.json",
    "performance_boundary_check": "performance_boundary_check.json",
    "performance_summary": "performance_summary.json",
}
BENCHMARK_FILES = {
    "benchmark_config": "benchmark_config.json",
    "benchmark_data_availability": "benchmark_data_availability.json",
    "benchmark_return_snapshot": "benchmark_return_snapshot.json",
    "benchmark_nav_snapshot": "benchmark_nav_snapshot.json",
    "portfolio_benchmark_comparison": "portfolio_benchmark_comparison.json",
    "relative_performance_snapshot": "relative_performance_snapshot.json",
    "benchmark_manifest": "benchmark_manifest.json",
    "benchmark_boundary_check": "benchmark_boundary_check.json",
    "benchmark_universe_snapshot": "benchmark_universe_snapshot.json",
}
TRACKING_FILES = {
    "long_holdings_snapshot": "long_holdings_snapshot.json",
    "mid_holdings_snapshot": "mid_holdings_snapshot.json",
    "short_holdings_snapshot": "short_holdings_snapshot.json",
    "portfolio_exposure_snapshot": "portfolio_exposure_snapshot.json",
    "tracking_summary": "tracking_summary.json",
    "tracking_manifest": "tracking_manifest.json",
}
PORTFOLIO_FILES = {
    "long_virtual_portfolio": "long_virtual_portfolio.json",
    "mid_virtual_portfolio": "mid_virtual_portfolio.json",
    "short_virtual_portfolio": "short_virtual_portfolio.json",
    "portfolio_weight_summary": "portfolio_weight_summary.json",
    "portfolio_industry_exposure": "portfolio_industry_exposure.json",
    "portfolio_risk_liquidity_summary": "portfolio_risk_liquidity_summary.json",
}
CANDIDATE_FILES = {
    "long_candidates": "long_candidates.json",
    "mid_candidates": "mid_candidates.json",
    "short_candidates": "short_candidates.json",
    "multi_horizon_candidates": "multi_horizon_candidates.json",
    "risk_downgraded_candidates": "risk_downgraded_candidates.json",
    "candidate_reason_breakdown": "candidate_reason_breakdown.json",
    "candidate_manifest": "candidate_manifest.json",
    "strict_tradable_universe": "strict_tradable_universe.json",
    "excluded_universe": "excluded_universe.json",
}
SCORE_FILES = {
    "score_manifest": "score_manifest.json",
    "score_config": "score_config.json",
    "scoring_summary": "scoring_summary.json",
    "composite_scores": "composite_scores.parquet",
    "horizon_scores": "horizon_scores.parquet",
    "risk_liquidity_industry_fundamental_scores": "risk_liquidity_industry_fundamental_scores.parquet",
}


@dataclass(frozen=True)
class AttributionInputs:
    as_of_date: str
    performance: dict[str, Any]
    benchmark: dict[str, Any]
    tracking: dict[str, Any]
    portfolios: dict[str, Any]
    candidates: dict[str, Any]
    scores: dict[str, Any]
    audits: dict[str, Any]
    input_paths: dict[str, Path]

    @property
    def holdings_by_key(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "long": list(self.tracking.get("long_holdings_snapshot", {}).get("holdings", [])),
            "mid": list(self.tracking.get("mid_holdings_snapshot", {}).get("holdings", [])),
            "short": list(self.tracking.get("short_holdings_snapshot", {}).get("holdings", [])),
        }


def load_attribution_inputs(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> AttributionInputs:
    paths = default_paths(paths)
    performance_paths = _daily_paths(paths.data_dir / "equity_performance" / "daily" / as_of_date, PERFORMANCE_FILES)
    benchmark_paths = _daily_paths(paths.data_dir / "equity_benchmarks" / "daily" / as_of_date, BENCHMARK_FILES)
    tracking_paths = _daily_paths(paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date, TRACKING_FILES)
    portfolio_paths = _daily_paths(paths.data_dir / "equity_portfolios" / "daily" / as_of_date, PORTFOLIO_FILES)
    candidate_paths = _daily_paths(paths.data_dir / "equity_selection" / "daily" / as_of_date, CANDIDATE_FILES)
    score_paths = _daily_paths(paths.data_dir / "equity_scores" / "daily" / as_of_date, SCORE_FILES)
    audit_paths = {
        "performance_audit": paths.data_dir / "equity_data_quality" / "a_share_multi_day_performance_audit.json",
        "benchmark_audit": paths.data_dir / "equity_data_quality" / "a_share_benchmark_comparison_audit.json",
        "tracking_audit": paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_tracking_audit.json",
        "portfolio_audit": paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_construction_audit.json",
        "candidate_audit": paths.data_dir / "equity_data_quality" / "a_share_candidate_generation_audit.json",
        "scoring_audit": paths.data_dir / "equity_data_quality" / "a_share_scoring_audit.json",
    }
    required_paths = {**performance_paths, **benchmark_paths, **tracking_paths, **portfolio_paths, **candidate_paths, **score_paths, **audit_paths}
    missing = [key for key, path in required_paths.items() if not path.exists()]
    if missing:
        raise ValueError(f"missing required attribution inputs: {missing}")
    performance = {key: _load_json(path) for key, path in performance_paths.items()}
    audits = {key: _load_json(path) for key, path in audit_paths.items()}
    baseline_issues = validate_v0711_baseline(performance=performance, audits=audits)
    if baseline_issues:
        raise ValueError("; ".join(baseline_issues))
    return AttributionInputs(
        as_of_date=as_of_date,
        performance=performance,
        benchmark={key: _load_json(path) for key, path in benchmark_paths.items()},
        tracking={key: _load_json(path) for key, path in tracking_paths.items()},
        portfolios={key: _load_json(path) for key, path in portfolio_paths.items()},
        candidates={key: _load_json(path) for key, path in candidate_paths.items()},
        scores={key: {"path": str(path), "exists": path.exists()} if path.suffix == ".parquet" else _load_json(path) for key, path in score_paths.items()},
        audits=audits,
        input_paths=required_paths,
    )


def validate_v0711_baseline(*, performance: dict[str, Any], audits: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    audit = audits.get("performance_audit", {})
    if audit.get("overall_passed") is not True:
        issues.append("v0.7.11 performance audit overall_passed must be true")
    if audit.get("blocking_reasons") != []:
        issues.append("v0.7.11 performance audit blocking_reasons must be []")
    if audit.get("recommended_next_version") != "v0.7.12-a-share-performance-attribution-and-risk-diagnostics":
        issues.append("v0.7.11 performance audit recommended_next_version must point to v0.7.12")
    if performance.get("performance_summary", {}).get("recommended_next_version") != "v0.7.12-a-share-performance-attribution-and-risk-diagnostics":
        issues.append("performance summary recommended_next_version must point to v0.7.12")
    if audits.get("benchmark_audit", {}).get("recommended_next_version") != "v0.7.11-a-share-multi-day-portfolio-performance-tracking":
        issues.append("benchmark audit must be the v0.7.11 baseline input")
    if RECOMMENDED_NEXT_VERSION != "v0.8.0-a-share-daily-data-refresh-and-provider-hardening":
        issues.append("v0.7.12 recommended next version must point to v0.8.0")
    return issues


def _daily_paths(base: Path, files: dict[str, str]) -> dict[str, Path]:
    return {key: base / filename for key, filename in files.items()}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
