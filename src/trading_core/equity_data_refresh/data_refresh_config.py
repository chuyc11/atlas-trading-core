"""Configuration for v0.8.0 A-share daily data refresh."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.0-a-share-daily-data-refresh-and-provider-hardening"
RECOMMENDED_NEXT_VERSION = "v0.8.1-a-share-current-day-research-workflow-runner"
REMEDIATION_VERSION = "v0.8.0.1-a-share-daily-data-refresh-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"
DEFAULT_MARKET = "A_SHARE"
DEFAULT_TIMEZONE = "Asia/Shanghai"

VALIDATE_EXISTING_DATA = "validate_existing_data"
REFRESH_FROM_LOCAL_SOURCES = "refresh_from_local_sources"
REFRESH_FROM_PUBLIC_PROVIDERS = "refresh_from_public_providers"
REFRESH_AND_VALIDATE = "refresh_and_validate"
ALLOWED_MODES = [
    VALIDATE_EXISTING_DATA,
    REFRESH_FROM_LOCAL_SOURCES,
    REFRESH_FROM_PUBLIC_PROVIDERS,
    REFRESH_AND_VALIDATE,
]

DATASET_IDS = [
    "equity_master",
    "daily_price",
    "adjusted_price",
    "daily_basic",
    "index_price",
    "industry_classification",
    "financial_indicators",
    "trading_calendar",
]
CRITICAL_DATASETS = ["trading_calendar", "daily_price", "adjusted_price", "index_price"]
REQUIRED_INDEX_IDS = ["CSI300", "CSI500", "CSI1000"]

REFRESH_FLAGS = {
    "research_only": True,
    "market_data_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

REFRESH_BOUNDARY = {
    "data_refresh_only": True,
    "market_data_only": True,
    "research_only": True,
    "real_portfolio_generated": False,
    "buy_sell_signals_generated": False,
    "order_preview_generated": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "run_daily_called": False,
    "day2_executed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "research_workflow_triggered": False,
    "official_forward_dry_run_status_unchanged": True,
}

FORBIDDEN_EXPLICIT_FILES = ["BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"]
FORBIDDEN_SOURCE_TOKENS = ["broker", "orders", "trades", "accounts", "run_daily", "day_002", "day_003", "real_order", "broker_order"]
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]

DATA_REFRESH_FILES = {
    "data_refresh_config": "data_refresh_config.json",
    "date_resolution": "date_resolution.json",
    "provider_registry_snapshot": "provider_registry_snapshot.json",
    "provider_health_check": "provider_health_check.json",
    "provider_execution_log": "provider_execution_log.json",
    "dataset_refresh_plan": "dataset_refresh_plan.json",
    "dataset_refresh_result": "dataset_refresh_result.json",
    "dataset_schema_validation": "dataset_schema_validation.json",
    "dataset_freshness_validation": "dataset_freshness_validation.json",
    "dataset_coverage_summary": "dataset_coverage_summary.json",
    "data_gap_report": "data_gap_report.json",
    "provider_fallback_report": "provider_fallback_report.json",
    "data_refresh_source_trace": "data_refresh_source_trace.json",
    "data_refresh_manifest": "data_refresh_manifest.json",
    "data_refresh_boundary_check": "data_refresh_boundary_check.json",
    "data_refresh_summary": "data_refresh_summary.json",
}

DATA_REFRESH_REPORTS = {
    "data_refresh_summary_report": "A_SHARE_DATA_REFRESH_SUMMARY.md",
    "provider_health_report": "PROVIDER_HEALTH_CHECK.md",
    "dataset_coverage_report": "DATASET_COVERAGE_SUMMARY.md",
    "data_gap_report_md": "DATA_GAP_REPORT.md",
    "data_refresh_source_trace_report": "DATA_REFRESH_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class DataRefreshConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    requested_date_mode: str = "explicit_as_of_date"
    market: str = DEFAULT_MARKET
    timezone: str = DEFAULT_TIMEZONE
    mode: str = VALIDATE_EXISTING_DATA
    resolve_latest_completed_trading_day: bool = False
    allow_network_providers: bool = False
    allow_public_providers: bool = False
    allow_intraday_research_refresh: bool = False
    allow_non_trading_day: bool = False
    allow_partial_refresh: bool = False
    allow_schema_fallback: bool = True
    allow_latest_available_if_exact_missing: bool = False
    allow_research_workflow_after_refresh: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-DAILY-DATA-REFRESH-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "requested_date_mode": self.requested_date_mode,
            "market": self.market,
            "timezone": self.timezone,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "datasets": list(DATASET_IDS),
            "allow_network_providers": self.allow_network_providers,
            "allow_public_providers": self.allow_public_providers,
            "allow_intraday_research_refresh": self.allow_intraday_research_refresh,
            "allow_non_trading_day": self.allow_non_trading_day,
            "allow_partial_refresh": self.allow_partial_refresh,
            "allow_schema_fallback": self.allow_schema_fallback,
            "allow_latest_available_if_exact_missing": self.allow_latest_available_if_exact_missing,
            "allow_research_workflow_after_refresh": self.allow_research_workflow_after_refresh,
            "broker_enabled": False,
            "real_order_enabled": False,
            **REFRESH_FLAGS,
            "raw_config": asdict(self),
        }


def validate_data_refresh_config(config: DataRefreshConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.market != DEFAULT_MARKET:
        issues.append("market must be A_SHARE")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.mode == REFRESH_FROM_PUBLIC_PROVIDERS and not (config.allow_network_providers and config.allow_public_providers):
        issues.append("refresh_from_public_providers requires explicit network and public provider opt-in")
    if config.allow_research_workflow_after_refresh:
        issues.append("allow_research_workflow_after_refresh must remain false for v0.8.0 release")
    return issues


def data_refresh_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_data_refresh" / "daily" / as_of_date


def data_refresh_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_data_refresh" / "daily" / as_of_date


def data_refresh_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = data_refresh_data_dir(paths, as_of_date)
    output_dir = data_refresh_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in DATA_REFRESH_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in DATA_REFRESH_REPORTS.items()})
    artifacts["data_refresh_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_daily_data_refresh_audit.json"
    artifacts["data_refresh_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_DAILY_DATA_REFRESH_AUDIT.md"
    return artifacts
