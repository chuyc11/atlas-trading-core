"""Configuration for A-share long/mid/short scoring."""

from __future__ import annotations

from typing import Any


TARGET_VERSION = "v0.7.4-a-share-long-mid-short-scoring-system"
RECOMMENDED_NEXT_VERSION = "v0.7.5-a-share-candidate-generation-system"
REMEDIATION_VERSION = "v0.7.4.1-a-share-scoring-system-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

SCORE_BOUNDARY = {
    "scoring_only": True,
    "scores_generated": True,
    "candidates_generated": False,
    "watchlists_generated": False,
    "virtual_portfolio_generated": False,
    "official_forward_dry_run_status_unchanged": True,
    "day2_executed": False,
    "run_daily_called": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
}

SCORE_FILES = {
    "score_config": "score_config.json",
    "risk_liquidity_industry_fundamental_scores": "risk_liquidity_industry_fundamental_scores.parquet",
    "horizon_scores": "horizon_scores.parquet",
    "composite_scores": "composite_scores.parquet",
    "score_component_breakdown": "score_component_breakdown.parquet",
    "score_distribution": "score_distribution.json",
    "score_manifest": "score_manifest.json",
    "scoring_summary": "scoring_summary.json",
}

SCORE_COLUMNS = [
    "LongScore",
    "MidScore",
    "ShortScore",
    "RiskScore",
    "LiquidityScore",
    "IndustryScore",
    "FundamentalScore",
    "CompositeOpportunityScore",
]

COMMON_COLUMNS = [
    "as_of_date",
    "symbol",
    "name",
    "exchange",
    "board",
    "industry_level_1",
    "industry_level_2",
]

