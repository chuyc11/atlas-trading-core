"""Configuration for v0.7.6 A-share virtual portfolio construction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


TARGET_VERSION = "v0.7.6-a-share-virtual-portfolio-construction"
RECOMMENDED_NEXT_VERSION = "v0.7.7-a-share-daily-stock-selection-briefing"
REMEDIATION_VERSION = "v0.7.6.1-a-share-virtual-portfolio-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

PORTFOLIO_BOUNDARY = {
    "virtual_portfolio_construction_only": True,
    "virtual_portfolio_generated": True,
    "real_portfolio_generated": False,
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

PORTFOLIO_FILES = {
    "portfolio_construction_config": "portfolio_construction_config.json",
    "long_virtual_portfolio_json": "long_virtual_portfolio.json",
    "long_virtual_portfolio_parquet": "long_virtual_portfolio.parquet",
    "mid_virtual_portfolio_json": "mid_virtual_portfolio.json",
    "mid_virtual_portfolio_parquet": "mid_virtual_portfolio.parquet",
    "short_virtual_portfolio_json": "short_virtual_portfolio.json",
    "short_virtual_portfolio_parquet": "short_virtual_portfolio.parquet",
    "portfolio_weight_summary": "portfolio_weight_summary.json",
    "portfolio_industry_exposure": "portfolio_industry_exposure.json",
    "portfolio_risk_liquidity_summary": "portfolio_risk_liquidity_summary.json",
    "portfolio_manifest": "portfolio_manifest.json",
}

PORTFOLIO_REPORTS = {
    "long_virtual_portfolio_report": "LONG_VIRTUAL_PORTFOLIO.md",
    "mid_virtual_portfolio_report": "MID_VIRTUAL_PORTFOLIO.md",
    "short_virtual_portfolio_report": "SHORT_VIRTUAL_PORTFOLIO.md",
    "portfolio_construction_summary_report": "PORTFOLIO_CONSTRUCTION_SUMMARY.md",
}


@dataclass(frozen=True)
class PortfolioConstructionConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    long_holdings: int = 30
    mid_holdings: int = 30
    short_holdings: int = 20
    long_max_single_weight: float = 0.05
    mid_max_single_weight: float = 0.06
    short_max_single_weight: float = 0.08
    long_max_industry_weight: float = 0.25
    mid_max_industry_weight: float = 0.25
    short_max_industry_weight: float = 0.30
    long_min_risk_score: float = 40.0
    long_min_liquidity_score: float = 40.0
    mid_min_risk_score: float = 35.0
    mid_min_liquidity_score: float = 45.0
    short_min_risk_score: float = 35.0
    short_min_liquidity_score: float = 50.0
    total_target_weight: float = 1.0
    minimum_cash_buffer: float = 0.0
    allow_caution_universe: bool = False
    allow_unknown_universe: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "target_version": TARGET_VERSION,
            "portfolio_method": "research_only_long_only_target_weight_construction",
            "weight_convention": "decimal_sum_to_1",
            "long_only": True,
            "leverage_allowed": False,
            "margin_allowed": False,
            "derivatives_allowed": False,
            "boundary": dict(PORTFOLIO_BOUNDARY),
        }


def validate_portfolio_config(config: PortfolioConstructionConfig) -> list[str]:
    issues: list[str] = []
    for field in ["long_holdings", "mid_holdings", "short_holdings"]:
        if int(getattr(config, field)) <= 0:
            issues.append(f"{field} must be positive")
    for field in [
        "long_max_single_weight",
        "mid_max_single_weight",
        "short_max_single_weight",
        "long_max_industry_weight",
        "mid_max_industry_weight",
        "short_max_industry_weight",
    ]:
        value = float(getattr(config, field))
        if value <= 0.0 or value > 1.0:
            issues.append(f"{field} must be within (0, 1]")
    if float(config.total_target_weight) <= 0.0 or float(config.total_target_weight) > 1.0:
        issues.append("total_target_weight must be within (0, 1]")
    return issues

