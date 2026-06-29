"""Dashboard health trend snapshots."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_monitoring.input_availability import load_json, monitoring_input_paths
from trading_core.equity_owner_monitoring.provider_health_trends import _health_snapshot, _previous_status
from trading_core.storage.file_paths import ProjectPaths


def build_dashboard_health_trend_snapshot(*, paths: ProjectPaths, as_of_date: str, run_history_snapshot: dict[str, Any], minimum_history_observations: int) -> dict[str, Any]:
    dashboard_audit = load_json(monitoring_input_paths(paths, as_of_date)["owner_dashboard_audit"])
    status = "passed" if dashboard_audit.get("overall_passed") else "failed"
    return _health_snapshot(
        snapshot_id="A-SHARE-OWNER-MONITORING-DASHBOARD-HEALTH-TREND",
        as_of_date=as_of_date,
        current_status=status,
        previous_status=_previous_status(run_history_snapshot, "dashboard_status"),
        history_count=run_history_snapshot.get("run_history_observation_count", 0),
        minimum_history_observations=minimum_history_observations,
        warnings=list(dashboard_audit.get("warnings", [])),
        blocking_reasons=list(dashboard_audit.get("blocking_reasons", [])),
    )
