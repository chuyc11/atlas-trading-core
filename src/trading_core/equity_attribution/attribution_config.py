"""Configuration for v0.7.12 A-share attribution diagnostics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.7.12-a-share-performance-attribution-and-risk-diagnostics"
RECOMMENDED_NEXT_VERSION = "v0.8.0-a-share-daily-data-refresh-and-provider-hardening"
REMEDIATION_VERSION = "v0.7.12.1-a-share-attribution-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"
DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS = 20

CURRENT_EXPOSURE_MODE = "current_exposure_diagnostics"
SINGLE_DAY_MODE = "single_day_initialization_attribution"
MULTI_DAY_MODE = "multi_day_performance_attribution"
ALLOWED_MODES = [CURRENT_EXPOSURE_MODE, SINGLE_DAY_MODE, MULTI_DAY_MODE]

PORTFOLIO_KEYS = ["long", "mid", "short"]
PORTFOLIO_IDS = {
    "long": "long_virtual_portfolio",
    "mid": "mid_virtual_portfolio",
    "short": "short_virtual_portfolio",
}
PORTFOLIO_ID_TO_KEY = {value: key for key, value in PORTFOLIO_IDS.items()}
BENCHMARK_IDS = [
    "CSI300",
    "CSI500",
    "CSI1000",
    "CASH",
    "EQUAL_WEIGHT_STRICT_TRADABLE",
    "EQUAL_WEIGHT_CANDIDATE_POOL",
]
SCORE_NAMES = ["CompositeOpportunityScore", "LongScore", "MidScore", "ShortScore"]
FACTOR_SCORE_NAMES = [
    "CompositeOpportunityScore",
    "LongScore",
    "MidScore",
    "ShortScore",
    "RiskScore",
    "LiquidityScore",
    "IndustryScore",
    "FundamentalScore",
]
BUCKET_EDGES = [0, 20, 40, 60, 80, 100]
CONCENTRATION_TOP_N = [5, 10]

ATTRIBUTION_FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_real_trade": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

ATTRIBUTION_BOUNDARY = {
    "performance_attribution_only": True,
    "risk_diagnostics_only": True,
    "research_only": True,
    "virtual_only": True,
    "real_portfolio_generated": False,
    "buy_sell_signals_generated": False,
    "order_preview_generated": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "run_daily_called": False,
    "day2_executed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "historical_performance_fabricated": False,
    "future_data_used": False,
    "attribution_used_as_trade_signal": False,
    "official_forward_dry_run_status_unchanged": True,
}

FORBIDDEN_EXPLICIT_FILES = ["BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"]
FORBIDDEN_PATH_TOKENS = ["tests/fixtures", "sample", "mock", "external_research", "day_002", "day_003", "broker", "orders", "trades", "accounts", "run_daily"]
FORBIDDEN_POSITIVE_WORDING = [
    "买入建议",
    "卖出建议",
    "下单建议",
    "保证盈利",
    "实盘就绪",
    "推荐买入",
    "买入信号",
    "卖出信号",
    "guaranteed profit",
    "strong buy",
    "must buy",
]

ATTRIBUTION_FILES = {
    "attribution_config": "attribution_config.json",
    "attribution_data_availability": "attribution_data_availability.json",
    "holding_contribution_snapshot": "holding_contribution_snapshot.json",
    "industry_contribution_snapshot": "industry_contribution_snapshot.json",
    "candidate_source_contribution_snapshot": "candidate_source_contribution_snapshot.json",
    "score_bucket_contribution_snapshot": "score_bucket_contribution_snapshot.json",
    "risk_bucket_contribution_snapshot": "risk_bucket_contribution_snapshot.json",
    "liquidity_bucket_contribution_snapshot": "liquidity_bucket_contribution_snapshot.json",
    "benchmark_relative_attribution_snapshot": "benchmark_relative_attribution_snapshot.json",
    "portfolio_concentration_diagnostics": "portfolio_concentration_diagnostics.json",
    "risk_diagnostics_snapshot": "risk_diagnostics_snapshot.json",
    "liquidity_diagnostics_snapshot": "liquidity_diagnostics_snapshot.json",
    "industry_diagnostics_snapshot": "industry_diagnostics_snapshot.json",
    "factor_exposure_snapshot": "factor_exposure_snapshot.json",
    "attribution_limitations": "attribution_limitations.json",
    "attribution_source_trace": "attribution_source_trace.json",
    "attribution_manifest": "attribution_manifest.json",
    "attribution_boundary_check": "attribution_boundary_check.json",
    "attribution_summary": "attribution_summary.json",
}

ATTRIBUTION_REPORTS = {
    "attribution_summary_report": "A_SHARE_ATTRIBUTION_SUMMARY.md",
    "holding_industry_report": "HOLDING_AND_INDUSTRY_ATTRIBUTION.md",
    "score_risk_liquidity_report": "SCORE_RISK_LIQUIDITY_DIAGNOSTICS.md",
    "benchmark_relative_report": "BENCHMARK_RELATIVE_ATTRIBUTION.md",
    "attribution_limitations_report": "ATTRIBUTION_LIMITATIONS.md",
    "attribution_source_trace_report": "ATTRIBUTION_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class AttributionConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = CURRENT_EXPOSURE_MODE
    minimum_required_observations: int = DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS
    allow_limited_history: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-PERFORMANCE-ATTRIBUTION-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "portfolio_ids": [PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS],
            "benchmark_ids": list(BENCHMARK_IDS),
            "minimum_required_observations": self.minimum_required_observations,
            "score_bucket_edges": list(BUCKET_EDGES),
            "risk_bucket_edges": list(BUCKET_EDGES),
            "liquidity_bucket_edges": list(BUCKET_EDGES),
            "concentration_top_n": list(CONCENTRATION_TOP_N),
            "structural_diagnostics_available": True,
            "realized_performance_attribution_available": False,
            "limited_history": True,
            "allow_limited_history": self.allow_limited_history,
            "broker_enabled": False,
            "real_order_enabled": False,
            **ATTRIBUTION_FLAGS,
            "boundary": dict(ATTRIBUTION_BOUNDARY),
            "raw_config": asdict(self),
        }


def validate_attribution_config(config: AttributionConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.minimum_required_observations <= 0:
        issues.append("minimum_required_observations must be positive")
    if not config.allow_limited_history and config.mode != MULTI_DAY_MODE:
        issues.append("allow_limited_history must remain true for structural attribution modes")
    return issues


def attribution_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_attribution" / "daily" / as_of_date


def attribution_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_attribution" / "daily" / as_of_date


def attribution_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = attribution_data_dir(paths, as_of_date)
    output_dir = attribution_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in ATTRIBUTION_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in ATTRIBUTION_REPORTS.items()})
    artifacts["attribution_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_performance_attribution_audit.json"
    artifacts["attribution_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_PERFORMANCE_ATTRIBUTION_AUDIT.md"
    return artifacts
