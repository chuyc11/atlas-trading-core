"""Configuration for v0.7.11 A-share multi-day performance tracking."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.7.11-a-share-multi-day-portfolio-performance-tracking"
RECOMMENDED_NEXT_VERSION = "v0.7.12-a-share-performance-attribution-and-risk-diagnostics"
REMEDIATION_VERSION = "v0.7.11.1-a-share-multi-day-performance-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"
DEFAULT_TRACKING_START_DATE = "2026-06-26"
DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS = 20
DEFAULT_ROLLING_WINDOW_DAYS = 20

CURRENT_SNAPSHOT_MODE = "current_snapshot"
APPEND_MODE = "append_from_existing_tracking"
REBUILD_MODE = "rebuild_virtual_performance_series"
ALLOWED_MODES = [CURRENT_SNAPSHOT_MODE, APPEND_MODE, REBUILD_MODE]

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

PERFORMANCE_FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

PERFORMANCE_BOUNDARY = {
    "multi_day_performance_tracking_only": True,
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
    "official_forward_dry_run_status_unchanged": True,
}

FORBIDDEN_EXPLICIT_FILES = [
    "BROKER_ORDER.json",
    "REAL_ORDER.json",
    "ORDER_PREVIEW.md",
    "BUY_LIST.md",
    "SELL_LIST.md",
]
FORBIDDEN_DATE_SCOPED_ARTIFACTS = [
    "data/orders/orders-{as_of_date}.jsonl",
    "data/trades/trades-{as_of_date}.jsonl",
    "data/accounts/account-{as_of_date}.json",
    "outputs/orders/orders-{as_of_date}.md",
    "outputs/trades/trades-{as_of_date}.md",
    "outputs/accounts/account-{as_of_date}.md",
]
FORBIDDEN_SOURCE_PATH_TOKENS = [
    "tests/fixtures",
    "sample",
    "mock",
    "external_research",
    "day_002",
    "day_003",
    "broker",
    "orders",
    "trades",
    "accounts",
    "run_daily",
]
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
    "live trading ready: true",
    "strong buy",
    "must buy",
]

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

PERFORMANCE_REPORTS = {
    "performance_summary_report": "A_SHARE_MULTI_DAY_PERFORMANCE_SUMMARY.md",
    "portfolio_nav_return_report": "PORTFOLIO_NAV_AND_RETURN_SERIES.md",
    "portfolio_relative_performance_report": "PORTFOLIO_RELATIVE_PERFORMANCE.md",
    "performance_limitations_report": "PERFORMANCE_LIMITATIONS.md",
    "performance_source_trace_report": "PERFORMANCE_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class PerformanceConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    tracking_start_date: str = DEFAULT_TRACKING_START_DATE
    mode: str = CURRENT_SNAPSHOT_MODE
    minimum_required_observations: int = DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS
    rolling_window_days: int = DEFAULT_ROLLING_WINDOW_DAYS
    append_only: bool = True
    allow_rebuild: bool = False
    allow_idempotent_append: bool = True
    allow_historical_reconstruction: bool = False
    label_historical_reconstruction_separately: bool = True
    price_policy: str = "use_existing_tracking_mark_price_then_adjusted_close_if_available_else_close"

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-MULTI-DAY-PERFORMANCE-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "tracking_start_date": self.tracking_start_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "portfolio_ids": [PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS],
            "benchmark_ids": list(BENCHMARK_IDS),
            "minimum_required_observations": self.minimum_required_observations,
            "rolling_window_days": self.rolling_window_days,
            "price_policy": self.price_policy,
            "append_only": self.append_only,
            "allow_rebuild": self.allow_rebuild,
            "allow_idempotent_append": self.allow_idempotent_append,
            "allow_historical_reconstruction": self.allow_historical_reconstruction,
            "label_historical_reconstruction_separately": self.label_historical_reconstruction_separately,
            "broker_enabled": False,
            "real_order_enabled": False,
            **PERFORMANCE_FLAGS,
            "boundary": dict(PERFORMANCE_BOUNDARY),
            "raw_config": asdict(self),
        }


def validate_performance_config(config: PerformanceConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if not config.tracking_start_date or len(config.tracking_start_date) != 10:
        issues.append("tracking_start_date must use YYYY-MM-DD")
    if config.tracking_start_date > config.as_of_date:
        issues.append("tracking_start_date must be <= as_of_date")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.minimum_required_observations <= 0:
        issues.append("minimum_required_observations must be positive")
    if config.rolling_window_days <= 0:
        issues.append("rolling_window_days must be positive")
    if config.rolling_window_days > config.minimum_required_observations:
        issues.append("rolling_window_days must be <= minimum_required_observations")
    if not config.append_only:
        issues.append("append_only must remain true")
    if config.mode == REBUILD_MODE and not config.allow_rebuild:
        issues.append("rebuild_virtual_performance_series requires allow_rebuild=true")
    if config.allow_historical_reconstruction and not config.allow_rebuild:
        issues.append("allow_historical_reconstruction requires allow_rebuild=true")
    if not config.label_historical_reconstruction_separately:
        issues.append("label_historical_reconstruction_separately must remain true")
    return issues


def performance_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_performance" / "daily" / as_of_date


def performance_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_performance" / "daily" / as_of_date


def performance_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = performance_data_dir(paths, as_of_date)
    output_dir = performance_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in PERFORMANCE_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in PERFORMANCE_REPORTS.items()})
    artifacts["performance_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_multi_day_performance_audit.json"
    artifacts["performance_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_MULTI_DAY_PERFORMANCE_AUDIT.md"
    return artifacts
