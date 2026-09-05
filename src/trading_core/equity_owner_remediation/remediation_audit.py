"""Fail-close audit for owner remediation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file, write_report
from trading_core.equity_owner_remediation.action_checklist import validate_checklist
from trading_core.equity_owner_remediation.input_availability import load_json
from trading_core.equity_owner_remediation.remediation_config import (
    DEFAULT_AS_OF_DATE,
    FORBIDDEN_ACTION_TYPES,
    REMEDIATION_BOUNDARY,
    REMEDIATION_FILES,
    REMEDIATION_REPORTS,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
    remediation_artifact_paths,
)
from trading_core.equity_owner_remediation.remediation_report import render_audit
from trading_core.equity_owner_remediation.remediation_source_trace import forbidden_source_path_hits
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


REQUIRED_ARTIFACTS = list(REMEDIATION_FILES) + list(REMEDIATION_REPORTS)


def audit_a_share_owner_remediation(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = remediation_artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in REMEDIATION_FILES}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads)
    blocking = [f"{key}=false" for key, passed in checks.items() if not passed]
    input_checks = payloads.get("remediation_input_availability", {}).get("input_audit_checks", {})
    checklist = payloads.get("safe_owner_action_checklist", {})
    dry_run = payloads.get("dry_run_remediation_plan", {})
    config = payloads.get("remediation_config", {})
    boundary = payloads.get("remediation_boundary_check", {})
    manifest = payloads.get("remediation_manifest", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-REMEDIATION-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": config.get("mode"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(payloads),
        "input_audit_checks": {
            "owner_monitoring_audit_passed": input_checks.get("owner_monitoring_audit_passed") is True,
            "owner_dashboard_audit_passed": input_checks.get("owner_dashboard_audit_passed") is True,
            "current_day_run_audit_passed": input_checks.get("current_day_run_audit_passed") is True,
            "data_refresh_audit_passed": input_checks.get("data_refresh_audit_passed") is True,
        },
        "remediation_checks": {
            "issue_catalog_present": bool(payloads.get("issue_catalog")),
            "remediation_maps_present": all(payloads.get(key) for key in ["warning_remediation_map", "blocking_remediation_map", "alert_remediation_map"]),
            "guides_present": all(
                payloads.get(key)
                for key in [
                    "provider_remediation_guide",
                    "data_freshness_remediation_guide",
                    "schema_coverage_remediation_guide",
                    "workflow_remediation_guide",
                    "dashboard_remediation_guide",
                    "monitoring_remediation_guide",
                ]
            ),
            "safe_action_checklist_present": bool(checklist),
            "no_forbidden_action_types": not _forbidden_action_type_hits(checklist),
            "automatic_action_count": int(checklist.get("automatic_action_count", -1)),
            "commands_executed": dry_run.get("commands_executed", []),
            "execute_remediation_actions": config.get("execute_remediation_actions"),
            "external_notifications_sent": config.get("send_external_notifications"),
        },
        "boundary": {key: boundary.get(key) for key in REMEDIATION_BOUNDARY},
        "checks": checks,
        "manifest": {
            "issue_count": manifest.get("issue_count", 0),
            "blocking_issue_count": manifest.get("blocking_issue_count", 0),
            "warning_issue_count": manifest.get("warning_issue_count", 0),
            "known_non_blocking_issue_count": manifest.get("known_non_blocking_issue_count", 0),
            "safe_action_count": manifest.get("safe_action_count", 0),
            "automatic_action_count": manifest.get("automatic_action_count", 0),
        },
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    return write_report(artifacts["remediation_audit_json"], audit, artifacts["remediation_audit_report"], render_audit(audit))


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    availability = payloads.get("remediation_input_availability", {})
    issue_catalog = payloads.get("issue_catalog", {})
    checklist = payloads.get("safe_owner_action_checklist", {})
    dry_run = payloads.get("dry_run_remediation_plan", {})
    source_trace = payloads.get("remediation_source_trace", {})
    boundary = payloads.get("remediation_boundary_check", {})
    manifest = payloads.get("remediation_manifest", {})
    summary = payloads.get("remediation_summary", {})
    config = payloads.get("remediation_config", {})
    return {
        "all_required_artifacts_exist": all(artifacts[key].exists() for key in REQUIRED_ARTIFACTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload),
        "input_monitoring_audit_passed": availability.get("input_audit_checks", {}).get("owner_monitoring_audit_passed") is True,
        "input_dashboard_audit_passed": availability.get("input_audit_checks", {}).get("owner_dashboard_audit_passed") is True,
        "input_current_day_run_audit_passed": availability.get("input_audit_checks", {}).get("current_day_run_audit_passed") is True,
        "input_data_refresh_audit_passed": availability.get("input_audit_checks", {}).get("data_refresh_audit_passed") is True,
        "issue_catalog_present": bool(issue_catalog.get("issues")),
        "remediation_maps_present": all(payloads.get(key) for key in ["warning_remediation_map", "blocking_remediation_map", "alert_remediation_map"]),
        "guides_present": all(
            payloads.get(key)
            for key in [
                "provider_remediation_guide",
                "data_freshness_remediation_guide",
                "schema_coverage_remediation_guide",
                "workflow_remediation_guide",
                "dashboard_remediation_guide",
                "monitoring_remediation_guide",
            ]
        ),
        "safe_action_checklist_present": bool(checklist.get("items")),
        "manual_verification_checklist_present": bool(payloads.get("manual_verification_checklist", {}).get("checks")),
        "non_actionable_issue_list_present": bool(payloads.get("non_actionable_issue_list", {}).get("items")),
        "dry_run_plan_present": dry_run.get("plan_id") == "A-SHARE-OWNER-REMEDIATION-DRY-RUN-PLAN",
        "priority_summary_present": manifest.get("blocking_issue_count") is not None,
        "all_issue_codes_mapped_or_unknown": all(issue.get("remediation_category") != "" or issue.get("explicitly_classified_unknown") is True for issue in issue_catalog.get("issues", [])),
        "no_forbidden_action_types": not _forbidden_action_type_hits(checklist),
        "automatic_action_count_zero": checklist.get("automatic_action_count") == 0 and manifest.get("automatic_action_count") == 0,
        "commands_executed_empty": dry_run.get("commands_executed") == [],
        "execute_remediation_actions_false": config.get("execute_remediation_actions") is False and dry_run.get("execute_remediation_actions") is False,
        "external_notifications_sent_false": config.get("send_external_notifications") is False and manifest.get("external_notifications_sent") is False,
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "source_trace_no_forbidden_paths": not forbidden_source_path_hits(source_trace.get("source_artifacts", []) + source_trace.get("output_artifacts", [])),
        "source_trace_hashes_match": _source_hashes_match(paths, source_trace),
        "boundary_clean": boundary.get("overall_passed") is True,
        "boundary_fields_clean": all(boundary.get(key) is expected for key, expected in REMEDIATION_BOUNDARY.items()),
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits"),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-REMEDIATION-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-REMEDIATION-SUMMARY",
    }


def _forbidden_action_type_hits(checklist: dict[str, Any]) -> list[str]:
    hits = [item.get("safe_action_type") for item in checklist.get("items", []) if item.get("safe_action_type") in FORBIDDEN_ACTION_TYPES]
    hits.extend(validate_checklist(checklist.get("items", [])))
    return sorted({str(hit) for hit in hits if hit})


def _source_hashes_match(paths: ProjectPaths, trace: dict[str, Any]) -> bool:
    for group in ["source_artifacts"]:
        for row in trace.get(group, []):
            path = Path(row.get("path", ""))
            if not path.is_absolute():
                path = paths.project_root / path
            if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
                return False
    return True


def _warnings(payloads: dict[str, Any]) -> list[str]:
    return sorted(
        set(payloads.get("remediation_input_availability", {}).get("warnings", []))
        | set(payloads.get("remediation_boundary_check", {}).get("warnings", []))
        | set(payloads.get("safe_owner_action_checklist", {}).get("blocking_reasons", []))
    )
