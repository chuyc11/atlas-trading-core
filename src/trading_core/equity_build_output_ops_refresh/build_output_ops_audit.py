"""Audit for v0.8.10 build-output ops refresh."""

from __future__ import annotations

import hashlib
import json

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import (
    BOUNDARY,
    FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    TARGET_VERSION,
    artifact_paths,
)
from trading_core.equity_build_output_ops_refresh.build_output_ops_report import render_audit_report
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


def audit_a_share_build_output_ops_refresh(*, as_of_date: str, paths: ProjectPaths | None = None) -> dict:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {}
    for key, path in artifacts.items():
        if key in FILES and path.exists():
            try:
                payloads[key] = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                payloads[key] = {}
    checks = _checks(paths, artifacts, payloads)
    blocking = sorted(key for key, ok in checks.items() if not ok)
    availability = payloads.get("build_output_ops_input_availability", {})
    summary = payloads.get("build_output_ops_summary", {})
    boundary = payloads.get("build_output_ops_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": "build_build_output_monitoring_remediation_ops_refresh",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "build_output_dashboard_audit_passed": availability.get("build_output_dashboard_audit_passed", False),
            "repeatability_audit_passed": availability.get("repeatability_audit_passed", False),
            "gated_build_audit_passed": availability.get("gated_build_audit_passed", False),
            "original_monitoring_audit_passed": availability.get("original_monitoring_audit_passed", False),
            "original_remediation_audit_passed": availability.get("original_remediation_audit_passed", False),
            "original_ops_center_audit_passed": availability.get("original_ops_center_audit_passed", False),
        },
        "refresh_checks": {
            "source_workflow_mode": summary.get("source_workflow_mode"),
            "monitoring_refresh_performed": summary.get("monitoring_refresh_performed", False),
            "remediation_refresh_performed": summary.get("remediation_refresh_performed", False),
            "ops_center_refresh_performed": summary.get("ops_center_refresh_performed", False),
            "ops_history_refresh_performed": summary.get("ops_history_refresh_performed", False),
            "build_from_existing_data_rerun": summary.get("build_from_existing_data_rerun", True),
            "business_output_drift_count": summary.get("business_output_drift_count"),
            "protected_path_modifications_detected": summary.get("protected_path_modifications_detected"),
            "execute_remediation_actions": summary.get("execute_remediation_actions", True),
            "external_notifications_sent": summary.get("external_notifications_sent", True),
            "automatic_action_count": summary.get("automatic_action_count", 1),
            "comparison_completed": summary.get("comparison_completed", False),
        },
        "boundary": {**BOUNDARY, **{k: boundary.get(k, v) for k, v in BOUNDARY.items()}},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json_markdown(
        artifacts["build_output_ops_audit_json"],
        audit,
        artifacts["build_output_ops_audit_report"],
        render_audit_report(audit),
    )
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "refresh_checks": audit["refresh_checks"],
        "boundary": audit["boundary"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["build_output_ops_audit_json"]),
        "report_path": str(artifacts["build_output_ops_audit_report"]),
    }


def _checks(paths: ProjectPaths, artifacts: dict, payloads: dict) -> dict[str, bool]:
    availability = payloads.get("build_output_ops_input_availability", {})
    resolution = payloads.get("build_output_ops_source_resolution", {})
    trace = payloads.get("build_output_ops_source_trace", {})
    boundary = payloads.get("build_output_ops_boundary_check", {})
    manifest = payloads.get("build_output_ops_manifest", {})
    summary = payloads.get("build_output_ops_summary", {})
    safe_action = payloads.get("build_output_safe_action_refresh", {})
    comparison = payloads.get("original_ops_vs_build_output_ops_comparison", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload),
        "build_output_dashboard_audit_passed": availability.get("build_output_dashboard_audit_passed", False) is True,
        "repeatability_audit_passed": availability.get("repeatability_audit_passed", False) is True,
        "gated_build_audit_passed": availability.get("gated_build_audit_passed", False) is True,
        "original_monitoring_audit_passed": availability.get("original_monitoring_audit_passed", False) is True,
        "original_remediation_audit_passed": availability.get("original_remediation_audit_passed", False) is True,
        "original_ops_center_audit_passed": availability.get("original_ops_center_audit_passed", False) is True,
        "source_workflow_mode_build": resolution.get("source_workflow_mode") == "build_from_existing_data",
        "business_output_drift_count_zero": summary.get("business_output_drift_count") == 0,
        "protected_path_modification_clean": summary.get("protected_path_modifications_detected") is False,
        "monitoring_refresh_performed": summary.get("monitoring_refresh_performed", False) is True,
        "remediation_refresh_performed": summary.get("remediation_refresh_performed", False) is True,
        "ops_center_refresh_performed": summary.get("ops_center_refresh_performed", False) is True,
        "ops_history_refresh_performed": summary.get("ops_history_refresh_performed", False) is True,
        "build_from_existing_data_not_rerun": summary.get("build_from_existing_data_rerun", True) is False,
        "execute_remediation_actions_false": summary.get("execute_remediation_actions", True) is False,
        "external_notifications_sent_false": summary.get("external_notifications_sent", True) is False,
        "automatic_action_count_zero": summary.get("automatic_action_count") == 0,
        "no_forbidden_safe_action_types": not safe_action.get("forbidden_safe_action_type_hits", []),
        "comparison_completed": comparison.get("comparison_completed", False) is True,
        "source_trace_complete": trace.get("source_trace_complete", False) is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_overall_passed": boundary.get("overall_passed", False) is True,
        "boundary_clean": all(boundary.get(key) is value for key, value in BOUNDARY.items()),
        "forbidden_artifacts_absent": not boundary.get("forbidden_artifacts_present", []),
        "forbidden_positive_wording_absent": not boundary.get("forbidden_wording_positive_hits", []),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-SUMMARY",
    }


def _source_hashes_match(paths: ProjectPaths, source_trace: dict) -> bool:
    entries = [entry for entry in source_trace.get("entries", []) if entry.get("required") is True]
    if not entries:
        return False
    for entry in entries:
        recorded = entry.get("sha256")
        if not recorded:
            return False
        path = paths.project_root / entry.get("path", "")
        if not path.exists():
            return False
        if hashlib.sha256(path.read_bytes()).hexdigest() != recorded:
            return False
    return True

