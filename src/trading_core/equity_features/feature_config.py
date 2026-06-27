"""Configuration and constants for A-share multi-horizon features."""

from __future__ import annotations


TARGET_VERSION = "v0.7.3-a-share-multi-horizon-feature-engineering"
RECOMMENDED_NEXT_VERSION = "v0.7.4-a-share-long-mid-short-scoring-system"
REMEDIATION_VERSION = "v0.7.3.1-a-share-feature-engineering-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

FEATURE_BOUNDARY = {
    "feature_engineering_only": True,
    "scores_generated": False,
    "candidates_generated": False,
    "watchlist_generated": False,
    "virtual_portfolio_generated": False,
    "official_forward_dry_run_status_unchanged": True,
    "day2_executed": False,
    "run_daily_called": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
}

COMMON_COLUMNS = [
    "as_of_date",
    "symbol",
    "name",
    "exchange",
    "board",
    "industry_level_1",
    "industry_level_2",
    "feature_group",
    "source",
    "created_at",
]

SHORT_FIELDS = [
    "return_1d",
    "return_3d",
    "return_5d",
    "return_10d",
    "return_20d",
    "momentum_5d",
    "momentum_10d",
    "momentum_20d",
    "volume_change_5d",
    "amount_change_5d",
    "amount_change_20d",
    "close_to_20d_high",
    "close_to_20d_low",
    "breakout_20d_high",
    "drawdown_from_20d_high",
    "reversal_from_20d_low",
    "gap_1d",
    "intraday_range_1d",
    "amplitude_5d",
    "amplitude_20d",
]

MID_FIELDS = [
    "return_20d",
    "return_60d",
    "return_120d",
    "momentum_60d",
    "momentum_120d",
    "ma_20",
    "ma_60",
    "ma_120",
    "close_to_ma_20",
    "close_to_ma_60",
    "close_to_ma_120",
    "ma_20_slope",
    "ma_60_slope",
    "ma_120_slope",
    "trend_consistency_60d",
    "trend_consistency_120d",
    "relative_strength_60d_vs_market",
    "relative_strength_120d_vs_market",
    "relative_strength_60d_vs_industry",
    "relative_strength_120d_vs_industry",
    "volatility_adjusted_return_60d",
    "volatility_adjusted_return_120d",
]

LONG_FIELDS = [
    "return_250d",
    "return_3y",
    "return_5y",
    "ma_250",
    "close_to_ma_250",
    "ma_250_slope",
    "max_drawdown_250d",
    "max_drawdown_3y",
    "annualized_return_250d",
    "annualized_volatility_250d",
    "calmar_250d",
    "relative_strength_250d_vs_market",
    "relative_strength_250d_vs_industry",
    "long_trend_consistency_250d",
]

RISK_FIELDS = [
    "volatility_20d",
    "volatility_60d",
    "volatility_120d",
    "volatility_250d",
    "downside_volatility_60d",
    "downside_volatility_120d",
    "max_drawdown_20d",
    "max_drawdown_60d",
    "max_drawdown_120d",
    "max_drawdown_250d",
    "var_95_20d",
    "var_95_60d",
    "expected_shortfall_95_60d",
    "skewness_60d",
    "kurtosis_60d",
    "limit_up_days_60d",
    "limit_down_days_60d",
    "large_drop_days_60d",
    "large_gap_days_60d",
]

LIQUIDITY_FIELDS = [
    "avg_amount_5d",
    "avg_amount_20d",
    "avg_amount_60d",
    "avg_volume_20d",
    "avg_volume_60d",
    "turnover_rate_20d_avg",
    "turnover_rate_60d_avg",
    "amount_stability_20d",
    "amount_stability_60d",
    "zero_volume_days_60d",
    "effective_trading_days_20d",
    "effective_trading_days_60d",
    "estimated_slippage_proxy_20d",
    "estimated_slippage_proxy_60d",
]

INDUSTRY_FIELDS = [
    "industry_level_1",
    "industry_level_2",
    "industry_return_5d",
    "industry_return_20d",
    "industry_return_60d",
    "industry_return_120d",
    "industry_return_250d",
    "industry_relative_strength_20d",
    "industry_relative_strength_60d",
    "industry_relative_strength_120d",
    "industry_relative_strength_250d",
    "stock_rank_in_industry_by_return_20d",
    "stock_rank_in_industry_by_return_60d",
    "stock_rank_in_industry_by_return_120d",
    "stock_percentile_in_industry_by_return_20d",
    "stock_percentile_in_industry_by_return_60d",
    "stock_percentile_in_industry_by_return_120d",
    "industry_member_count",
]

FUNDAMENTAL_FIELDS = [
    "pe_ttm",
    "pb",
    "ps_ttm",
    "dv_ttm",
    "pe_ttm_percentile_3y",
    "pb_percentile_3y",
    "ps_ttm_percentile_3y",
    "total_mv",
    "circ_mv",
    "revenue_growth_yoy",
    "net_profit_growth_yoy",
    "roe_latest",
    "roe_ttm",
    "gross_margin_latest",
    "net_margin_latest",
    "operating_cash_flow_latest",
    "debt_to_asset_latest",
    "eps_latest",
    "bps_latest",
    "financial_report_age_days",
    "financial_quarters_available",
]

FEATURE_GROUP_FIELDS = {
    "short_horizon": SHORT_FIELDS,
    "mid_horizon": MID_FIELDS,
    "long_horizon": LONG_FIELDS,
    "risk": RISK_FIELDS,
    "liquidity": LIQUIDITY_FIELDS,
    "industry": INDUSTRY_FIELDS,
    "fundamental": FUNDAMENTAL_FIELDS,
}

