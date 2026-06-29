"""Configuration for v0.8.7 A-share gated current-day build-from-existing-data dry-run."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.7-a-share-gated-current-day-build-from-existing-data-dry-run"
BASELINE_VERSION = "v0.8.6-a-share-ops-run-history-deepening-and-trend-baselines"
OPS_CENTER_VERSION = "v0.8.5-a-share-daily-ops-command-center"
CURRENT_DAY_VERSION = "v0.8.1-a-share-current-day-research-workflow-runner"
DATA_REFRESH_VERSION = "v0.8.0-a-share-daily-data-refresh-and-provider-hardening"
RECOMMENDED_NEXT_VERSION = "v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_GATED_BUILD_INPUTS = "validate_gated_build_inputs"
EVALUATE_PREFLIGHT_GATE = "evaluate_preflight_gate"
RUN_GATED_BUILD_FROM_EXISTING_DATA = "run_gated_build_from_existing_data"
COMPARE_VALIDATE_VS_BUILD_OUTPUTS = "compare_validate_vs_build_outputs"
AUDIT_EXISTING_GATED_BUILD = "audit_existing_gated_build"
ALLOWED_MODES = [
    VALIDATE_GATED_BUILD_INPUTS,
    EVALUATE_PREFLIGHT_GATE,
    RUN_GATED_BUILD_FROM_EXISTING_DATA,
    COMPARE_VALIDATE_VS_BUILD_OUTPUTS,
    AUDIT_EXISTING_GATED_BUILD,
]

FROM_WORKFLOW_MODE = "validate_existing_artifacts"
TO_WORKFLOW_MODE = "build_from_existing_data"
ALLOWED_WORKFLOW_MODES = [FROM_WORKFLOW_MODE, TO_WORKFLOW_MODE]

GATED_BUILD_FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

GATED_BUILD_BOUNDARY = {
    "gated_build_from_existing_data_only": True,
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
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "build_result_used_as_trade_instruction": False,
}

GATED_BUILD_FILES = {
    "gated_build_config": "gated_build_config.json",
    "gated_build_input_availability": "gated_build_input_availability.json",
    "gated_build_date_alignment": "gated_build_date_alignment.json",
    "preflight_gate": "preflight_gate.json",
    "gated_build_execution_plan": "gated_build_execution_plan.json",
    "gated_build_execution_record": "gated_build_execution_record.json",
    "build_from_existing_data_workflow_result": "build_from_existing_data_workflow_result.json",
    "build_from_existing_data_audit_link": "build_from_existing_data_audit_link.json",
    "build_artifact_index": "build_artifact_index.json",
    "validate_vs_build_comparison": "validate_vs_build_comparison.json",
    "artifact_drift_summary": "artifact_drift_summary.json",
    "gated_build_warning_summary": "gated_build_warning_summary.json",
    "gated_build_source_trace": "gated_build_source_trace.json",
    "gated_build_boundary_check": "gated_build_boundary_check.json",
    "gated_build_manifest": "gated_build_manifest.json",
    "gated_build_summary": "gated_build_summary.json",
}

GATED_BUILD_REPORTS = {
    "gated_build_dry_run_report": "A_SHARE_GATED_BUILD_FROM_EXISTING_DATA_DRY_RUN.md",
    "gated_build_preflight_report": "A_SHARE_GATED_BUILD_PREFLIGHT.md",
    "validate_vs_build_report": "A_SHARE_VALIDATE_VS_BUILD_COMPARISON.md",
    "artifact_drift_report": "A_SHARE_GATED_BUILD_ARTIFACT_DRIFT.md",
    "source_trace_report": "A_SHARE_GATED_BUILD_SOURCE_TRACE.md",
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

WORKFLOW_COMMAND_TEMPLATE = (
    "python -m trading_core.cli run-and-audit-a-share-current-day-research"
    " --as-of-date {as_of_date}"
    " --mode run_research_from_existing_refresh"
    " --workflow-mode build_from_existing_data"
)


@dataclass(frozen=True)
class GatedBuildConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = RUN_GATED_BUILD_FROM_EXISTING_DATA
    allow_date_mismatch: bool = False
    minimum_ops_health_score: int = 60
    allow_public_network_refresh: bool = False
    allow_full_research_run: bool = False
    allow_broker: bool = False
    allow_real_orders: bool = False
    allow_order_preview: bool = False
    allow_buy_sell_signals: bool = False
    allow_old_run_daily: bool = False
    execute_remediation_actions: bool = False
    execute_official_forward_dry_run_day2: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-DRY-RUN-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "from_workflow_mode": FROM_WORKFLOW_MODE,
            "to_workflow_mode": TO_WORKFLOW_MODE,
            "preflight_required": True,
            "preflight_passed_required": True,
            "gated_build_execution_allowed": self.mode == RUN_GATED_BUILD_FROM_EXISTING_DATA,
            "gated_build_execution_performed": False,
            "release_e2e_executes_build_from_existing_data": True,
            "allow_public_network_refresh": self.allow_public_network_refresh,
            "allow_full_research_run": self.allow_full_research_run,
            "allow_broker": self.allow_broker,
            "allow_real_orders": self.allow_real_orders,
            "allow_order_preview": self.allow_order_preview,
            "allow_buy_sell_signals": self.allow_buy_sell_signals,
            "allow_old_run_daily": self.allow_old_run_daily,
            "execute_official_forward_dry_run_day2": self.execute_official_forward_dry_run_day2,
            "minimum_ops_health_score": self.minimum_ops_health_score,
            **GATED_BUILD_FLAGS,
            "raw_config": asdict(self),
        }


def validate_gated_build_config(config: GatedBuildConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.allow_broker:
        issues.append("broker is not allowed in gated build")
    if config.allow_real_orders:
        issues.append("real orders are not allowed in gated build")
    if config.allow_old_run_daily:
        issues.append("old run-daily is not allowed in gated build")
    if config.execute_official_forward_dry_run_day2:
        issues.append("official forward dry-run day2 is not allowed in gated build")
    return issues


def gated_build_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_current_day_builds" / "daily" / as_of_date


def gated_build_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_current_day_builds" / "daily" / as_of_date


def gated_build_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = gated_build_data_dir(paths, as_of_date)
    output_dir = gated_build_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in GATED_BUILD_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in GATED_BUILD_REPORTS.items()})
    artifacts["gated_build_audit_json"] = (
        paths.data_dir / "equity_data_quality" / "a_share_gated_build_from_existing_data_audit.json"
    )
    artifacts["gated_build_audit_report"] = (
        paths.outputs_dir / "audit" / "A_SHARE_GATED_BUILD_FROM_EXISTING_DATA_AUDIT.md"
    )
    return artifacts
