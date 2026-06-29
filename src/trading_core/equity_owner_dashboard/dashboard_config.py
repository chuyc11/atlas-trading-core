"""Configuration for v0.8.2 A-share owner dashboard."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.2-a-share-current-day-owner-briefing-and-monitoring-dashboard"
BASELINE_VERSION = "v0.8.1-a-share-current-day-research-workflow-runner"
RECOMMENDED_NEXT_VERSION = "v0.8.3-a-share-owner-alerting-and-run-history-monitoring"
REMEDIATION_VERSION = "v0.8.2.1-a-share-owner-dashboard-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_EXISTING_DASHBOARD_INPUTS = "validate_existing_dashboard_inputs"
BUILD_DASHBOARD_FROM_EXISTING_RUN = "build_dashboard_from_existing_run"
AUDIT_EXISTING_DASHBOARD = "audit_existing_dashboard"
ALLOWED_MODES = [
    VALIDATE_EXISTING_DASHBOARD_INPUTS,
    BUILD_DASHBOARD_FROM_EXISTING_RUN,
    AUDIT_EXISTING_DASHBOARD,
]

DASHBOARD_SCOPE = [
    "data_refresh",
    "current_day_research_run",
    "workflow",
    "briefing",
    "tracking",
    "benchmark",
    "performance",
    "attribution",
    "warnings",
    "boundary",
    "artifact_navigation",
]

REQUIRED_CARDS = [
    "executive_status_card",
    "data_freshness_card",
    "workflow_status_card",
    "research_output_card",
    "warning_and_blocker_card",
    "artifact_navigation_index",
]

OPTIONAL_CARDS = [
    "provider_health_card",
    "candidate_summary_card",
    "portfolio_summary_card",
    "benchmark_summary_card",
    "performance_summary_card",
    "attribution_summary_card",
]

DASHBOARD_FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

DASHBOARD_BOUNDARY = {
    "owner_dashboard_only": True,
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
    "dashboard_used_as_trade_instruction": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_PATH_TOKENS = {"broker", "orders", "trades", "accounts", "run_daily", "day_002", "day_003", "real_order", "broker_order"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]

DASHBOARD_FILES = {
    "dashboard_config": "dashboard_config.json",
    "dashboard_input_availability": "dashboard_input_availability.json",
    "executive_status_card": "executive_status_card.json",
    "data_freshness_card": "data_freshness_card.json",
    "provider_health_card": "provider_health_card.json",
    "workflow_status_card": "workflow_status_card.json",
    "research_output_card": "research_output_card.json",
    "candidate_summary_card": "candidate_summary_card.json",
    "portfolio_summary_card": "portfolio_summary_card.json",
    "benchmark_summary_card": "benchmark_summary_card.json",
    "performance_summary_card": "performance_summary_card.json",
    "attribution_summary_card": "attribution_summary_card.json",
    "warning_and_blocker_card": "warning_and_blocker_card.json",
    "artifact_navigation_index": "artifact_navigation_index.json",
    "dashboard_source_trace": "dashboard_source_trace.json",
    "dashboard_boundary_check": "dashboard_boundary_check.json",
    "dashboard_manifest": "dashboard_manifest.json",
    "dashboard_summary": "dashboard_summary.json",
}

DASHBOARD_REPORTS = {
    "owner_dashboard_report": "A_SHARE_OWNER_DASHBOARD.md",
    "owner_dashboard_compact_report": "A_SHARE_OWNER_DASHBOARD_COMPACT.md",
    "owner_warning_blocker_report": "A_SHARE_OWNER_WARNING_AND_BLOCKER_SUMMARY.md",
    "owner_artifact_navigation_report": "A_SHARE_OWNER_ARTIFACT_NAVIGATION.md",
    "owner_dashboard_source_trace_report": "A_SHARE_OWNER_DASHBOARD_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class OwnerDashboardConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    resolved_as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_DASHBOARD_FROM_EXISTING_RUN
    language: str = "zh-CN"
    owner_facing: bool = True
    machine_readable: bool = True
    render_markdown: bool = True
    compact_report: bool = True
    allow_missing_optional_cards: bool = True
    fail_on_missing_required_cards: bool = True
    allow_date_mismatch: bool = False
    fail_on_missing_optional_card: bool = False
    compact_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-DASHBOARD-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "resolved_as_of_date": self.resolved_as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "dashboard_scope": list(DASHBOARD_SCOPE),
            "language": self.language,
            "owner_facing": self.owner_facing,
            "machine_readable": self.machine_readable,
            "render_markdown": self.render_markdown,
            "compact_report": self.compact_report,
            "allow_missing_optional_cards": self.allow_missing_optional_cards,
            "fail_on_missing_required_cards": self.fail_on_missing_required_cards,
            "allow_date_mismatch": self.allow_date_mismatch,
            "fail_on_missing_optional_card": self.fail_on_missing_optional_card,
            "compact_only": self.compact_only,
            "broker_enabled": False,
            "real_order_enabled": False,
            **DASHBOARD_FLAGS,
            "raw_config": asdict(self),
        }


def validate_dashboard_config(config: OwnerDashboardConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if not config.resolved_as_of_date or len(config.resolved_as_of_date) != 10:
        issues.append("resolved_as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.as_of_date != config.resolved_as_of_date and not config.allow_date_mismatch:
        issues.append("resolved_as_of_date differs from as_of_date; pass allow_date_mismatch to proceed")
    return issues


def dashboard_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_dashboard" / "daily" / as_of_date


def dashboard_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_dashboard" / "daily" / as_of_date


def dashboard_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = dashboard_data_dir(paths, as_of_date)
    output_dir = dashboard_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / name for key, name in DASHBOARD_FILES.items()}
    artifacts.update({key: output_dir / name for key, name in DASHBOARD_REPORTS.items()})
    artifacts["dashboard_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_dashboard_audit.json"
    artifacts["dashboard_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_DASHBOARD_AUDIT.md"
    return artifacts

