"""Alert event log and history index."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_quality.common import write_json
from trading_core.equity_owner_monitoring.input_availability import load_json
from trading_core.equity_owner_monitoring.monitoring_config import TARGET_VERSION, monitoring_artifact_paths
from trading_core.storage.file_paths import ProjectPaths


def write_alert_event_log_and_history(*, paths: ProjectPaths, as_of_date: str, alert_evaluation_result: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    artifacts = monitoring_artifact_paths(paths, as_of_date)
    events = list(alert_evaluation_result.get("events", []))
    log = {
        "event_log_id": "A-SHARE-OWNER-MONITORING-ALERT-EVENT-LOG",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "events": events,
        "event_count": len(events),
        "triggered_event_count": len([event for event in events if event.get("status") == "triggered"]),
        "external_notifications_sent": False,
    }
    existing = load_json(artifacts["alert_history_index"])
    history_events = list(existing.get("events", []))
    existing_ids = {event.get("alert_id") for event in history_events}
    for event in events:
        if event.get("alert_id") not in existing_ids:
            history_events.append(event)
            existing_ids.add(event.get("alert_id"))
    history = {
        "index_id": "A-SHARE-OWNER-MONITORING-ALERT-HISTORY-INDEX",
        "target_version": TARGET_VERSION,
        "events": history_events,
        "event_count": len(history_events),
        "triggered_event_count": len([event for event in history_events if event.get("status") == "triggered"]),
        "external_notifications_sent": False,
    }
    write_json(artifacts["alert_event_log"], log)
    write_json(artifacts["alert_history_index"], history)
    return log, history
