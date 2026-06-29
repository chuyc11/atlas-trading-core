"""Configuration for v0.8.1 A-share current-day research workflow runner."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.1-a-share-current-day-research-workflow-runner"
BASELINE_VERSION = "v0.8.0-a-share-daily-data-refresh-and-provider-hardening"
RECOMMENDED_NEXT_VERSION = "v0.8.2-a-share-current-day-owner-briefing-and-monitoring-dashboard"
REMEDIATION_VERSION = "v0.8.1.1-a-share-current-day-runner-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_CURRENT_DAY_READINESS = "validate_current_day_readiness"
RUN_RESEARCH_FROM_EXISTING_REFRESH = "run_research_from_existing_refresh"
REFRESH_THEN_RUN_RESEARCH = "refresh_then_run_research"
AUDIT_EXISTING_CURRENT_DAY_RUN = "audit_existing_current_day_run"
ALLOWED_MODES = [
    VALIDATE_CURRENT_DAY_READINESS,
    RUN_RESEARCH_FROM_EXISTING_REFRESH,
    REFRESH_THEN_RUN_RESEARCH,
    AUDIT_EXISTING_CURRENT_DAY_RUN,
]

VALIDATE_EXISTING_ARTIFACTS = "validate_existing_artifacts"
BUILD_FROM_EXISTING_DATA = "build_from_existing_data"
FULL_RESEARCH_RUN = "full_research_run"
ALLOWED_WORKFLOW_MODES = [
    VALIDATE_EXISTING_ARTIFACTS,
    BUILD_FROM_EXISTING_DATA,
    FULL_RESEARCH_RUN,
]

KNOWN_DATA_REFRESH_WARNINGS = [
    "daily_basic:required_field_all_null",
    "trading_calendar:exchange_level_calendar_collapsed_to_trade_date",
]

CURRENT_DAY_FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

CURRENT_DAY_BOUNDARY = {
    "current_day_research_run_only": True,
    "research_only": True,
    "virtual_only": True,
    "real_portfolio_generated": False,
    "buy_sell_signals_generated": False,
    "order_preview_generated": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "run_daily_called": False,
    "old_run_daily_called": False,
    "day2_executed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "research_result_used_as_trade_instruction": False,
}

CURRENT_DAY_FILES = {
    "current_day_run_config": "current_day_run_config.json",
    "current_day_readiness": "current_day_readiness.json",
    "current_day_data_refresh_link": "current_day_data_refresh_link.json",
    "current_day_workflow_plan": "current_day_workflow_plan.json",
    "current_day_workflow_execution": "current_day_workflow_execution.json",
    "current_day_stage_manifest": "current_day_stage_manifest.json",
    "current_day_artifact_index": "current_day_artifact_index.json",
    "current_day_warning_summary": "current_day_warning_summary.json",
    "current_day_source_trace": "current_day_source_trace.json",
    "current_day_boundary_check": "current_day_boundary_check.json",
    "current_day_run_manifest": "current_day_run_manifest.json",
    "current_day_summary": "current_day_summary.json",
}

CURRENT_DAY_REPORTS = {
    "current_day_summary_report": "A_SHARE_CURRENT_DAY_RUN_SUMMARY.md",
    "current_day_readiness_report": "CURRENT_DAY_READINESS.md",
    "current_day_workflow_stage_report": "CURRENT_DAY_WORKFLOW_STAGE_REPORT.md",
    "current_day_warning_summary_report": "CURRENT_DAY_WARNING_SUMMARY.md",
    "current_day_source_trace_report": "CURRENT_DAY_SOURCE_TRACE.md",
}

FORBIDDEN_ARTIFACT_NAMES = {
    "BROKER_ORDER.json",
    "REAL_ORDER.json",
    "ORDER_PREVIEW.md",
    "BUY_LIST.md",
    "SELL_LIST.md",
}

FORBIDDEN_PATH_TOKENS = {
    "broker",
    "orders",
    "trades",
    "accounts",
    "run_daily",
    "day_002",
    "day_003",
    "real_order",
    "broker_order",
}

FORBIDDEN_POSITIVE_WORDING = [
    "买入建议",
    "卖出建议",
    "下单建议",
    "保证盈利",
    "实盘就绪",
    "推荐买入",
    "买入信号",
    "卖出信号",
]


@dataclass(frozen=True)
class CurrentDayRunConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    resolved_as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = RUN_RESEARCH_FROM_EXISTING_REFRESH
    workflow_mode: str = VALIDATE_EXISTING_ARTIFACTS
    use_data_refresh_resolved_date: bool = False
    allow_date_mismatch: bool = False
    allow_refresh_before_run: bool = False
    allow_network_providers: bool = False
    allow_public_providers: bool = False
    run_post_workflow_modules: bool = False
    allow_post_workflow_warnings_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-CURRENT-DAY-RESEARCH-RUN-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "resolved_as_of_date": self.resolved_as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "workflow_mode": self.workflow_mode,
            "allowed_workflow_modes": list(ALLOWED_WORKFLOW_MODES),
            "use_data_refresh_resolved_date": self.use_data_refresh_resolved_date,
            "allow_date_mismatch": self.allow_date_mismatch,
            "allow_refresh_before_run": self.allow_refresh_before_run,
            "allow_network_providers": self.allow_network_providers,
            "allow_public_providers": self.allow_public_providers,
            "run_post_workflow_modules": self.run_post_workflow_modules,
            "allow_post_workflow_warnings_only": self.allow_post_workflow_warnings_only,
            "call_old_run_daily": False,
            "execute_official_forward_dry_run_day2": False,
            "broker_enabled": False,
            "real_order_enabled": False,
            **CURRENT_DAY_FLAGS,
            "raw_config": asdict(self),
        }


def validate_current_day_config(config: CurrentDayRunConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if not config.resolved_as_of_date or len(config.resolved_as_of_date) != 10:
        issues.append("resolved_as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.workflow_mode not in ALLOWED_WORKFLOW_MODES:
        issues.append(f"workflow_mode must be one of {ALLOWED_WORKFLOW_MODES}")
    if config.mode == REFRESH_THEN_RUN_RESEARCH and not config.allow_refresh_before_run:
        issues.append("refresh_then_run_research requires allow_refresh_before_run=true")
    if config.allow_public_providers and not config.allow_network_providers:
        issues.append("allow_public_providers requires allow_network_providers=true")
    if config.as_of_date != config.resolved_as_of_date and not config.allow_date_mismatch:
        issues.append("resolved_as_of_date differs from as_of_date; pass allow_date_mismatch to proceed")
    return issues


def current_day_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date


def current_day_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_current_day_runs" / "daily" / as_of_date


def current_day_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = current_day_data_dir(paths, as_of_date)
    output_dir = current_day_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in CURRENT_DAY_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in CURRENT_DAY_REPORTS.items()})
    artifacts["current_day_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json"
    artifacts["current_day_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_CURRENT_DAY_RESEARCH_RUN_AUDIT.md"
    return artifacts

