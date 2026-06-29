"""Configuration for v0.8.9 build-output owner dashboard."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh"
BASELINE_VERSION = "v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability"
RECOMMENDED_NEXT_VERSION = "v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_INPUTS = "validate_build_output_dashboard_inputs"
RESOLVE_SOURCES = "resolve_build_output_sources"
BUILD_DASHBOARD = "build_owner_dashboard_from_build_output"
COMPARE_DASHBOARDS = "compare_validate_dashboard_vs_build_dashboard"
AUDIT_EXISTING = "audit_existing_build_output_dashboard"
ALLOWED_MODES = [
    VALIDATE_INPUTS,
    RESOLVE_SOURCES,
    BUILD_DASHBOARD,
    COMPARE_DASHBOARDS,
    AUDIT_EXISTING,
]

SOURCE_WORKFLOW_MODE = "build_from_existing_data"

REQUIRED_CARDS = [
    "build_output_executive_status_card",
    "build_output_data_freshness_card",
    "build_output_workflow_status_card",
    "build_output_research_output_card",
    "build_output_warning_and_blocker_card",
    "build_output_artifact_navigation",
]

OPTIONAL_CARDS = [
    "build_output_candidate_summary_card",
    "build_output_portfolio_summary_card",
    "build_output_benchmark_summary_card",
    "build_output_performance_summary_card",
    "build_output_attribution_summary_card",
    "build_output_repeatability_card",
    "build_output_protected_path_card",
]

BOUNDARY = {
    "build_output_dashboard_only": True,
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
    "official_forward_dry_run_status_unchanged": True,
    "external_notifications_sent": False,
    "public_network_refresh_run": False,
    "full_research_run": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "dashboard_used_as_trade_instruction": False,
}

FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

FORBIDDEN_ARTIFACT_NAMES = {
    "BROKER_ORDER.json",
    "REAL_ORDER.json",
    "ORDER_PREVIEW.md",
    "BUY_LIST.md",
    "SELL_LIST.md",
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

FILES = {
    "build_output_dashboard_config": "build_output_dashboard_config.json",
    "build_output_input_availability": "build_output_input_availability.json",
    "build_output_source_resolution": "build_output_source_resolution.json",
    "build_output_date_alignment": "build_output_date_alignment.json",
    "build_output_executive_status_card": "build_output_executive_status_card.json",
    "build_output_data_freshness_card": "build_output_data_freshness_card.json",
    "build_output_workflow_status_card": "build_output_workflow_status_card.json",
    "build_output_research_output_card": "build_output_research_output_card.json",
    "build_output_candidate_summary_card": "build_output_candidate_summary_card.json",
    "build_output_portfolio_summary_card": "build_output_portfolio_summary_card.json",
    "build_output_benchmark_summary_card": "build_output_benchmark_summary_card.json",
    "build_output_performance_summary_card": "build_output_performance_summary_card.json",
    "build_output_attribution_summary_card": "build_output_attribution_summary_card.json",
    "build_output_repeatability_card": "build_output_repeatability_card.json",
    "build_output_protected_path_card": "build_output_protected_path_card.json",
    "build_output_warning_and_blocker_card": "build_output_warning_and_blocker_card.json",
    "build_output_artifact_navigation": "build_output_artifact_navigation.json",
    "validate_dashboard_vs_build_dashboard_comparison": "validate_dashboard_vs_build_dashboard_comparison.json",
    "build_output_dashboard_source_trace": "build_output_dashboard_source_trace.json",
    "build_output_dashboard_boundary_check": "build_output_dashboard_boundary_check.json",
    "build_output_dashboard_manifest": "build_output_dashboard_manifest.json",
    "build_output_dashboard_summary": "build_output_dashboard_summary.json",
}

REPORTS = {
    "build_output_owner_dashboard_report": "A_SHARE_BUILD_OUTPUT_OWNER_DASHBOARD.md",
    "build_output_owner_dashboard_compact_report": "A_SHARE_BUILD_OUTPUT_OWNER_DASHBOARD_COMPACT.md",
    "build_output_artifact_navigation_report": "A_SHARE_BUILD_OUTPUT_ARTIFACT_NAVIGATION.md",
    "build_output_repeatability_card_report": "A_SHARE_BUILD_OUTPUT_REPEATABILITY_CARD.md",
    "validate_dashboard_vs_build_dashboard_report": "A_SHARE_VALIDATE_DASHBOARD_VS_BUILD_DASHBOARD.md",
    "build_output_dashboard_source_trace_report": "A_SHARE_BUILD_OUTPUT_DASHBOARD_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class BuildOutputDashboardConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_DASHBOARD
    allow_date_mismatch: bool = False
    allow_required_validate_fallback: bool = False
    allow_business_output_drift: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-BUILD-OUTPUT-OWNER-DASHBOARD-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "prefer_build_output": True,
            "allow_validate_fallback_for_required_artifacts": self.allow_required_validate_fallback,
            "allow_validate_fallback_for_optional_artifacts": True,
            "require_repeatability_audit_passed": True,
            "require_business_output_drift_count_zero": not self.allow_business_output_drift,
            "require_protected_path_modification_clean": True,
            "owner_facing": True,
            "machine_readable": True,
            "generate_markdown": True,
            "broker_enabled": False,
            "real_order_enabled": False,
            **FLAGS,
            "raw_config": asdict(self),
        }


def validate_config(config: BuildOutputDashboardConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_build_output_dashboard" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["build_output_dashboard_audit_json"] = (
        paths.data_dir / "equity_data_quality" / "a_share_build_output_owner_dashboard_audit.json"
    )
    artifacts["build_output_dashboard_audit_report"] = (
        paths.outputs_dir / "audit" / "A_SHARE_BUILD_OUTPUT_OWNER_DASHBOARD_AUDIT.md"
    )
    return artifacts

