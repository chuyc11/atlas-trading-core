"""Configuration for v0.8.5 A-share daily ops command center."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.5-a-share-daily-ops-command-center"
BASELINE_REMEDIATION_VERSION = "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist"
RECOMMENDED_NEXT_VERSION = "v0.8.6-a-share-ops-run-history-deepening-and-trend-baselines"
REMEDIATION_VERSION = "v0.8.5.1-a-share-daily-ops-center-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_OPS_INPUTS = "validate_ops_inputs"
BUILD_OPS_PLAN = "build_ops_plan"
AGGREGATE_EXISTING_OPS_ARTIFACTS = "aggregate_existing_ops_artifacts"
RUN_SAFE_OPS_VALIDATION_CHAIN = "run_safe_ops_validation_chain"
AUDIT_EXISTING_OPS_CENTER = "audit_existing_ops_center"
ALLOWED_MODES = [
    VALIDATE_OPS_INPUTS,
    BUILD_OPS_PLAN,
    AGGREGATE_EXISTING_OPS_ARTIFACTS,
    RUN_SAFE_OPS_VALIDATION_CHAIN,
    AUDIT_EXISTING_OPS_CENTER,
]

OPS_FLAGS = {
    "owner_facing": True,
    "machine_readable": True,
    "generate_markdown": True,
    "aggregate_existing_artifacts_only": True,
    "allow_data_refresh_run": False,
    "allow_current_day_research_run": False,
    "allow_dashboard_build": False,
    "allow_monitoring_build": False,
    "allow_remediation_build": False,
    "execute_remediation_actions": False,
    "send_external_notifications": False,
    "commands_executed": [],
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
    "broker_enabled": False,
    "real_order_enabled": False,
}

OPS_BOUNDARY = {
    "ops_center_only": True,
    "aggregate_existing_artifacts_only": True,
    "commands_executed": [],
    "safe_validation_chain_run": False,
    "data_refresh_run": False,
    "current_day_research_run": False,
    "dashboard_build_run": False,
    "monitoring_build_run": False,
    "remediation_build_run": False,
    "remediation_actions_executed": False,
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
    "ops_used_as_trade_instruction": False,
}

MODULE_IDS = ["data_refresh", "current_day_research_run", "owner_dashboard", "owner_monitoring", "owner_remediation"]
FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_PATH_TOKENS = {"broker", "orders", "trades", "accounts", "run_daily", "day_002", "day_003", "real_order", "broker_order"}
FORBIDDEN_COMMAND_TOKENS = {"run-daily", "broker", "order", "trade", "easytrader", "thstrader", "buy", "sell"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]

OPS_FILES = {
    "ops_center_config": "ops_center_config.json",
    "ops_input_availability": "ops_input_availability.json",
    "ops_date_alignment": "ops_date_alignment.json",
    "ops_plan": "ops_plan.json",
    "ops_execution_record": "ops_execution_record.json",
    "ops_health_score_card": "ops_health_score_card.json",
    "ops_module_status_matrix": "ops_module_status_matrix.json",
    "ops_issue_summary": "ops_issue_summary.json",
    "ops_action_summary": "ops_action_summary.json",
    "ops_artifact_navigation": "ops_artifact_navigation.json",
    "ops_command_reference": "ops_command_reference.json",
    "ops_owner_next_steps": "ops_owner_next_steps.json",
    "ops_source_trace": "ops_source_trace.json",
    "ops_boundary_check": "ops_boundary_check.json",
    "ops_manifest": "ops_manifest.json",
    "ops_summary": "ops_summary.json",
}

OPS_REPORTS = {
    "ops_command_center_report": "A_SHARE_DAILY_OPS_COMMAND_CENTER.md",
    "ops_compact_report": "A_SHARE_DAILY_OPS_COMPACT.md",
    "ops_module_status_report": "A_SHARE_OPS_MODULE_STATUS.md",
    "ops_action_summary_report": "A_SHARE_OPS_ACTION_SUMMARY.md",
    "ops_artifact_navigation_report": "A_SHARE_OPS_ARTIFACT_NAVIGATION.md",
    "ops_source_trace_report": "A_SHARE_OPS_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class OpsCenterConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = AGGREGATE_EXISTING_OPS_ARTIFACTS
    allow_date_mismatch: bool = False
    allow_safe_validation_chain: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-DAILY-OPS-CENTER-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "allow_date_mismatch": self.allow_date_mismatch,
            "allow_safe_validation_chain": self.allow_safe_validation_chain,
            **OPS_FLAGS,
            "raw_config": asdict(self),
        }


def validate_ops_config(config: OpsCenterConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.mode == RUN_SAFE_OPS_VALIDATION_CHAIN and not config.allow_safe_validation_chain:
        issues.append("run_safe_ops_validation_chain requires allow_safe_validation_chain=true")
    return issues


def ops_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_ops_center" / "daily" / as_of_date


def ops_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_ops_center" / "daily" / as_of_date


def ops_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = ops_data_dir(paths, as_of_date)
    output_dir = ops_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in OPS_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in OPS_REPORTS.items()})
    artifacts["ops_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_daily_ops_center_audit.json"
    artifacts["ops_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_DAILY_OPS_CENTER_AUDIT.md"
    return artifacts
