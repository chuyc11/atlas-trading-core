"""Fail-close audit for the daily ops command center."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file, write_report
from trading_core.equity_ops_center.input_availability import load_json
from trading_core.equity_ops_center.ops_config import DEFAULT_AS_OF_DATE, OPS_BOUNDARY, OPS_FILES, OPS_REPORTS, RECOMMENDED_NEXT_VERSION, REMEDIATION_VERSION, TARGET_VERSION, ops_artifact_paths
from trading_core.equity_ops_center.ops_report import render_audit
from trading_core.equity_ops_center.ops_source_trace import forbidden_source_path_hits
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


REQUIRED_ARTIFACTS = list(OPS_FILES) + list(OPS_REPORTS)


def audit_a_share_daily_ops_center(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = ops_artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in OPS_FILES}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads)
    blocking = [f"{key}=false" for key, passed in checks.items() if not passed]
    availability = payloads.get("ops_input_availability", {})
    input_checks = availability.get("input_audit_checks", {})
    execution = payloads.get("ops_execution_record", {})
    config = payloads.get("ops_center_config", {})
    health = payloads.get("ops_health_score_card", {})
    boundary = payloads.get("ops_boundary_check", {})
    manifest = payloads.get("ops_manifest", {})
    audit = {
        "audit_id": "A-SHARE-DAILY-OPS-CENTER-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": config.get("mode"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(payloads),
        "input_audit_checks": {
            "data_refresh_audit_passed": input_checks.get("data_refresh_audit_passed") is True,
            "current_day_run_audit_passed": input_checks.get("current_day_research_run_audit_passed") is True,
            "owner_dashboard_audit_passed": input_checks.get("owner_dashboard_audit_passed") is True,
            "owner_monitoring_audit_passed": input_checks.get("owner_monitoring_audit_passed") is True,
            "owner_remediation_audit_passed": input_checks.get("owner_remediation_audit_passed") is True,
        },
        "ops_checks": {
            "required_modules_available": availability.get("required_modules_available") is True,
            "dates_aligned": payloads.get("ops_date_alignment", {}).get("all_dates_aligned") is True,
            "health_score_valid": _health_score_valid(health),
            "automatic_action_count": int(payloads.get("ops_action_summary", {}).get("automatic_action_count", -1)),
            "commands_executed": execution.get("commands_executed", []),
            "aggregate_existing_artifacts_only": config.get("aggregate_existing_artifacts_only") is True,
            "external_notifications_sent": execution.get("external_notifications_sent"),
        },
        "boundary": {key: boundary.get(key) for key in OPS_BOUNDARY},
        "manifest": {
            "ops_health_score": manifest.get("ops_health_score"),
            "ops_health_grade": health.get("grade"),
            "overall_status": manifest.get("overall_status"),
            "blocking_issue_count": manifest.get("blocking_issue_count", 0),
            "warning_issue_count": manifest.get("warning_issue_count", 0),
            "known_non_blocking_issue_count": manifest.get("known_non_blocking_issue_count", 0),
            "safe_action_count": manifest.get("safe_action_count", 0),
            "automatic_action_count": manifest.get("automatic_action_count", 0),
        },
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    return write_report(artifacts["ops_audit_json"], audit, artifacts["ops_audit_report"], render_audit(audit))


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    availability = payloads.get("ops_input_availability", {})
    input_checks = availability.get("input_audit_checks", {})
    alignment = payloads.get("ops_date_alignment", {})
    execution = payloads.get("ops_execution_record", {})
    health = payloads.get("ops_health_score_card", {})
    action = payloads.get("ops_action_summary", {})
    source_trace = payloads.get("ops_source_trace", {})
    boundary = payloads.get("ops_boundary_check", {})
    manifest = payloads.get("ops_manifest", {})
    compact = artifacts["ops_compact_report"]
    return {
        "all_required_artifacts_exist": all(artifacts[key].exists() for key in REQUIRED_ARTIFACTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload),
        "input_data_refresh_audit_passed": input_checks.get("data_refresh_audit_passed") is True,
        "input_current_day_run_audit_passed": input_checks.get("current_day_research_run_audit_passed") is True,
        "input_owner_dashboard_audit_passed": input_checks.get("owner_dashboard_audit_passed") is True,
        "input_owner_monitoring_audit_passed": input_checks.get("owner_monitoring_audit_passed") is True,
        "input_owner_remediation_audit_passed": input_checks.get("owner_remediation_audit_passed") is True,
        "required_modules_available": availability.get("required_modules_available") is True,
        "dates_aligned": alignment.get("all_dates_aligned") is True and not alignment.get("blocking_reasons"),
        "health_score_valid": _health_score_valid(health),
        "automatic_action_count_zero": action.get("automatic_action_count") == 0 and manifest.get("automatic_action_count") == 0,
        "no_trade_related_actions": not action.get("forbidden_action_hits"),
        "commands_executed_empty": execution.get("commands_executed") == [] and manifest.get("commands_executed") == [],
        "aggregate_existing_artifacts_only": payloads.get("ops_center_config", {}).get("aggregate_existing_artifacts_only") is True and execution.get("aggregate_existing_artifacts_only") is True,
        "external_notifications_sent_false": execution.get("external_notifications_sent") is False,
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "source_trace_no_forbidden_paths": not forbidden_source_path_hits(source_trace.get("source_artifacts", []) + source_trace.get("output_artifacts", [])),
        "source_trace_hashes_match": _source_hashes_match(paths, source_trace),
        "boundary_clean": boundary.get("overall_passed") is True,
        "boundary_fields_clean": _boundary_fields_clean(boundary),
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits"),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-DAILY-OPS-CENTER-MANIFEST",
        "summary_generated": payloads.get("ops_summary", {}).get("summary_id") == "A-SHARE-DAILY-OPS-CENTER-SUMMARY",
        "compact_report_length": compact.exists() and len(compact.read_text(encoding="utf-8")) <= 1200,
    }


def _health_score_valid(health: dict[str, Any]) -> bool:
    score = health.get("score")
    return isinstance(score, int) and 0 <= score <= 100 and health.get("grade") in {"A", "B", "C", "D", "F"}


def _boundary_fields_clean(boundary: dict[str, Any]) -> bool:
    for key, expected in OPS_BOUNDARY.items():
        value = boundary.get(key)
        if isinstance(expected, list):
            if value != expected:
                return False
        elif value is not expected:
            return False
    return True


def _source_hashes_match(paths: ProjectPaths, trace: dict[str, Any]) -> bool:
    for row in trace.get("source_artifacts", []):
        path = Path(row.get("path", ""))
        if not path.is_absolute():
            path = paths.project_root / path
        if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
            return False
    return True


def _warnings(payloads: dict[str, Any]) -> list[str]:
    return sorted(set(payloads.get("ops_input_availability", {}).get("warnings", [])) | set(payloads.get("ops_boundary_check", {}).get("warnings", [])))
