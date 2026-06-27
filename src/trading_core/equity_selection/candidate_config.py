"""Configuration for v0.7.5 A-share candidate generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


TARGET_VERSION = "v0.7.5-a-share-candidate-generation-system"
RECOMMENDED_NEXT_VERSION = "v0.7.6-a-share-virtual-portfolio-construction"
REMEDIATION_VERSION = "v0.7.5.1-a-share-candidate-generation-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

CANDIDATE_BOUNDARY = {
    "candidate_generation_only": True,
    "scores_generated_upstream": True,
    "candidates_generated": True,
    "watchlists_generated": True,
    "virtual_portfolio_generated": False,
    "buy_sell_signals_generated": False,
    "order_preview_generated": False,
    "official_forward_dry_run_status_unchanged": True,
    "day2_executed": False,
    "run_daily_called": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
}

CANDIDATE_FILES = {
    "candidate_generation_config": "candidate_generation_config.json",
    "long_candidates_json": "long_candidates.json",
    "long_candidates_parquet": "long_candidates.parquet",
    "mid_candidates_json": "mid_candidates.json",
    "mid_candidates_parquet": "mid_candidates.parquet",
    "short_candidates_json": "short_candidates.json",
    "short_candidates_parquet": "short_candidates.parquet",
    "extended_watch_pool_json": "extended_watch_pool.json",
    "extended_watch_pool_parquet": "extended_watch_pool.parquet",
    "multi_horizon_candidates": "multi_horizon_candidates.json",
    "risk_downgraded_candidates": "risk_downgraded_candidates.json",
    "candidate_reason_breakdown": "candidate_reason_breakdown.json",
    "candidate_generation_summary": "candidate_generation_summary.json",
    "candidate_manifest": "candidate_manifest.json",
}

CANDIDATE_REPORTS = {
    "long_candidates_report": "LONG_CANDIDATES.md",
    "mid_candidates_report": "MID_CANDIDATES.md",
    "short_candidates_report": "SHORT_CANDIDATES.md",
    "multi_horizon_candidates_report": "MULTI_HORIZON_CANDIDATES.md",
    "risk_downgraded_candidates_report": "RISK_DOWNGRADED_CANDIDATES.md",
    "candidate_generation_summary_report": "CANDIDATE_GENERATION_SUMMARY.md",
}


@dataclass(frozen=True)
class CandidateGenerationConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    long_count: int = 30
    mid_count: int = 30
    short_count: int = 30
    extended_count: int = 100
    long_percentile_min: float = 90.0
    mid_percentile_min: float = 90.0
    short_percentile_min: float = 90.0
    multi_horizon_percentile_min: float = 85.0
    composite_percentile_min: float = 95.0
    long_risk_percentile_min: float = 40.0
    long_risk_score_min: float = 45.0
    long_liquidity_percentile_min: float = 35.0
    long_liquidity_score_min: float = 45.0
    mid_risk_percentile_min: float = 35.0
    mid_risk_score_min: float = 40.0
    mid_liquidity_percentile_min: float = 40.0
    mid_liquidity_score_min: float = 45.0
    mid_industry_score_min_percentile: float = 20.0
    short_risk_percentile_min: float = 30.0
    short_risk_score_min: float = 35.0
    short_liquidity_percentile_min: float = 50.0
    short_liquidity_score_min: float = 50.0
    severe_overheat_component_max: float = 25.0
    minimum_fundamental_confidence: float = 0.40
    minimum_candidate_confidence: float = 0.40
    risk_downgrade_percentile_min: float = 90.0
    risk_downgrade_risk_score_max: float = 35.0
    risk_downgrade_liquidity_score_max: float = 40.0

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "target_version": TARGET_VERSION,
            "selection_method": "rank_and_percentile_relative_selection",
            "score_percentile_convention": "0_to_100",
            "confidence_convention": "0_to_1",
            "boundary": dict(CANDIDATE_BOUNDARY),
        }


def validate_candidate_config(config: CandidateGenerationConfig) -> list[str]:
    issues: list[str] = []
    for field in ["long_count", "mid_count", "short_count", "extended_count"]:
        if int(getattr(config, field)) <= 0:
            issues.append(f"{field} must be positive")
    for field in [
        "long_percentile_min",
        "mid_percentile_min",
        "short_percentile_min",
        "multi_horizon_percentile_min",
        "composite_percentile_min",
    ]:
        value = float(getattr(config, field))
        if value < 0.0 or value > 100.0:
            issues.append(f"{field} must be within 0-100")
    return issues
