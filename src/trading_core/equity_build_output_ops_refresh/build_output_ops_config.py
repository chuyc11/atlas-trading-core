"""Configuration for v0.8.10 build-output ops refresh."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh"
BASELINE_VERSION = "v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh"
RECOMMENDED_NEXT_VERSION = "v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_INPUTS = "validate_build_output_ops_refresh_inputs"
RESOLVE_SOURCES = "resolve_build_output_ops_sources"
BUILD_REFRESH = "build_build_output_monitoring_remediation_ops_refresh"
COMPARE_OPS = "compare_original_ops_vs_build_output_ops"
AUDIT_EXISTING = "audit_existing_build_output_ops_refresh"
ALLOWED_MODES = [VALIDATE_INPUTS, RESOLVE_SOURCES, BUILD_REFRESH, COMPARE_OPS, AUDIT_EXISTING]

SOURCE_WORKFLOW_MODE = "build_from_existing_data"

BOUNDARY = {
    "build_output_ops_refresh_only": True,
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
    "ops_refresh_used_as_trade_instruction": False,
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
    "build_output_ops_refresh_config": "build_output_ops_refresh_config.json",
    "build_output_ops_input_availability": "build_output_ops_input_availability.json",
    "build_output_ops_source_resolution": "build_output_ops_source_resolution.json",
    "build_output_ops_date_alignment": "build_output_ops_date_alignment.json",
    "build_output_monitoring_refresh": "build_output_monitoring_refresh.json",
    "build_output_alert_summary_refresh": "build_output_alert_summary_refresh.json",
    "build_output_remediation_refresh": "build_output_remediation_refresh.json",
    "build_output_safe_action_refresh": "build_output_safe_action_refresh.json",
    "build_output_ops_center_refresh": "build_output_ops_center_refresh.json",
    "build_output_ops_history_refresh": "build_output_ops_history_refresh.json",
    "build_output_health_score_refresh": "build_output_health_score_refresh.json",
    "build_output_module_status_matrix_refresh": "build_output_module_status_matrix_refresh.json",
    "build_output_issue_summary_refresh": "build_output_issue_summary_refresh.json",
    "build_output_action_summary_refresh": "build_output_action_summary_refresh.json",
    "build_output_owner_next_steps_refresh": "build_output_owner_next_steps_refresh.json",
    "original_ops_vs_build_output_ops_comparison": "original_ops_vs_build_output_ops_comparison.json",
    "build_output_ops_artifact_navigation": "build_output_ops_artifact_navigation.json",
    "build_output_ops_source_trace": "build_output_ops_source_trace.json",
    "build_output_ops_boundary_check": "build_output_ops_boundary_check.json",
    "build_output_ops_manifest": "build_output_ops_manifest.json",
    "build_output_ops_summary": "build_output_ops_summary.json",
}

REPORTS = {
    "build_output_ops_refresh_report": "A_SHARE_BUILD_OUTPUT_OPS_REFRESH.md",
    "build_output_monitoring_refresh_report": "A_SHARE_BUILD_OUTPUT_MONITORING_REFRESH.md",
    "build_output_remediation_refresh_report": "A_SHARE_BUILD_OUTPUT_REMEDIATION_REFRESH.md",
    "build_output_ops_center_refresh_report": "A_SHARE_BUILD_OUTPUT_OPS_CENTER_REFRESH.md",
    "original_ops_vs_build_output_ops_report": "A_SHARE_ORIGINAL_OPS_VS_BUILD_OUTPUT_OPS.md",
    "build_output_ops_source_trace_report": "A_SHARE_BUILD_OUTPUT_OPS_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class BuildOutputOpsRefreshConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_REFRESH
    allow_date_mismatch: bool = False
    allow_business_output_drift: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "prefer_build_output_dashboard": True,
            "refresh_monitoring_from_build_output": True,
            "refresh_remediation_from_build_output": True,
            "refresh_ops_center_from_build_output": True,
            "refresh_ops_history_from_build_output": True,
            "rerun_build_from_existing_data": False,
            "rerun_original_monitoring": False,
            "rerun_original_remediation": False,
            "rerun_original_ops_center": False,
            "execute_remediation_actions": False,
            "send_external_notifications": False,
            "allow_business_output_drift": self.allow_business_output_drift,
            "allow_protected_path_modifications": False,
            "allow_public_network_refresh": False,
            "allow_full_research_run": False,
            "allow_broker": False,
            "allow_real_orders": False,
            "allow_order_preview": False,
            "allow_buy_sell_signals": False,
            "allow_old_run_daily": False,
            "execute_official_forward_dry_run_day2": False,
            **FLAGS,
            "raw_config": asdict(self),
        }


def validate_config(config: BuildOutputOpsRefreshConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["build_output_ops_audit_json"] = (
        paths.data_dir / "equity_data_quality" / "a_share_build_output_ops_refresh_audit.json"
    )
    artifacts["build_output_ops_audit_report"] = (
        paths.outputs_dir / "audit" / "A_SHARE_BUILD_OUTPUT_OPS_REFRESH_AUDIT.md"
    )
    return artifacts

