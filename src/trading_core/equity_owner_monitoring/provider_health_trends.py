"""Provider health trend snapshots."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_monitoring.input_availability import load_json, monitoring_input_paths
from trading_core.equity_owner_monitoring.monitoring_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths


def build_provider_health_trend_snapshot(*, paths: ProjectPaths, as_of_date: str, run_history_snapshot: dict[str, Any], minimum_history_observations: int) -> dict[str, Any]:
    provider_card = load_json(monitoring_input_paths(paths, as_of_date)["provider_health_card"])
    status = provider_card.get("status", "missing")
    warnings = list(provider_card.get("warnings", []))
    return _health_snapshot(
        snapshot_id="A-SHARE-OWNER-MONITORING-PROVIDER-HEALTH-TREND",
        as_of_date=as_of_date,
        current_status=status,
        previous_status=_previous_status(run_history_snapshot, "data_refresh_status"),
        history_count=run_history_snapshot.get("run_history_observation_count", 0),
        minimum_history_observations=minimum_history_observations,
        warnings=warnings,
        blocking_reasons=[],
    )


def _previous_status(run_history_snapshot: dict[str, Any], field: str) -> str | None:
    records = run_history_snapshot.get("records", [])
    if len(records) < 2:
        return None
    return records[-2].get(field)


def _health_snapshot(*, snapshot_id: str, as_of_date: str, current_status: str, previous_status: str | None, history_count: int, minimum_history_observations: int, warnings: list[str], blocking_reasons: list[str]) -> dict[str, Any]:
    trend_available = history_count >= minimum_history_observations
    degraded = trend_available and previous_status not in {None, "failed"} and current_status == "failed"
    improved = trend_available and previous_status == "failed" and current_status != "failed"
    unchanged = trend_available and previous_status == current_status
    return {
        "snapshot_id": snapshot_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "current_status": current_status,
        "previous_status": previous_status,
        "trend_status": "available" if trend_available else "insufficient_history",
        "history_observation_count": history_count,
        "minimum_history_observations": minimum_history_observations,
        "degraded": degraded,
        "improved": improved,
        "unchanged": unchanged,
        "insufficient_history": not trend_available,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
    }