FEATURE_DIRECTIONS = {
    "volatility_20d": "lower",
    "volatility_60d": "lower",
    "volatility_120d": "lower",
    "volatility_250d": "lower",
    "downside_volatility_60d": "lower",
    "downside_volatility_120d": "lower",
    "max_drawdown_20d": "magnitude_lower",
    "max_drawdown_60d": "magnitude_lower",
    "max_drawdown_120d": "magnitude_lower",
    "max_drawdown_250d": "magnitude_lower",
    "max_drawdown_3y": "magnitude_lower",
    "var_95_20d": "magnitude_lower",
    "var_95_60d": "magnitude_lower",
    "expected_shortfall_95_60d": "magnitude_lower",
    "large_drop_days_60d": "lower",
    "large_gap_days_60d": "lower",
    "limit_up_days_60d": "lower",
    "limit_down_days_60d": "lower",
    "avg_amount_5d": "higher",
    "avg_amount_20d": "higher",
    "avg_amount_60d": "higher",
    "avg_volume_20d": "higher",
    "avg_volume_60d": "higher",
    "turnover_rate_20d_avg": "moderate",
    "turnover_rate_60d_avg": "moderate",
    "amount_stability_20d": "higher",
    "amount_stability_60d": "higher",
    "zero_volume_days_60d": "lower",
    "effective_trading_days_20d": "higher",
    "effective_trading_days_60d": "higher",
    "estimated_slippage_proxy_20d": "lower",
    "estimated_slippage_proxy_60d": "lower",
    "industry_return_5d": "higher",
    "industry_return_20d": "higher",
    "industry_return_60d": "higher",
    "industry_return_120d": "higher",
    "industry_return_250d": "higher",
    "industry_relative_strength_20d": "higher",
    "industry_relative_strength_60d": "higher",
    "industry_relative_strength_120d": "higher",
    "industry_relative_strength_250d": "higher",
    "stock_percentile_in_industry_by_return_20d": "higher",
    "stock_percentile_in_industry_by_return_60d": "higher",
    "stock_percentile_in_industry_by_return_120d": "higher",
    "industry_member_count": "higher",
    "pe_ttm": "moderate",
    "pb": "moderate",
    "ps_ttm": "moderate",
    "dv_ttm": "higher",
    "pe_ttm_percentile_3y": "moderate",
    "pb_percentile_3y": "moderate",
    "ps_ttm_percentile_3y": "moderate",
    "total_mv": "higher",
    "circ_mv": "higher",
    "revenue_growth_yoy": "higher",
    "net_profit_growth_yoy": "higher",
    "roe_latest": "higher",
    "roe_ttm": "higher",
    "gross_margin_latest": "higher",
    "net_margin_latest": "higher",
    "operating_cash_flow_latest": "higher",
    "debt_to_asset_latest": "lower",
    "eps_latest": "higher",
    "bps_latest": "higher",
    "financial_report_age_days": "lower",
    "financial_quarters_available": "higher",
    "return_1d": "higher",
    "return_3d": "higher",
    "return_5d": "higher",
    "return_10d": "higher",
    "return_20d": "higher",
    "overheat_return_20d": "moderate",
    "return_60d": "higher",
    "return_120d": "higher",
    "return_250d": "higher",
    "return_3y": "higher",
    "return_5y": "higher",
    "momentum_5d": "higher",
    "momentum_10d": "higher",
    "momentum_20d": "higher",
    "momentum_60d": "higher",
    "momentum_120d": "higher",
    "volume_change_5d": "higher",
    "amount_change_5d": "higher",
    "amount_change_20d": "higher",
    "close_to_20d_high": "higher",
    "close_to_20d_low": "higher",
    "breakout_20d_high": "boolean_higher",
    "drawdown_from_20d_high": "magnitude_lower",
    "reversal_from_20d_low": "higher",
    "gap_1d": "moderate",
    "intraday_range_1d": "lower",
    "amplitude_5d": "lower",
    "amplitude_20d": "lower",
    "ma_20": "higher",
    "ma_60": "higher",
    "ma_120": "higher",
    "ma_250": "higher",
    "close_to_ma_20": "higher",
    "close_to_ma_60": "higher",
    "close_to_ma_120": "higher",
    "close_to_ma_250": "higher",
    "ma_20_slope": "higher",
    "ma_60_slope": "higher",
    "ma_120_slope": "higher",
    "ma_250_slope": "higher",
    "trend_consistency_60d": "higher",
    "trend_consistency_120d": "higher",
    "long_trend_consistency_250d": "higher",
    "relative_strength_60d_vs_market": "higher",
    "relative_strength_120d_vs_market": "higher",
    "relative_strength_250d_vs_market": "higher",
    "relative_strength_60d_vs_industry": "higher",
    "relative_strength_120d_vs_industry": "higher",
    "relative_strength_250d_vs_industry": "higher",
    "volatility_adjusted_return_60d": "higher",
    "volatility_adjusted_return_120d": "higher",
    "annualized_return_250d": "higher",
    "annualized_volatility_250d": "lower",
    "calmar_250d": "higher",
}

