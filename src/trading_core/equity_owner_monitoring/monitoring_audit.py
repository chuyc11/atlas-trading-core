"""Fail-close audit for owner monitoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file, write_report
from trading_core.equity_owner_monitoring.input_availability import load_json
from trading_core.equity_owner_monitoring.monitoring_config import (
    MONITORING_BOUNDARY,
    MONITORING_FILES,
    MONITORING_HISTORY_FILES,
    MONITORING_REPORTS,
    DEFAULT_AS_OF_DATE,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
    monitoring_artifact_paths,
)
from trading_core.equity_owner_monitoring.monitoring_report import render_audit
from trading_core.equity_owner_monitoring.monitoring_source_trace import forbidden_source_path_hits
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


REQUIRED_ARTIFACTS = list(MONITORING_FILES) + list(MONITORING_HISTORY_FILES) + list(MONITORING_REPORTS)


def audit_a_share_owner_monitoring(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = monitoring_artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in set(MONITORING_FILES) | set(MONITORING_HISTORY_FILES)}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads)
    blocking = [f"{key}=false" for key, passed in checks.items() if not passed]
    input_checks = payloads.get("monitoring_input_availability", {}).get("input_audit_checks", {})
    alert_counts = payloads.get("alert_evaluation_result", {}).get("alert_counts", {})
    boundary = payloads.get("monitoring_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-MONITORING-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("monitoring_config", {}).get("mode"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(payloads),
        "input_audit_checks": {
            "owner_dashboard_audit_passed": input_checks.get("owner_dashboard_audit_passed") is True,
            "current_day_run_audit_passed": input_checks.get("current_day_run_audit_passed") is True,
            "data_refresh_audit_passed": input_checks.get("data_refresh_audit_passed") is True,
        },
        "monitoring_checks": {
            "run_history_updated": bool(payloads.get("run_history_update")),
            "alert_rules_evaluated": bool(payloads.get("alert_evaluation_result")),
            "trend_analysis_available": payloads.get("run_history_snapshot", {}).get("trend_analysis_available") is True,
            "insufficient_history_correctly_flagged": _insufficient_history_correct(payloads),
            "external_notifications_sent": payloads.get("alert_evaluation_result", {}).get("external_notifications_sent") is True,
        },
        "alert_counts": {
            "critical": int(alert_counts.get("critical", 0)),
            "warning": int(alert_counts.get("warning", 0)),
            "informational": int(alert_counts.get("informational", 0)),
            "known_non_blocking": int(alert_counts.get("known_non_blocking", 0)),
        },
        "boundary": {key: boundary.get(key) for key in MONITORING_BOUNDARY},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    return write_report(artifacts["monitoring_audit_json"], audit, artifacts["monitoring_audit_report"], render_audit(audit))


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    input_availability = payloads.get("monitoring_input_availability", {})
    alert_eval = payloads.get("alert_evaluation_result", {})
    alert_log = payloads.get("alert_event_log", {})
    warning_trend = payloads.get("warning_trend_snapshot", {})
    blocking_trend = payloads.get("blocking_trend_snapshot", {})
    source_trace = payloads.get("monitoring_source_trace", {})
    boundary = payloads.get("monitoring_boundary_check", {})
    manifest = payloads.get("monitoring_manifest", {})
    summary = payloads.get("monitoring_summary", {})
    return {
        "all_required_artifacts_exist": all(artifacts[key].exists() for key in REQUIRED_ARTIFACTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload),
        "input_dashboard_audit_passed": input_availability.get("input_audit_checks", {}).get("owner_dashboard_audit_passed") is True,
        "input_current_day_run_audit_passed": input_availability.get("input_audit_checks", {}).get("current_day_run_audit_passed") is True,
        "input_data_refresh_audit_passed": input_availability.get("input_audit_checks", {}).get("data_refresh_audit_passed") is True,
        "critical_alert_count_matches": alert_eval.get("critical_alert_count") == len([event for event in alert_eval.get("events", []) if event.get("status") == "triggered" and event.get("severity") == "critical"]),
        "blocking_count_matches_source_blockers": payloads.get("monitoring_status_card", {}).get("blocking_count") == blocking_trend.get("blocking_count_current"),
        "trend_insufficiency_correctly_flagged": _insufficient_history_correct(payloads),
        "external_notifications_sent_false": alert_eval.get("external_notifications_sent") is False and alert_log.get("external_notifications_sent") is False,
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "source_trace_no_forbidden_paths": not forbidden_source_path_hits(source_trace.get("source_artifacts", []) + source_trace.get("history_artifacts", []) + source_trace.get("output_artifacts", [])),
        "source_trace_hashes_match": _source_hashes_match(paths, source_trace),
        "boundary_clean": boundary.get("overall_passed") is True,
        "boundary_fields_clean": all(boundary.get(key) is expected for key, expected in MONITORING_BOUNDARY.items()),
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits"),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-MONITORING-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-MONITORING-SUMMARY",
    }


def _insufficient_history_correct(payloads: dict[str, Any]) -> bool:
    snapshot = payloads.get("run_history_snapshot", {})
    count = int(snapshot.get("run_history_observation_count", 0))
    minimum = int(snapshot.get("minimum_history_observations", 3))
    return (count < minimum and snapshot.get("insufficient_history_for_trends") is True and snapshot.get("trend_analysis_available") is False) or count >= minimum


def _source_hashes_match(paths: ProjectPaths, trace: dict[str, Any]) -> bool:
    for group in ["source_artifacts", "history_artifacts"]:
        for row in trace.get(group, []):
            path = Path(row.get("path", ""))
            if not path.is_absolute():
                path = paths.project_root / path
            if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
                return False
    return True


def _warnings(payloads: dict[str, Any]) -> list[str]:
    return sorted(
        set(payloads.get("monitoring_input_availability", {}).get("warnings", []))
        | set(payloads.get("alert_evaluation_result", {}).get("warnings", []))
        | set(payloads.get("monitoring_boundary_check", {}).get("warnings", []))
    )
