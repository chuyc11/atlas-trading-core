"""Monitoring refresh sourced from build-output dashboard."""

from __future__ import annotations

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import TARGET_VERSION
from trading_core.equity_build_output_ops_refresh.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_monitoring_refresh(*, paths: ProjectPaths, as_of_date: str) -> dict:
    status = load_json(paths.data_dir / "equity_owner_monitoring" / "daily" / as_of_date / "monitoring_status_card.json")
    dashboard = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_dashboard_summary.json")
    warning = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_warning_and_blocker_card.json")
    return {
        "refresh_id": "A-SHARE-BUILD-OUTPUT-MONITORING-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "monitoring_refresh_performed": True,
        "original_monitoring_status": status.get("overall_monitoring_status"),
        "build_output_dashboard_status": dashboard.get("overall_status"),
        "critical_alert_count": status.get("critical_alert_count", 0),
        "warning_alert_count": status.get("warning_alert_count", 0),
        "known_non_blocking_alert_count": status.get("known_non_blocking_alert_count", 0),
        "build_output_warning_count": warning.get("warning_count", len(dashboard.get("warnings", []))),
        "build_output_blocking_count": warning.get("blocking_count", len(dashboard.get("blocking_reasons", []))),
        "external_notifications_sent": False,
        "non_trading_interpretation": True,
        "warnings": dashboard.get("warnings", []),
    }


def build_alert_summary_refresh(*, paths: ProjectPaths, as_of_date: str, monitoring_refresh: dict) -> dict:
    alert = load_json(paths.data_dir / "equity_owner_monitoring" / "daily" / as_of_date / "owner_alert_summary_card.json")
    return {
        "refresh_id": "A-SHARE-BUILD-OUTPUT-ALERT-SUMMARY-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "alert_summary_refresh_performed": True,
        "critical_alerts": alert.get("critical_alerts", []),
        "warning_alerts": alert.get("warning_alerts", []),
        "known_non_blocking_alerts": alert.get("known_non_blocking_alerts", []),
        "informational_alerts": alert.get("informational_alerts", []),
        "critical_alert_count": monitoring_refresh.get("critical_alert_count", 0),
        "warning_alert_count": monitoring_refresh.get("warning_alert_count", 0),
        "known_non_blocking_alert_count": monitoring_refresh.get("known_non_blocking_alert_count", 0),
        "external_notifications_sent": False,
        "alert_used_as_trade_instruction": False,
    }