COMPONENT_FIELDS = {
    "risk": {
        "volatility_component": ["volatility_20d", "volatility_60d", "volatility_120d", "volatility_250d"],
        "downside_component": ["downside_volatility_60d", "downside_volatility_120d"],
        "drawdown_component": ["max_drawdown_20d", "max_drawdown_60d", "max_drawdown_120d", "max_drawdown_250d"],
        "tail_loss_component": ["var_95_20d", "var_95_60d", "expected_shortfall_95_60d"],
        "event_risk_component": ["large_drop_days_60d", "large_gap_days_60d", "limit_up_days_60d", "limit_down_days_60d"],
    },
    "liquidity": {
        "amount_component": ["avg_amount_5d", "avg_amount_20d", "avg_amount_60d"],
        "volume_component": ["avg_volume_20d", "avg_volume_60d"],
        "turnover_component": ["turnover_rate_20d_avg", "turnover_rate_60d_avg"],
        "stability_component": ["amount_stability_20d", "amount_stability_60d"],
        "effective_days_component": ["effective_trading_days_20d", "effective_trading_days_60d"],
        "friction_component": ["zero_volume_days_60d", "estimated_slippage_proxy_20d", "estimated_slippage_proxy_60d"],
    },
    "industry": {
        "industry_return_component": ["industry_return_5d", "industry_return_20d", "industry_return_60d", "industry_return_120d", "industry_return_250d"],
        "industry_relative_strength_component": ["industry_relative_strength_20d", "industry_relative_strength_60d", "industry_relative_strength_120d", "industry_relative_strength_250d"],
        "stock_industry_position_component": ["stock_percentile_in_industry_by_return_20d", "stock_percentile_in_industry_by_return_60d", "stock_percentile_in_industry_by_return_120d"],
        "industry_depth_component": ["industry_member_count"],
    },
    "fundamental": {
        "growth_quality_component": ["revenue_growth_yoy", "net_profit_growth_yoy", "roe_latest", "roe_ttm", "gross_margin_latest", "net_margin_latest", "operating_cash_flow_latest", "eps_latest", "bps_latest", "dv_ttm"],
        "valuation_component": ["pe_ttm", "pb", "ps_ttm", "pe_ttm_percentile_3y", "pb_percentile_3y", "ps_ttm_percentile_3y"],
        "balance_sheet_component": ["debt_to_asset_latest"],
        "data_freshness_component": ["financial_report_age_days", "financial_quarters_available"],
        "size_stability_component": ["total_mv", "circ_mv"],
    },
    "long": {
        "long_trend_component": ["return_250d", "return_3y", "return_5y", "ma_250_slope", "close_to_ma_250", "annualized_return_250d", "relative_strength_250d_vs_market", "relative_strength_250d_vs_industry", "long_trend_consistency_250d", "calmar_250d"],
        "valuation_component": ["pe_ttm", "pb", "ps_ttm", "pe_ttm_percentile_3y", "pb_percentile_3y", "ps_ttm_percentile_3y"],
        "drawdown_control_component": ["max_drawdown_250d", "max_drawdown_3y", "annualized_volatility_250d"],
    },
    "mid": {
        "trend_component": ["return_20d", "return_60d", "return_120d", "momentum_60d", "momentum_120d", "ma_20_slope", "ma_60_slope", "ma_120_slope", "close_to_ma_20", "close_to_ma_60", "close_to_ma_120", "trend_consistency_60d", "trend_consistency_120d"],
        "relative_strength_component": ["relative_strength_60d_vs_market", "relative_strength_120d_vs_market", "relative_strength_60d_vs_industry", "relative_strength_120d_vs_industry"],
        "fundamental_improvement_component": ["revenue_growth_yoy", "net_profit_growth_yoy", "roe_latest", "roe_ttm"],
        "volatility_adjusted_return_component": ["volatility_adjusted_return_60d", "volatility_adjusted_return_120d"],
    },
    "short": {
        "short_momentum_component": ["return_1d", "return_3d", "return_5d", "return_10d", "return_20d", "momentum_5d", "momentum_10d", "momentum_20d"],
        "breakout_reversal_component": ["close_to_20d_high", "close_to_20d_low", "breakout_20d_high", "drawdown_from_20d_high", "reversal_from_20d_low"],
        "volume_amount_component": ["volume_change_5d", "amount_change_5d", "amount_change_20d"],
        "overheat_penalty_component": ["overheat_return_20d", "gap_1d", "intraday_range_1d", "amplitude_5d", "amplitude_20d", "limit_up_days_60d"],
    },
}

