"""Audit for v0.8.9 build-output owner dashboard."""

from __future__ import annotations
from typing import Any

import hashlib
import json

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import (
    BOUNDARY,
    FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    REQUIRED_CARDS,
    TARGET_VERSION,
    artifact_paths,
)
from trading_core.equity_build_output_dashboard.build_output_report import render_audit_report
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


def audit_a_share_build_output_owner_dashboard(*, as_of_date: str, paths: ProjectPaths | None = None) -> dict:
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
    availability = payloads.get("build_output_input_availability", {})
    resolution = payloads.get("build_output_source_resolution", {})
    comparison = payloads.get("validate_dashboard_vs_build_dashboard_comparison", {})
    boundary = payloads.get("build_output_dashboard_boundary_check", {})
    audit: dict[str, Any] = {
        "audit_id": "A-SHARE-BUILD-OUTPUT-OWNER-DASHBOARD-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": "build_owner_dashboard_from_build_output",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "repeatability_audit_passed": availability.get("repeatability_audit_passed", False),
            "gated_build_audit_passed": availability.get("gated_build_audit_passed", False),
            "validate_source_dashboard_audit_passed": availability.get("validate_source_dashboard_audit_passed", False),
            "data_refresh_audit_passed": availability.get("data_refresh_audit_passed", False),
        },
        "dashboard_checks": {
            "source_workflow_mode": "build_from_existing_data",
            "required_cards_present": all(artifacts[key].exists() for key in REQUIRED_CARDS),
            "business_output_drift_count": availability.get("business_output_drift_count", 1),
            "protected_path_modifications_detected": availability.get("protected_path_modifications_detected", True),
            "required_validate_fallback_used": resolution.get("required_validate_fallback_used", True),
            "optional_validate_fallback_used": resolution.get("optional_validate_fallback_used", False),
            "comparison_completed": comparison.get("comparison_completed", False),
        },
        "boundary": {**BOUNDARY, **{k: boundary.get(k, v) for k, v in BOUNDARY.items()}},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json_markdown(
        artifacts["build_output_dashboard_audit_json"],
        audit,
        artifacts["build_output_dashboard_audit_report"],
        render_audit_report(audit),
    )
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "dashboard_checks": audit["dashboard_checks"],
        "boundary": audit["boundary"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["build_output_dashboard_audit_json"]),
        "report_path": str(artifacts["build_output_dashboard_audit_report"]),
    }


def _checks(paths: ProjectPaths, artifacts: dict, payloads: dict) -> dict[str, bool]:
    availability = payloads.get("build_output_input_availability", {})
    resolution = payloads.get("build_output_source_resolution", {})
    source_trace = payloads.get("build_output_dashboard_source_trace", {})
    boundary = payloads.get("build_output_dashboard_boundary_check", {})
    manifest = payloads.get("build_output_dashboard_manifest", {})
    summary = payloads.get("build_output_dashboard_summary", {})
    comparison = payloads.get("validate_dashboard_vs_build_dashboard_comparison", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload),
        "repeatability_audit_passed": availability.get("repeatability_audit_passed", False) is True,
        "gated_build_audit_passed": availability.get("gated_build_audit_passed", False) is True,
        "validate_source_dashboard_audit_passed": availability.get("validate_source_dashboard_audit_passed", False) is True,
        "data_refresh_audit_passed": availability.get("data_refresh_audit_passed", False) is True,
        "source_workflow_mode_build": resolution.get("source_workflow_mode") == "build_from_existing_data",
        "business_output_drift_count_zero": availability.get("business_output_drift_count") == 0,
        "protected_path_modification_clean": availability.get("protected_path_modifications_detected") is False,
        "required_cards_present": all(artifacts[key].exists() and payloads.get(key) for key in REQUIRED_CARDS),
        "required_validate_fallback_not_used": resolution.get("required_validate_fallback_used", True) is False,
        "comparison_completed": comparison.get("comparison_completed", False) is True,
        "source_trace_complete": source_trace.get("source_trace_complete", False) is True,
        "source_trace_hashes_match": _source_hashes_match(paths, source_trace),
        "boundary_overall_passed": boundary.get("overall_passed", False) is True,
        "boundary_clean": all(boundary.get(key) is value for key, value in BOUNDARY.items()),
        "forbidden_artifacts_absent": not boundary.get("forbidden_artifacts_present", []),
        "forbidden_positive_wording_absent": not boundary.get("forbidden_wording_positive_hits", []),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-BUILD-OUTPUT-OWNER-DASHBOARD-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-BUILD-OUTPUT-OWNER-DASHBOARD-SUMMARY",
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

