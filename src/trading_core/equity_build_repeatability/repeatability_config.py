"""Configuration for v0.8.8 build repeatability checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability"
BASELINE_VERSION = "v0.8.7-a-share-gated-current-day-build-from-existing-data-dry-run"
RECOMMENDED_NEXT_VERSION = "v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_REPEATABILITY_INPUTS = "validate_repeatability_inputs"
SNAPSHOT_PROTECTED_PATHS = "snapshot_protected_paths"
RUN_REPEAT_BUILD_FROM_EXISTING_DATA = "run_repeat_build_from_existing_data"
COMPARE_BUILD_REPEATS = "compare_build_repeats"
AUDIT_EXISTING_REPEATABILITY = "audit_existing_repeatability"
ALLOWED_MODES = [
    VALIDATE_REPEATABILITY_INPUTS,
    SNAPSHOT_PROTECTED_PATHS,
    RUN_REPEAT_BUILD_FROM_EXISTING_DATA,
    COMPARE_BUILD_REPEATS,
    AUDIT_EXISTING_REPEATABILITY,
]

WORKFLOW_MODE = "build_from_existing_data"
WORKFLOW_COMMAND_TEMPLATE = (
    "python -m trading_core.cli run-and-audit-a-share-current-day-research"
    " --as-of-date {as_of_date}"
    " --mode run_research_from_existing_refresh"
    " --workflow-mode build_from_existing_data"
)

REPEATABILITY_FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

REPEATABILITY_BOUNDARY = {
    "repeatability_only": True,
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
    "build_repeatability_used_as_trade_instruction": False,
}

REPEATABILITY_FILES = {
    "repeatability_config": "repeatability_config.json",
    "repeatability_input_availability": "repeatability_input_availability.json",
    "repeatability_date_alignment": "repeatability_date_alignment.json",
    "protected_path_pre_run_snapshot": "protected_path_pre_run_snapshot.json",
    "repeat_build_execution_plan": "repeat_build_execution_plan.json",
    "repeat_build_execution_record": "repeat_build_execution_record.json",
    "repeat_build_workflow_result": "repeat_build_workflow_result.json",
    "protected_path_post_run_snapshot": "protected_path_post_run_snapshot.json",
    "protected_path_modification_check": "protected_path_modification_check.json",
    "first_build_artifact_snapshot": "first_build_artifact_snapshot.json",
    "second_build_artifact_snapshot": "second_build_artifact_snapshot.json",
    "build_vs_build_comparison": "build_vs_build_comparison.json",
    "repeatability_drift_summary": "repeatability_drift_summary.json",
    "deterministic_field_normalization": "deterministic_field_normalization.json",
    "repeatability_warning_comparison": "repeatability_warning_comparison.json",
    "repeatability_source_trace": "repeatability_source_trace.json",
    "repeatability_boundary_check": "repeatability_boundary_check.json",
    "repeatability_manifest": "repeatability_manifest.json",
    "repeatability_summary": "repeatability_summary.json",
}

REPEATABILITY_REPORTS = {
    "repeatability_report": "A_SHARE_BUILD_REPEATABILITY_REPORT.md",
    "build_vs_build_report": "A_SHARE_BUILD_VS_BUILD_COMPARISON.md",
    "drift_summary_report": "A_SHARE_REPEATABILITY_DRIFT_SUMMARY.md",
    "protected_path_report": "A_SHARE_PROTECTED_PATH_MODIFICATION_CHECK.md",
    "source_trace_report": "A_SHARE_REPEATABILITY_SOURCE_TRACE.md",
}

PROTECTED_PATHS = [
    "data/orders",
    "data/trades",
    "data/accounts",
    "outputs/orders",
    "outputs/trades",
    "outputs/accounts",
]

FORBIDDEN_ARTIFACT_NAMES = {
    "BROKER_ORDER.json",
    "REAL_ORDER.json",
    "ORDER_PREVIEW.md",
    "BUY_LIST.md",
    "SELL_LIST.md",
}

FORBIDDEN_COMMAND_FRAGMENTS = [
    "run-daily",
    "broker",
    "order",
    "trade",
    "easytrader",
    "thstrader",
    "buy",
    "sell",
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
]


@dataclass(frozen=True)
class RepeatabilityConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = RUN_REPEAT_BUILD_FROM_EXISTING_DATA
    allow_date_mismatch: bool = False
    allow_business_output_drift: bool = False
    allow_public_network_refresh: bool = False
    allow_full_research_run: bool = False
    allow_broker: bool = False
    allow_real_orders: bool = False
    allow_order_preview: bool = False
    allow_buy_sell_signals: bool = False
    allow_old_run_daily: bool = False
    execute_official_forward_dry_run_day2: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-BUILD-REPEATABILITY-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "workflow_mode": WORKFLOW_MODE,
            "repeat_build_execution_required": True,
            "compare_against_first_gated_build": True,
            "allow_timestamp_drift": True,
            "allow_metadata_hash_drift": True,
            "allow_business_output_drift": self.allow_business_output_drift,
            "allow_missing_required_artifacts": False,
            "allow_boundary_drift": False,
            "allow_source_trace_missing": False,
            "distinguish_preexisting_protected_paths": True,
            "allow_preexisting_protected_paths": True,
            "allow_protected_path_modifications": False,
            "allow_public_network_refresh": self.allow_public_network_refresh,
            "allow_full_research_run": self.allow_full_research_run,
            "allow_broker": self.allow_broker,
            "allow_real_orders": self.allow_real_orders,
            "allow_order_preview": self.allow_order_preview,
            "allow_buy_sell_signals": self.allow_buy_sell_signals,
            "allow_old_run_daily": self.allow_old_run_daily,
            "execute_official_forward_dry_run_day2": self.execute_official_forward_dry_run_day2,
            "external_notifications_sent": False,
            **REPEATABILITY_FLAGS,
            "raw_config": asdict(self),
        }


def validate_repeatability_config(config: RepeatabilityConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.allow_public_network_refresh:
        issues.append("public network refresh is not allowed in repeatability checks")
    if config.allow_full_research_run:
        issues.append("full_research_run is not allowed in repeatability checks")
    if config.allow_broker:
        issues.append("broker is not allowed in repeatability checks")
    if config.allow_real_orders:
        issues.append("real orders are not allowed in repeatability checks")
    if config.allow_order_preview:
        issues.append("order preview is not allowed in repeatability checks")
    if config.allow_buy_sell_signals:
        issues.append("buy/sell signals are not allowed in repeatability checks")
    if config.allow_old_run_daily:
        issues.append("old run-daily is not allowed in repeatability checks")
    if config.execute_official_forward_dry_run_day2:
        issues.append("official forward dry-run day2 is not allowed in repeatability checks")
    return issues


def repeatability_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_build_repeatability" / "daily" / as_of_date


def repeatability_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_build_repeatability" / "daily" / as_of_date


def repeatability_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = repeatability_data_dir(paths, as_of_date)
    output_dir = repeatability_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in REPEATABILITY_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in REPEATABILITY_REPORTS.items()})
    artifacts["repeatability_audit_json"] = (
        paths.data_dir / "equity_data_quality" / "a_share_build_repeatability_audit.json"
    )
    artifacts["repeatability_audit_report"] = (
        paths.outputs_dir / "audit" / "A_SHARE_BUILD_REPEATABILITY_AUDIT.md"
    )
    return artifacts

