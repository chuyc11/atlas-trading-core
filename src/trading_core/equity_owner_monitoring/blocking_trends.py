"""Blocking history and trend snapshots."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_quality.common import write_json
from trading_core.equity_owner_monitoring.input_availability import load_json, monitoring_input_paths
from trading_core.equity_owner_monitoring.monitoring_config import TARGET_VERSION, monitoring_artifact_paths
from trading_core.storage.file_paths import ProjectPaths


def update_blocking_history_and_snapshot(*, paths: ProjectPaths, as_of_date: str, minimum_history_observations: int, source_hash: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    artifacts = monitoring_artifact_paths(paths, as_of_date)
    audit = load_json(monitoring_input_paths(paths, as_of_date)["owner_dashboard_audit"])
    current_blockers = sorted({str(item) for item in audit.get("blocking_reasons", [])})
    existing = load_json(artifacts["blocking_history_index"])
    records = list(existing.get("records", []))
    key_exists = any(row.get("as_of_date") == as_of_date and row.get("source_dashboard_hash") == source_hash for row in records)
    if not key_exists:
        records.append({"as_of_date": as_of_date, "source_dashboard_hash": source_hash, "blocking_codes": current_blockers, "blocking_count": len(current_blockers)})
    records = sorted(records, key=lambda row: row.get("as_of_date", ""))
    index = {
        "index_id": "A-SHARE-OWNER-MONITORING-BLOCKING-HISTORY-INDEX",
        "target_version": TARGET_VERSION,
        "records": records,
        "record_count": len(records),
    }
    snapshot = build_blocking_trend_snapshot(as_of_date=as_of_date, records=records, current_blockers=current_blockers, minimum_history_observations=minimum_history_observations)
    write_json(artifacts["blocking_history_index"], index)
    write_json(artifacts["blocking_trend_snapshot"], snapshot)
    return index, snapshot


def build_blocking_trend_snapshot(*, as_of_date: str, records: list[dict[str, Any]], current_blockers: list[str], minimum_history_observations: int) -> dict[str, Any]:
    count = len(records)
    trend_available = count >= minimum_history_observations
    previous = records[-2] if count >= 2 else None
    previous_codes = set(previous.get("blocking_codes", [])) if previous else set()
    current_codes = set(current_blockers)
    return {
        "snapshot_id": "A-SHARE-OWNER-MONITORING-BLOCKING-TREND-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "history_observation_count": count,
        "minimum_history_observations": minimum_history_observations,
        "trend_analysis_available": trend_available,
        "insufficient_history_for_trends": not trend_available,
        "trend_status": "available" if trend_available else "insufficient_history",
        "blocking_count_current": len(current_blockers),
        "blocking_count_previous": previous.get("blocking_count") if previous else None,
        "blocking_count_change": len(current_blockers) - int(previous.get("blocking_count", 0)) if previous else None,
        "new_blocking_codes": sorted(current_codes - previous_codes) if trend_available else [],
        "resolved_blocking_codes": sorted(previous_codes - current_codes) if trend_available else [],
        "current_blocking_codes": current_blockers,
    }
