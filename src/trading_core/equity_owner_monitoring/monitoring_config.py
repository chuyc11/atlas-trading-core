"""Configuration for v0.8.3 A-share owner monitoring."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.3-a-share-owner-alerting-and-run-history-monitoring"
BASELINE_DASHBOARD_VERSION = "v0.8.2-a-share-current-day-owner-briefing-and-monitoring-dashboard"
RECOMMENDED_NEXT_VERSION = "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist"
REMEDIATION_VERSION = "v0.8.3.1-a-share-owner-monitoring-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"
DEFAULT_HISTORY_WINDOW_DAYS = 30
DEFAULT_MINIMUM_HISTORY_OBSERVATIONS = 3

VALIDATE_MONITORING_INPUTS = "validate_monitoring_inputs"
BUILD_RUN_HISTORY_FROM_EXISTING_ARTIFACTS = "build_run_history_from_existing_artifacts"
EVALUATE_OWNER_ALERTS = "evaluate_owner_alerts"
BUILD_MONITORING_DASHBOARD = "build_monitoring_dashboard"
ALLOWED_MODES = [
    VALIDATE_MONITORING_INPUTS,
    BUILD_RUN_HISTORY_FROM_EXISTING_ARTIFACTS,
    EVALUATE_OWNER_ALERTS,
    BUILD_MONITORING_DASHBOARD,
]

MONITORING_FLAGS = {
    "owner_facing": True,
    "machine_readable": True,
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
    "broker_enabled": False,
    "real_order_enabled": False,
}

MONITORING_BOUNDARY = {
    "owner_monitoring_only": True,
    "local_alert_artifacts_only": True,
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
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_PATH_TOKENS = {"broker", "orders", "trades", "accounts", "run_daily", "day_002", "day_003", "real_order", "broker_order"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]

MONITORING_FILES = {
    "monitoring_config": "monitoring_config.json",
    "monitoring_input_availability": "monitoring_input_availability.json",
    "run_history_update": "run_history_update.json",
    "run_history_snapshot": "run_history_snapshot.json",
    "alert_rule_config": "alert_rule_config.json",
    "alert_evaluation_result": "alert_evaluation_result.json",
    "alert_event_log": "alert_event_log.json",
    "warning_trend_snapshot": "warning_trend_snapshot.json",
    "blocking_trend_snapshot": "blocking_trend_snapshot.json",
    "provider_health_trend_snapshot": "provider_health_trend_snapshot.json",
    "workflow_health_trend_snapshot": "workflow_health_trend_snapshot.json",
    "dashboard_health_trend_snapshot": "dashboard_health_trend_snapshot.json",
    "monitoring_status_card": "monitoring_status_card.json",
    "owner_alert_summary_card": "owner_alert_summary_card.json",
    "run_history_summary_card": "run_history_summary_card.json",
    "monitoring_source_trace": "monitoring_source_trace.json",
    "monitoring_boundary_check": "monitoring_boundary_check.json",
    "monitoring_manifest": "monitoring_manifest.json",
    "monitoring_summary": "monitoring_summary.json",
}

MONITORING_HISTORY_FILES = {
    "run_history_index": "run_history_index.json",
    "warning_history_index": "warning_history_index.json",
    "blocking_history_index": "blocking_history_index.json",
    "alert_history_index": "alert_history_index.json",
}

MONITORING_REPORTS = {
    "owner_monitoring_summary_report": "A_SHARE_OWNER_MONITORING_SUMMARY.md",
    "owner_alert_summary_report": "A_SHARE_OWNER_ALERT_SUMMARY.md",
    "run_history_summary_report": "A_SHARE_RUN_HISTORY_SUMMARY.md",
    "warning_trend_summary_report": "A_SHARE_WARNING_TREND_SUMMARY.md",
    "monitoring_source_trace_report": "A_SHARE_MONITORING_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class OwnerMonitoringConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_MONITORING_DASHBOARD
    history_window_days: int = DEFAULT_HISTORY_WINDOW_DAYS
    minimum_history_observations: int = DEFAULT_MINIMUM_HISTORY_OBSERVATIONS
    append_only_history: bool = True
    allow_rebuild_history: bool = False
    evaluate_alerts: bool = True
    send_external_notifications: bool = False
    notification_channels_enabled: tuple[str, ...] = ()
    local_alert_artifacts_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-MONITORING-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "history_window_days": self.history_window_days,
            "minimum_history_observations": self.minimum_history_observations,
            "append_only_history": self.append_only_history,
            "allow_rebuild_history": self.allow_rebuild_history,
            "evaluate_alerts": self.evaluate_alerts,
            "send_external_notifications": self.send_external_notifications,
            "notification_channels_enabled": list(self.notification_channels_enabled),
            "local_alert_artifacts_only": self.local_alert_artifacts_only,
            **MONITORING_FLAGS,
            "raw_config": asdict(self),
        }


def validate_monitoring_config(config: OwnerMonitoringConfig) -> list[str]:
    issues = []
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.history_window_days <= 0:
        issues.append("history_window_days must be positive")
    if config.minimum_history_observations <= 0:
        issues.append("minimum_history_observations must be positive")
    return issues


def monitoring_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_monitoring" / "daily" / as_of_date


def monitoring_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_monitoring" / "daily" / as_of_date


def monitoring_history_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_owner_monitoring" / "history"


def monitoring_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = monitoring_data_dir(paths, as_of_date)
    output_dir = monitoring_output_dir(paths, as_of_date)
    history_dir = monitoring_history_dir(paths)
    artifacts = {key: data_dir / filename for key, filename in MONITORING_FILES.items()}
    artifacts.update({key: history_dir / filename for key, filename in MONITORING_HISTORY_FILES.items()})
    artifacts.update({key: output_dir / filename for key, filename in MONITORING_REPORTS.items()})
    artifacts["monitoring_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_monitoring_audit.json"
    artifacts["monitoring_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_MONITORING_AUDIT.md"
    return artifacts
