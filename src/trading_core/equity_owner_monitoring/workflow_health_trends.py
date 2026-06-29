"""Workflow health trend snapshots."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_monitoring.input_availability import load_json, monitoring_input_paths
from trading_core.equity_owner_monitoring.provider_health_trends import _health_snapshot, _previous_status
from trading_core.storage.file_paths import ProjectPaths


def build_workflow_health_trend_snapshot(*, paths: ProjectPaths, as_of_date: str, run_history_snapshot: dict[str, Any], minimum_history_observations: int) -> dict[str, Any]:
    workflow_card = load_json(monitoring_input_paths(paths, as_of_date)["workflow_status_card"])
    status = "passed" if workflow_card.get("workflow_audit_passed") else "failed"
    return _health_snapshot(
        snapshot_id="A-SHARE-OWNER-MONITORING-WORKFLOW-HEALTH-TREND",
        as_of_date=as_of_date,
        current_status=status,
        previous_status=_previous_status(run_history_snapshot, "workflow_status"),
        history_count=run_history_snapshot.get("run_history_observation_count", 0),
        minimum_history_observations=minimum_history_observations,
        warnings=list(workflow_card.get("warnings", [])),
        blocking_reasons=list(workflow_card.get("blocking_reasons", [])),
    )
