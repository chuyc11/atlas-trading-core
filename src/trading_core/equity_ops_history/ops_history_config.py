"""Configuration for v0.8.6 ops run-history baselines."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.6-a-share-ops-run-history-deepening-and-trend-baselines"
BASELINE_OPS_VERSION = "v0.8.5-a-share-daily-ops-command-center"
RECOMMENDED_NEXT_VERSION = "v0.8.7-a-share-current-day-build-from-existing-data-promotion-gate"
REMEDIATION_VERSION = "v0.8.6.1-a-share-ops-history-baseline-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"
DEFAULT_HISTORY_WINDOW_DAYS = 90
DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS = 5
DEFAULT_BASELINE_WINDOW_OBSERVATIONS = 20

VALIDATE_HISTORY_INPUTS = "validate_history_inputs"
APPEND_CURRENT_OPS_RUN_TO_HISTORY = "append_current_ops_run_to_history"
BUILD_TREND_BASELINES = "build_trend_baselines"
BUILD_HISTORY_BASELINE_REPORT = "build_history_baseline_report"
AUDIT_EXISTING_HISTORY_BASELINES = "audit_existing_history_baselines"
ALLOWED_MODES = [
    VALIDATE_HISTORY_INPUTS,
    APPEND_CURRENT_OPS_RUN_TO_HISTORY,
    BUILD_TREND_BASELINES,
    BUILD_HISTORY_BASELINE_REPORT,
    AUDIT_EXISTING_HISTORY_BASELINES,
]

OPS_HISTORY_FLAGS = {
    "append_only_history": True,
    "allow_rebuild_history": False,
    "allow_synthetic_history": False,
    "allow_future_dates": False,
    "owner_facing": True,
    "machine_readable": True,
    "generate_markdown": True,
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
    "broker_enabled": False,
    "real_order_enabled": False,
}

OPS_HISTORY_BOUNDARY = {
    "ops_history_only": True,
    "trend_baseline_only": True,
    "append_only_history": True,
    "synthetic_history_used": False,
    "future_dates_used": False,
    "commands_executed": [],
    "data_refresh_run": False,
    "current_day_research_run": False,
    "dashboard_build_run": False,
    "monitoring_build_run": False,
    "remediation_build_run": False,
    "ops_center_build_run": False,
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
    "trend_baseline_used_as_trade_instruction": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_PATH_TOKENS = {"broker", "orders", "trades", "accounts", "run_daily", "day_002", "day_003", "real_order", "broker_order"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]

OPS_HISTORY_FILES = {
    "ops_history_config": "ops_history_config.json",
    "ops_history_input_availability": "ops_history_input_availability.json",
    "ops_run_record": "ops_run_record.json",
    "ops_history_append_result": "ops_history_append_result.json",
    "ops_history_snapshot": "ops_history_snapshot.json",
    "ops_trend_baseline_config": "ops_trend_baseline_config.json",
    "ops_trend_sufficiency": "ops_trend_sufficiency.json",
    "ops_health_score_history": "ops_health_score_history.json",
    "ops_health_score_baseline": "ops_health_score_baseline.json",
    "ops_module_reliability_baseline": "ops_module_reliability_baseline.json",
    "ops_warning_recurrence_baseline": "ops_warning_recurrence_baseline.json",
    "ops_issue_recurrence_baseline": "ops_issue_recurrence_baseline.json",
    "ops_action_recurrence_baseline": "ops_action_recurrence_baseline.json",
    "ops_boundary_history_snapshot": "ops_boundary_history_snapshot.json",
    "ops_baseline_drift_snapshot": "ops_baseline_drift_snapshot.json",
    "ops_history_source_trace": "ops_history_source_trace.json",
    "ops_history_boundary_check": "ops_history_boundary_check.json",
    "ops_history_manifest": "ops_history_manifest.json",
    "ops_history_summary": "ops_history_summary.json",
}

OPS_HISTORY_INDEX_FILES = {
    "ops_run_history_index": "ops_run_history_index.json",
    "ops_health_score_history_index": "ops_health_score_history_index.json",
    "ops_module_status_history_index": "ops_module_status_history_index.json",
    "ops_warning_history_index": "ops_warning_history_index.json",
    "ops_issue_history_index": "ops_issue_history_index.json",
    "ops_action_history_index": "ops_action_history_index.json",
    "ops_boundary_history_index": "ops_boundary_history_index.json",
}

OPS_HISTORY_REPORTS = {
    "ops_run_history_baseline_report": "A_SHARE_OPS_RUN_HISTORY_BASELINE.md",
    "ops_health_score_baseline_report": "A_SHARE_OPS_HEALTH_SCORE_BASELINE.md",
    "ops_warning_issue_baseline_report": "A_SHARE_OPS_WARNING_ISSUE_BASELINE.md",
    "ops_module_reliability_baseline_report": "A_SHARE_OPS_MODULE_RELIABILITY_BASELINE.md",
    "ops_history_source_trace_report": "A_SHARE_OPS_HISTORY_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class OpsHistoryConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_TREND_BASELINES
    history_window_days: int = DEFAULT_HISTORY_WINDOW_DAYS
    minimum_required_observations: int = DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS
    baseline_window_observations: int = DEFAULT_BASELINE_WINDOW_OBSERVATIONS
    allow_rebuild_history: bool = False
    allow_synthetic_history: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OPS-HISTORY-BASELINE-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "history_window_days": self.history_window_days,
            "minimum_required_observations": self.minimum_required_observations,
            "baseline_window_observations": self.baseline_window_observations,
            **{**OPS_HISTORY_FLAGS, "allow_rebuild_history": self.allow_rebuild_history, "allow_synthetic_history": self.allow_synthetic_history},
            "raw_config": asdict(self),
        }


def validate_ops_history_config(config: OpsHistoryConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if config.history_window_days <= 0:
        issues.append("history_window_days must be positive")
    if config.minimum_required_observations <= 0:
        issues.append("minimum_required_observations must be positive")
    if config.baseline_window_observations <= 0:
        issues.append("baseline_window_observations must be positive")
    return issues


def ops_history_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_ops_history" / "daily" / as_of_date


def ops_history_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_ops_history" / "daily" / as_of_date


def ops_history_index_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_ops_history" / "history"


def ops_history_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = ops_history_data_dir(paths, as_of_date)
    output_dir = ops_history_output_dir(paths, as_of_date)
    history_dir = ops_history_index_dir(paths)
    artifacts = {key: data_dir / filename for key, filename in OPS_HISTORY_FILES.items()}
    artifacts.update({key: history_dir / filename for key, filename in OPS_HISTORY_INDEX_FILES.items()})
    artifacts.update({key: output_dir / filename for key, filename in OPS_HISTORY_REPORTS.items()})
    artifacts["ops_history_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_ops_history_baseline_audit.json"
    artifacts["ops_history_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OPS_HISTORY_BASELINE_AUDIT.md"
    return artifacts
