"""Configuration for v0.8.4 A-share owner remediation runbooks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist"
BASELINE_MONITORING_VERSION = "v0.8.3-a-share-owner-alerting-and-run-history-monitoring"
RECOMMENDED_NEXT_VERSION = "v0.8.5-a-share-daily-ops-command-center"
REMEDIATION_VERSION = "v0.8.4.1-a-share-owner-remediation-follow-up"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_REMEDIATION_INPUTS = "validate_remediation_inputs"
BUILD_REMEDIATION_RUNBOOK = "build_remediation_runbook"
BUILD_SAFE_ACTION_CHECKLIST = "build_safe_action_checklist"
AUDIT_EXISTING_REMEDIATION = "audit_existing_remediation"
ALLOWED_MODES = [
    VALIDATE_REMEDIATION_INPUTS,
    BUILD_REMEDIATION_RUNBOOK,
    BUILD_SAFE_ACTION_CHECKLIST,
    AUDIT_EXISTING_REMEDIATION,
]

REMEDIATION_FLAGS = {
    "owner_facing": True,
    "machine_readable": True,
    "generate_markdown": True,
    "generate_safe_action_checklist": True,
    "generate_dry_run_plan": True,
    "execute_remediation_actions": False,
    "send_external_notifications": False,
    "notification_channels_enabled": [],
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
    "broker_enabled": False,
    "real_order_enabled": False,
}

REMEDIATION_BOUNDARY = {
    "owner_remediation_only": True,
    "runbook_only": True,
    "checklist_only": True,
    "execute_remediation_actions": False,
    "external_notifications_sent": False,
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
    "alert_used_as_trade_instruction": False,
    "remediation_used_as_trade_instruction": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_PATH_TOKENS = {"broker", "orders", "trades", "accounts", "run_daily", "day_002", "day_003", "real_order", "broker_order"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]
FORBIDDEN_ACTION_TYPES = {
    "place_order",
    "cancel_order",
    "rebalance_account",
    "buy_stock",
    "sell_stock",
    "connect_broker",
    "read_real_account",
    "enable_live_trading",
}
ALLOWED_SAFE_ACTION_TYPES = {
    "inspect_artifact",
    "verify_audit",
    "check_data_freshness",
    "check_provider_status",
    "rerun_safe_data_validation",
    "rerun_safe_current_day_research_validation",
    "rerun_safe_dashboard_build",
    "rerun_safe_monitoring_build",
    "wait_for_more_history",
    "document_known_warning",
    "escalate_to_developer",
}

REMEDIATION_FILES = {
    "remediation_config": "remediation_config.json",
    "remediation_input_availability": "remediation_input_availability.json",
    "issue_catalog": "issue_catalog.json",
    "warning_remediation_map": "warning_remediation_map.json",
    "blocking_remediation_map": "blocking_remediation_map.json",
    "alert_remediation_map": "alert_remediation_map.json",
    "provider_remediation_guide": "provider_remediation_guide.json",
    "data_freshness_remediation_guide": "data_freshness_remediation_guide.json",
    "schema_coverage_remediation_guide": "schema_coverage_remediation_guide.json",
    "workflow_remediation_guide": "workflow_remediation_guide.json",
    "dashboard_remediation_guide": "dashboard_remediation_guide.json",
    "monitoring_remediation_guide": "monitoring_remediation_guide.json",
    "safe_owner_action_checklist": "safe_owner_action_checklist.json",
    "manual_verification_checklist": "manual_verification_checklist.json",
    "non_actionable_issue_list": "non_actionable_issue_list.json",
    "dry_run_remediation_plan": "dry_run_remediation_plan.json",
    "remediation_priority_summary": "remediation_priority_summary.json",
    "remediation_source_trace": "remediation_source_trace.json",
    "remediation_boundary_check": "remediation_boundary_check.json",
    "remediation_manifest": "remediation_manifest.json",
    "remediation_summary": "remediation_summary.json",
}

REMEDIATION_REPORTS = {
    "owner_remediation_runbook_report": "A_SHARE_OWNER_REMEDIATION_RUNBOOK.md",
    "safe_action_checklist_report": "A_SHARE_SAFE_ACTION_CHECKLIST.md",
    "data_remediation_guide_report": "A_SHARE_DATA_REMEDIATION_GUIDE.md",
    "workflow_remediation_guide_report": "A_SHARE_WORKFLOW_REMEDIATION_GUIDE.md",
    "remediation_source_trace_report": "A_SHARE_REMEDIATION_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class OwnerRemediationConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    resolved_as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_REMEDIATION_RUNBOOK
    allow_date_mismatch: bool = False
    allow_safe_local_dry_run: bool = False
    allow_data_refresh_rerun: bool = False
    allow_research_workflow_rerun: bool = False
    allow_dashboard_rerun: bool = False
    allow_monitoring_rerun: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-REMEDIATION-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "resolved_as_of_date": self.resolved_as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "allow_date_mismatch": self.allow_date_mismatch,
            "allow_safe_local_dry_run": self.allow_safe_local_dry_run,
            "allow_data_refresh_rerun": self.allow_data_refresh_rerun,
            "allow_research_workflow_rerun": self.allow_research_workflow_rerun,
            "allow_dashboard_rerun": self.allow_dashboard_rerun,
            "allow_monitoring_rerun": self.allow_monitoring_rerun,
            **REMEDIATION_FLAGS,
            "raw_config": asdict(self),
        }


def validate_remediation_config(config: OwnerRemediationConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if not config.resolved_as_of_date or len(config.resolved_as_of_date) != 10:
        issues.append("resolved_as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.as_of_date != config.resolved_as_of_date and not config.allow_date_mismatch:
        issues.append("resolved_as_of_date differs from as_of_date; pass allow_date_mismatch to proceed")
    return issues


def remediation_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_remediation" / "daily" / as_of_date


def remediation_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_remediation" / "daily" / as_of_date


def remediation_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = remediation_data_dir(paths, as_of_date)
    output_dir = remediation_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in REMEDIATION_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in REMEDIATION_REPORTS.items()})
    artifacts["remediation_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_remediation_audit.json"
    artifacts["remediation_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_REMEDIATION_AUDIT.md"
    return artifacts
