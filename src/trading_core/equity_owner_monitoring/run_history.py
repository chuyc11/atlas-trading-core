"""Append-only run history for owner monitoring."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file, write_json
from trading_core.equity_owner_monitoring.input_availability import load_json, monitoring_input_paths
from trading_core.equity_owner_monitoring.monitoring_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION, monitoring_artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_run_history_record(*, paths: ProjectPaths, as_of_date: str, generated_at: str | None = None) -> dict[str, Any]:
    inputs = monitoring_input_paths(paths, as_of_date)
    dashboard_audit = load_json(inputs["owner_dashboard_audit"])
    dashboard_manifest = load_json(inputs["dashboard_manifest"])
    dashboard_summary = load_json(inputs["dashboard_summary"])
    dashboard_source_trace = load_json(inputs["dashboard_source_trace"])
    current_audit = load_json(inputs["current_day_run_audit"])
    current_manifest = load_json(inputs["current_day_run_manifest"])
    refresh_audit = load_json(inputs["data_refresh_audit"])
    workflow_card = load_json(inputs["workflow_status_card"])
    boundary = load_json(inputs["dashboard_boundary_check"])
    dashboard_hash = sha256_file(inputs["dashboard_manifest"])
    run_id = f"A-SHARE-OWNER-MONITORING-RUN-{as_of_date}"
    return {
        "run_id": run_id,
        "as_of_date": as_of_date,
        "resolved_as_of_date": dashboard_manifest.get("resolved_as_of_date", as_of_date),
        "target_version": TARGET_VERSION,
        "source_dashboard_version": dashboard_manifest.get("target_version"),
        "source_current_day_version": current_manifest.get("target_version"),
        "source_dashboard_hash": dashboard_hash,
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "overall_status": dashboard_summary.get("overall_status", "unknown"),
        "data_refresh_status": "passed" if refresh_audit.get("overall_passed") else "failed",
        "current_day_run_status": "passed" if current_audit.get("overall_passed") else "failed",
        "workflow_status": "passed" if workflow_card.get("workflow_audit_passed") else "failed",
        "dashboard_status": "passed" if dashboard_audit.get("overall_passed") else "failed",
        "blocking_count": len(dashboard_audit.get("blocking_reasons", [])),
        "warning_count": len(dashboard_audit.get("warnings", [])),
        "critical_alert_count": 0,
        "warning_alert_count": 0,
        "known_non_blocking_count": 0,
        "audit_paths": {
            "owner_dashboard_audit": relative(inputs["owner_dashboard_audit"], paths.project_root),
            "current_day_run_audit": relative(inputs["current_day_run_audit"], paths.project_root),
            "data_refresh_audit": relative(inputs["data_refresh_audit"], paths.project_root),
        },
        "dashboard_paths": {
            "manifest": relative(inputs["dashboard_manifest"], paths.project_root),
            "summary": relative(inputs["dashboard_summary"], paths.project_root),
        },
        "source_trace_paths": {
            "dashboard_source_trace": relative(inputs["dashboard_source_trace"], paths.project_root),
        },
        "boundary_status": boundary.get("overall_passed") is True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "dashboard_source_trace_complete": dashboard_source_trace.get("source_trace_complete") is True,
    }


def update_run_history(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    history_window_days: int,
    minimum_history_observations: int,
    allow_rebuild_history: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifacts = monitoring_artifact_paths(paths, as_of_date)
    artifacts["run_history_index"].parent.mkdir(parents=True, exist_ok=True)
    existing = load_json(artifacts["run_history_index"])
    records = [] if allow_rebuild_history else list(existing.get("records", []))
    record = build_run_history_record(paths=paths, as_of_date=as_of_date)
    duplicate = next(
        (
            row
            for row in records
            if row.get("as_of_date") == record["as_of_date"]
            and row.get("target_version") == record["target_version"]
            and row.get("source_dashboard_hash") == record["source_dashboard_hash"]
        ),
        None,
    )
    warnings = []
    appended = False
    duplicate_skipped = False
    if duplicate:
        duplicate_skipped = True
    else:
        changed_same_date = any(row.get("as_of_date") == record["as_of_date"] and row.get("target_version") == record["target_version"] for row in records)
        if changed_same_date:
            warnings.append("same_date_target_version_changed_source_dashboard_hash")
        records.append(record)
        appended = True
    records = sorted(records, key=lambda row: (row.get("as_of_date", ""), row.get("generated_at", "")))
    index = {
        "index_id": "A-SHARE-OWNER-MONITORING-RUN-HISTORY-INDEX",
        "target_version": TARGET_VERSION,
        "history_window_days": history_window_days,
        "minimum_history_observations": minimum_history_observations,
        "append_only_history": not allow_rebuild_history,
        "records": records,
        "record_count": len(records),
        "warnings": warnings,
    }
    snapshot_records = records[-history_window_days:]
    trend_available = len(snapshot_records) >= minimum_history_observations
    snapshot = {
        "snapshot_id": "A-SHARE-OWNER-MONITORING-RUN-HISTORY-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "history_window_days": history_window_days,
        "minimum_history_observations": minimum_history_observations,
        "run_history_observation_count": len(snapshot_records),
        "trend_analysis_available": trend_available,
        "insufficient_history_for_trends": not trend_available,
        "records": snapshot_records,
        "latest_record": snapshot_records[-1] if snapshot_records else None,
    }
    update = {
        "update_id": "A-SHARE-OWNER-MONITORING-RUN-HISTORY-UPDATE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "appended": appended,
        "duplicate_skipped": duplicate_skipped,
        "allow_rebuild_history": allow_rebuild_history,
        "run_history_observation_count": len(snapshot_records),
        "trend_analysis_available": trend_available,
        "insufficient_history_for_trends": not trend_available,
        "warnings": warnings,
    }
    write_json(artifacts["run_history_index"], index)
    write_json(artifacts["run_history_snapshot"], snapshot)
    write_json(artifacts["run_history_update"], update)
    return update, snapshot
