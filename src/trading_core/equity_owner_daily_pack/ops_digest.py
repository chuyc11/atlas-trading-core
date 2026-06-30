"""Monitoring/remediation/ops digest."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_monitoring_remediation_ops_digest(*, paths: ProjectPaths, as_of_date: str) -> dict:
    monitoring = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_monitoring_refresh.json")
    remediation = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_remediation_refresh.json")
    ops_center = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_ops_center_refresh.json")
    history = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_ops_history_refresh.json")
    return {
        "digest_id": "A-SHARE-MONITORING-REMEDIATION-OPS-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "monitoring_refresh_performed": monitoring.get("monitoring_refresh_performed", False),
        "remediation_refresh_performed": remediation.get("remediation_refresh_performed", False),
        "ops_center_refresh_performed": ops_center.get("ops_center_refresh_performed", False),
        "ops_history_refresh_performed": history.get("ops_history_refresh_performed", False),
        "ops_health_score": ops_center.get("health_score"),
        "ops_health_grade": ops_center.get("health_grade"),
        "overall_status": ops_center.get("overall_status"),
        "execute_remediation_actions": remediation.get("execute_remediation_actions", True),
        "external_notifications_sent": monitoring.get("external_notifications_sent", True),
    }