COMPONENT_WEIGHTS = {
    "risk": {
        "volatility_component": 0.30,
        "downside_component": 0.15,
        "drawdown_component": 0.25,
        "tail_loss_component": 0.20,
        "event_risk_component": 0.10,
    },
    "liquidity": {
        "amount_component": 0.30,
        "volume_component": 0.15,
        "turnover_component": 0.15,
        "stability_component": 0.15,
        "effective_days_component": 0.15,
        "friction_component": 0.10,
    },
    "industry": {
        "industry_return_component": 0.35,
        "industry_relative_strength_component": 0.35,
        "stock_industry_position_component": 0.20,
        "industry_depth_component": 0.10,
    },
    "fundamental": {
        "growth_quality_component": 0.45,
        "valuation_component": 0.25,
        "balance_sheet_component": 0.15,
        "data_freshness_component": 0.10,
        "size_stability_component": 0.05,
    },
    "long": {
        "FundamentalScore": 0.30,
        "long_trend_component": 0.20,
        "IndustryScore": 0.15,
        "RiskScore": 0.15,
        "valuation_component": 0.10,
        "LiquidityScore": 0.05,
        "drawdown_control_component": 0.05,
    },
    "mid": {
        "trend_component": 0.30,
        "relative_strength_component": 0.20,
        "IndustryScore": 0.15,
        "RiskScore": 0.10,
        "LiquidityScore": 0.10,
        "fundamental_improvement_component": 0.10,
        "volatility_adjusted_return_component": 0.05,
    },
    "short": {
        "short_momentum_component": 0.25,
        "breakout_reversal_component": 0.20,
        "volume_amount_component": 0.20,
        "LiquidityScore": 0.15,
        "RiskScore": 0.10,
        "IndustryScore": 0.05,
        "overheat_penalty_component": 0.05,
    },
    "composite": {
        "LongScore": 0.30,
        "MidScore": 0.35,
        "ShortScore": 0.25,
        "RiskScore": 0.05,
        "LiquidityScore": 0.05,
    },
}


def default_score_config(as_of_date: str = DEFAULT_AS_OF_DATE, created_at: str = "") -> dict[str, Any]:
    return {
        "score_version": TARGET_VERSION,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "normalization_method": "cross_sectional_percentile_rank",
        "percentile_convention": "0_to_100",
        "confidence_convention": "0_to_1",
        "winsorization_limits": {"lower": 0.01, "upper": 0.99},
        "missing_value_policy": {
            "score_fill": 50.0,
            "confidence_penalty": "per_symbol_valid_feature_ratio",
            "high_missing_field_coverage_warning_threshold": 0.60,
        },
        "feature_directions": dict(FEATURE_DIRECTIONS),
        "component_fields": COMPONENT_FIELDS,
        "component_weights": COMPONENT_WEIGHTS,
        "horizon_weights": {
            "LongScore": COMPONENT_WEIGHTS["long"],
            "MidScore": COMPONENT_WEIGHTS["mid"],
            "ShortScore": COMPONENT_WEIGHTS["short"],
            "CompositeOpportunityScore": COMPONENT_WEIGHTS["composite"],
        },
        "risk_penalty_policy": {
            "policy": "weighted_component_plus_confidence_penalty",
            "low_score_threshold": 30.0,
            "candidate_generation_allowed": False,
        },
        "liquidity_penalty_policy": {
            "policy": "weighted_component_plus_confidence_penalty",
            "low_score_threshold": 30.0,
            "candidate_generation_allowed": False,
        },
        "fundamental_confidence_policy": {
            "policy": "field_coverage_confidence_penalty",
            "score_fill_when_missing": 50.0,
            "allow_partial_score": True,
        },
        "created_at": created_at,
        "boundary": dict(SCORE_BOUNDARY),
    }


def validate_score_config(config: dict[str, Any]) -> list[str]:
    issues = []
    directions = set(config.get("feature_directions", {}).values())
    invalid_directions = directions.difference({"higher", "lower", "magnitude_lower", "moderate", "boolean_higher"})
    if invalid_directions:
        issues.append(f"invalid feature directions: {sorted(invalid_directions)}")
    for group, weights in config.get("component_weights", {}).items():
        total = sum(float(value) for value in weights.values())
        if abs(total - 1.0) > 1e-9:
            issues.append(f"{group} weights sum to {total}")
    return issues
