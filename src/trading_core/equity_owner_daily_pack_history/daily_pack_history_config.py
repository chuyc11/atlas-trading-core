"""Configuration for v0.8.12 owner daily pack history."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.12-a-share-build-output-daily-pack-history-and-owner-readiness-trends"
BASELINE_VERSION = "v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack"
RECOMMENDED_NEXT_VERSION = "v0.8.13-a-share-owner-readiness-gate-and-daily-pack-quality-thresholds"
DEFAULT_AS_OF_DATE = "2026-06-26"
DEFAULT_HISTORY_WINDOW_DAYS = 90
DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS = 5
DEFAULT_BASELINE_WINDOW_OBSERVATIONS = 20

VALIDATE_INPUTS = "validate_daily_pack_history_inputs"
APPEND_HISTORY = "append_current_daily_pack_to_history"
BUILD_TRENDS = "build_owner_readiness_trends"
BUILD_REPORT = "build_daily_pack_history_report"
AUDIT_EXISTING = "audit_existing_daily_pack_history"
ALLOWED_MODES = [VALIDATE_INPUTS, APPEND_HISTORY, BUILD_TRENDS, BUILD_REPORT, AUDIT_EXISTING]
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

BOUNDARY = {
    "daily_pack_history_only": True,
    "owner_readiness_trends_only": True,
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
    "build_from_existing_data_rerun": False,
    "owner_daily_pack_rerun": False,
    "ops_refresh_rerun": False,
    "execute_remediation_actions": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "owner_readiness_used_as_trade_instruction": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]
FORBIDDEN_SAFE_ACTION_MARKERS = ["broker", "order", "trade", "buy", "sell", "下单", "买入", "卖出", "实盘"]

FILES = {
    "daily_pack_history_config": "daily_pack_history_config.json",
    "daily_pack_history_input_availability": "daily_pack_history_input_availability.json",
    "daily_pack_history_source_resolution": "daily_pack_history_source_resolution.json",
    "daily_pack_history_date_alignment": "daily_pack_history_date_alignment.json",
    "daily_pack_run_record": "daily_pack_run_record.json",
    "daily_pack_history_append_result": "daily_pack_history_append_result.json",
    "daily_pack_history_snapshot": "daily_pack_history_snapshot.json",
    "owner_readiness_score": "owner_readiness_score.json",
    "owner_readiness_history": "owner_readiness_history.json",
    "owner_readiness_trend_sufficiency": "owner_readiness_trend_sufficiency.json",
    "daily_pack_quality_baseline": "daily_pack_quality_baseline.json",
    "warning_issue_trend_baseline": "warning_issue_trend_baseline.json",
    "safe_action_trend_baseline": "safe_action_trend_baseline.json",
    "protected_path_trend_baseline": "protected_path_trend_baseline.json",
    "boundary_trend_baseline": "boundary_trend_baseline.json",
    "source_trace_quality_trend": "source_trace_quality_trend.json",
    "daily_pack_completeness_trend": "daily_pack_completeness_trend.json",
    "owner_next_step_trend": "owner_next_step_trend.json",
    "daily_pack_history_source_trace": "daily_pack_history_source_trace.json",
    "daily_pack_history_boundary_check": "daily_pack_history_boundary_check.json",
    "daily_pack_history_manifest": "daily_pack_history_manifest.json",
    "daily_pack_history_summary": "daily_pack_history_summary.json",
}

INDEX_FILES = {
    "daily_pack_history_index": "daily_pack_history_index.json",
    "owner_readiness_history_index": "owner_readiness_history_index.json",
    "daily_pack_quality_history_index": "daily_pack_quality_history_index.json",
    "warning_issue_history_index": "warning_issue_history_index.json",
    "safe_action_history_index": "safe_action_history_index.json",
    "protected_path_history_index": "protected_path_history_index.json",
    "boundary_history_index": "boundary_history_index.json",
    "source_trace_quality_history_index": "source_trace_quality_history_index.json",
}

REPORTS = {
    "daily_pack_history_report": "A_SHARE_OWNER_DAILY_PACK_HISTORY.md",
    "owner_readiness_trends_report": "A_SHARE_OWNER_READINESS_TRENDS.md",
    "daily_pack_quality_baseline_report": "A_SHARE_DAILY_PACK_QUALITY_BASELINE.md",
    "warning_safe_action_trends_report": "A_SHARE_DAILY_PACK_WARNING_SAFE_ACTION_TRENDS.md",
    "daily_pack_history_source_trace_report": "A_SHARE_DAILY_PACK_HISTORY_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class DailyPackHistoryConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_TRENDS
    history_window_days: int = DEFAULT_HISTORY_WINDOW_DAYS
    minimum_required_observations: int = DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS
    baseline_window_observations: int = DEFAULT_BASELINE_WINDOW_OBSERVATIONS
    allow_date_mismatch: bool = False
    allow_rebuild_history: bool = False
    allow_synthetic_history: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "history_window_days": self.history_window_days,
            "minimum_required_observations": self.minimum_required_observations,
            "baseline_window_observations": self.baseline_window_observations,
            "append_only_history": True,
            "allow_rebuild_history": self.allow_rebuild_history,
            "allow_synthetic_history": self.allow_synthetic_history,
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
            "raw_config": asdict(self),
        }


def validate_config(config: DailyPackHistoryConfig) -> list[str]:
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


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_daily_pack_history" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_daily_pack_history" / "daily" / as_of_date


def history_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_owner_daily_pack_history" / "history"


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    hdir = history_dir(paths)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: hdir / name for key, name in INDEX_FILES.items()})
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["daily_pack_history_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_daily_pack_history_audit.json"
    artifacts["daily_pack_history_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_DAILY_PACK_HISTORY_AUDIT.md"
    return artifacts
