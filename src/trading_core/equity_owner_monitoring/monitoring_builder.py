"""Builder for v0.8.3 owner alerting and run-history monitoring."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file, write_json
from trading_core.equity_owner_monitoring.alert_evaluation import evaluate_alert_rules
from trading_core.equity_owner_monitoring.alert_event_log import write_alert_event_log_and_history
from trading_core.equity_owner_monitoring.alert_rules import build_alert_rule_config
from trading_core.equity_owner_monitoring.blocking_trends import update_blocking_history_and_snapshot
from trading_core.equity_owner_monitoring.dashboard_health_trends import build_dashboard_health_trend_snapshot
from trading_core.equity_owner_monitoring.input_availability import build_monitoring_input_availability, monitoring_input_paths
from trading_core.equity_owner_monitoring.monitoring_boundary import build_monitoring_boundary_check
from trading_core.equity_owner_monitoring.monitoring_cards import build_monitoring_status_card, build_owner_alert_summary_card, build_run_history_summary_card
from trading_core.equity_owner_monitoring.monitoring_config import (
    BUILD_MONITORING_DASHBOARD,
    BUILD_RUN_HISTORY_FROM_EXISTING_ARTIFACTS,
    DEFAULT_AS_OF_DATE,
    DEFAULT_HISTORY_WINDOW_DAYS,
    DEFAULT_MINIMUM_HISTORY_OBSERVATIONS,
    VALIDATE_MONITORING_INPUTS,
    OwnerMonitoringConfig,
    monitoring_artifact_paths,
    monitoring_output_dir,
    validate_monitoring_config,
)
from trading_core.equity_owner_monitoring.monitoring_manifest import build_monitoring_manifest, build_monitoring_summary
from trading_core.equity_owner_monitoring.monitoring_report import write_monitoring_reports
from trading_core.equity_owner_monitoring.monitoring_source_trace import build_monitoring_source_trace
from trading_core.equity_owner_monitoring.provider_health_trends import build_provider_health_trend_snapshot
from trading_core.equity_owner_monitoring.run_history import update_run_history
from trading_core.equity_owner_monitoring.warning_trends import update_warning_history_and_snapshot
from trading_core.equity_owner_monitoring.workflow_health_trends import build_workflow_health_trend_snapshot
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_monitoring_inputs(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    history_window_days: int = DEFAULT_HISTORY_WINDOW_DAYS,
    minimum_history_observations: int = DEFAULT_MINIMUM_HISTORY_OBSERVATIONS,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    return build_a_share_owner_monitoring(
        as_of_date=as_of_date,
        mode=VALIDATE_MONITORING_INPUTS,
        history_window_days=history_window_days,
        minimum_history_observations=minimum_history_observations,
        paths=paths,
    )


def build_a_share_owner_monitoring(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_MONITORING_DASHBOARD,
    history_window_days: int = DEFAULT_HISTORY_WINDOW_DAYS,
    minimum_history_observations: int = DEFAULT_MINIMUM_HISTORY_OBSERVATIONS,
    allow_rebuild_history: bool = False,
    send_external_notifications: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = OwnerMonitoringConfig(
        as_of_date=as_of_date,
        mode=mode,
        history_window_days=history_window_days,
        minimum_history_observations=minimum_history_observations,
        allow_rebuild_history=allow_rebuild_history,
        send_external_notifications=send_external_notifications,
    )
    issues = validate_monitoring_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    artifacts = monitoring_artifact_paths(paths, as_of_date)
    generated_at = datetime.now(timezone.utc).isoformat()
    availability = build_monitoring_input_availability(paths=paths, as_of_date=as_of_date)
    write_json(artifacts["monitoring_config"], config.to_dict())
    write_json(artifacts["monitoring_input_availability"], availability)
    if mode == VALIDATE_MONITORING_INPUTS:
        return {
            "builder_id": "A-SHARE-OWNER-MONITORING-INPUT-VALIDATION",
            "mode": mode,
            "as_of_date": as_of_date,
            "overall_passed": availability["overall_passed"],
            "blocking_reasons": availability["blocking_reasons"],
            "warnings": availability["warnings"],
            "monitoring_config_path": str(artifacts["monitoring_config"]),
            "monitoring_input_availability_path": str(artifacts["monitoring_input_availability"]),
        }

    run_history_update, run_history_snapshot = update_run_history(
        paths=paths,
        as_of_date=as_of_date,
        history_window_days=history_window_days,
        minimum_history_observations=minimum_history_observations,
        allow_rebuild_history=allow_rebuild_history,
    )
    dashboard_hash = sha256_file(monitoring_input_paths(paths, as_of_date)["dashboard_manifest"])
    _, warning_trend = update_warning_history_and_snapshot(
        paths=paths,
        as_of_date=as_of_date,
        minimum_history_observations=minimum_history_observations,
        source_hash=dashboard_hash,
    )
    _, blocking_trend = update_blocking_history_and_snapshot(
        paths=paths,
        as_of_date=as_of_date,
        minimum_history_observations=minimum_history_observations,
        source_hash=dashboard_hash,
    )
    provider_health = build_provider_health_trend_snapshot(paths=paths, as_of_date=as_of_date, run_history_snapshot=run_history_snapshot, minimum_history_observations=minimum_history_observations)
    workflow_health = build_workflow_health_trend_snapshot(paths=paths, as_of_date=as_of_date, run_history_snapshot=run_history_snapshot, minimum_history_observations=minimum_history_observations)
    dashboard_health = build_dashboard_health_trend_snapshot(paths=paths, as_of_date=as_of_date, run_history_snapshot=run_history_snapshot, minimum_history_observations=minimum_history_observations)
    alert_rules = build_alert_rule_config(as_of_date=as_of_date)
    preliminary_boundary = build_monitoring_boundary_check(paths=paths, as_of_date=as_of_date, warnings=availability.get("warnings", []), blocking_reasons=availability.get("blocking_reasons", []))
    alert_evaluation = evaluate_alert_rules(
        as_of_date=as_of_date,
        alert_rule_config=alert_rules,
        monitoring_input_availability=availability,
        warning_trend_snapshot=warning_trend,
        blocking_trend_snapshot=blocking_trend,
        provider_health_trend_snapshot=provider_health,
        workflow_health_trend_snapshot=workflow_health,
        dashboard_health_trend_snapshot=dashboard_health,
        monitoring_boundary_check=preliminary_boundary,
        send_external_notifications=send_external_notifications,
    )
    alert_event_log, _ = write_alert_event_log_and_history(paths=paths, as_of_date=as_of_date, alert_evaluation_result=alert_evaluation)
    status_card = build_monitoring_status_card(
        as_of_date=as_of_date,
        run_history_snapshot=run_history_snapshot,
        warning_trend_snapshot=warning_trend,
        blocking_trend_snapshot=blocking_trend,
        alert_evaluation_result=alert_evaluation,
    )
    owner_alert_card = build_owner_alert_summary_card(as_of_date=as_of_date, alert_evaluation_result=alert_evaluation)
    run_history_card = build_run_history_summary_card(as_of_date=as_of_date, run_history_snapshot=run_history_snapshot)
    payload = {
        "monitoring_config": config.to_dict(),
        "monitoring_input_availability": availability,
        "run_history_update": run_history_update,
        "run_history_snapshot": run_history_snapshot,
        "alert_rule_config": alert_rules,
        "alert_evaluation_result": alert_evaluation,
        "alert_event_log": alert_event_log,
        "warning_trend_snapshot": warning_trend,
        "blocking_trend_snapshot": blocking_trend,
        "provider_health_trend_snapshot": provider_health,
        "workflow_health_trend_snapshot": workflow_health,
        "dashboard_health_trend_snapshot": dashboard_health,
        "monitoring_status_card": status_card,
        "owner_alert_summary_card": owner_alert_card,
        "run_history_summary_card": run_history_card,
    }
    for key, value in payload.items():
        if key in artifacts:
            write_json(artifacts[key], value)
    if mode == BUILD_RUN_HISTORY_FROM_EXISTING_ARTIFACTS:
        return _result("A-SHARE-OWNER-MONITORING-RUN-HISTORY-BUILDER", mode, as_of_date, availability, status_card, artifacts)

    boundary = build_monitoring_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        warnings=sorted(set(availability.get("warnings", []) + alert_evaluation.get("warnings", []))),
        blocking_reasons=sorted(set(availability.get("blocking_reasons", []) + [event["rule_id"] for event in alert_evaluation.get("triggered_alerts", []) if event.get("blocking")])),
        external_notifications_sent=False,
    )
    source_trace = _source_trace(paths=paths, as_of_date=as_of_date, generated_at=generated_at, alert_evaluation=alert_evaluation, warning_trend=warning_trend, artifacts=artifacts)
    manifest = _manifest(paths=paths, as_of_date=as_of_date, generated_at=generated_at, mode=mode, status_card=status_card, artifacts=artifacts, boundary=boundary)
    summary = build_monitoring_summary(as_of_date=as_of_date, mode=mode, manifest=manifest, warning_trend_snapshot=warning_trend, owner_alert_summary_card=owner_alert_card)
    payload.update({"monitoring_boundary_check": boundary, "monitoring_source_trace": source_trace, "monitoring_manifest": manifest, "monitoring_summary": summary})
    for key in ["monitoring_boundary_check", "monitoring_source_trace", "monitoring_manifest", "monitoring_summary"]:
        write_json(artifacts[key], payload[key])
    write_monitoring_reports(monitoring_output_dir(paths, as_of_date), payload)

    boundary = build_monitoring_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        warnings=sorted(set(availability.get("warnings", []) + alert_evaluation.get("warnings", []))),
        blocking_reasons=sorted(set(availability.get("blocking_reasons", []) + [event["rule_id"] for event in alert_evaluation.get("triggered_alerts", []) if event.get("blocking")])),
        external_notifications_sent=False,
    )
    source_trace = _source_trace(paths=paths, as_of_date=as_of_date, generated_at=generated_at, alert_evaluation=alert_evaluation, warning_trend=warning_trend, artifacts=artifacts)
    manifest = _manifest(paths=paths, as_of_date=as_of_date, generated_at=generated_at, mode=mode, status_card=status_card, artifacts=artifacts, boundary=boundary)
    summary = build_monitoring_summary(as_of_date=as_of_date, mode=mode, manifest=manifest, warning_trend_snapshot=warning_trend, owner_alert_summary_card=owner_alert_card)
    payload.update({"monitoring_boundary_check": boundary, "monitoring_source_trace": source_trace, "monitoring_manifest": manifest, "monitoring_summary": summary})
    for key in ["monitoring_boundary_check", "monitoring_source_trace", "monitoring_manifest", "monitoring_summary"]:
        write_json(artifacts[key], payload[key])
    write_monitoring_reports(monitoring_output_dir(paths, as_of_date), payload)
    return _result("A-SHARE-OWNER-MONITORING-BUILDER", mode, as_of_date, availability, status_card, artifacts)


def _source_trace(*, paths: ProjectPaths, as_of_date: str, generated_at: str, alert_evaluation: dict[str, Any], warning_trend: dict[str, Any], artifacts: dict[str, Path]) -> dict[str, Any]:
    source_paths = list(monitoring_input_paths(paths, as_of_date).values())
    history_paths = [artifacts[key] for key in ["run_history_index", "warning_history_index", "blocking_history_index", "alert_history_index"]]
    output_paths = [path for key, path in artifacts.items() if key not in {"monitoring_audit_json", "monitoring_audit_report"}]
    return build_monitoring_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        source_paths=source_paths,
        history_paths=history_paths,
        output_paths=output_paths,
        alert_rule_decisions=alert_evaluation.get("events", []),
        warning_carry_forward_decisions=warning_trend.get("current_warning_codes", []),
    )


def _manifest(*, paths: ProjectPaths, as_of_date: str, generated_at: str, mode: str, status_card: dict[str, Any], artifacts: dict[str, Path], boundary: dict[str, Any]) -> dict[str, Any]:
    source_paths = monitoring_input_paths(paths, as_of_date)
    return build_monitoring_manifest(
        as_of_date=as_of_date,
        generated_at=generated_at,
        mode=mode,
        monitoring_status_card=status_card,
        output_artifacts={key: str(path) for key, path in artifacts.items() if key not in {"monitoring_audit_json", "monitoring_audit_report"}},
        source_artifacts={key: str(path) for key, path in source_paths.items()},
        boundary=boundary,
    )


def _result(builder_id: str, mode: str, as_of_date: str, availability: dict[str, Any], status_card: dict[str, Any], artifacts: dict[str, Path]) -> dict[str, Any]:
    return {
        "builder_id": builder_id,
        "mode": mode,
        "as_of_date": as_of_date,
        "overall_passed": availability.get("overall_passed") is True and status_card.get("critical_alert_count", 0) == 0 and status_card.get("blocking_count", 0) == 0,
        "overall_monitoring_status": status_card.get("overall_monitoring_status"),
        "blocking_reasons": availability.get("blocking_reasons", []),
        "warnings": availability.get("warnings", []),
        "monitoring_manifest_path": str(artifacts["monitoring_manifest"]),
        "monitoring_summary_path": str(artifacts["monitoring_summary"]),
        "owner_monitoring_summary_report": str(artifacts["owner_monitoring_summary_report"]),
    }
