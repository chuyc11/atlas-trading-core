"""Audit for v0.8.11 owner daily pack."""

from __future__ import annotations

import hashlib
import json

from trading_core.equity_owner_daily_pack.daily_pack_config import (
    BOUNDARY,
    FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    TARGET_VERSION,
    artifact_paths,
)
from trading_core.equity_owner_daily_pack.daily_pack_boundary import (
    _forbidden_artifacts,
    _forbidden_wording_hits,
)
from trading_core.equity_owner_daily_pack.daily_pack_report import render_audit_report
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


def audit_a_share_owner_daily_pack(*, as_of_date: str, paths: ProjectPaths | None = None) -> dict:
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
    availability = payloads.get("daily_pack_input_availability", {})
    summary = payloads.get("daily_pack_summary", {})
    boundary = payloads.get("daily_pack_boundary_check", {})
    safe = payloads.get("safe_action_digest", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-DAILY-PACK-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": "build_owner_operations_decision_pack",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "build_output_ops_refresh_audit_passed": availability.get("build_output_ops_refresh_audit_passed", False),
            "build_output_dashboard_audit_passed": availability.get("build_output_dashboard_audit_passed", False),
            "repeatability_audit_passed": availability.get("repeatability_audit_passed", False),
            "gated_build_audit_passed": availability.get("gated_build_audit_passed", False),
        },
        "daily_pack_checks": {
            "source_workflow_mode": summary.get("source_workflow_mode"),
            "daily_pack_generated": summary.get("daily_pack_generated", False),
            "owner_daily_runbook_generated": summary.get("owner_daily_runbook_generated", False),
            "owner_operations_decision_pack_generated": summary.get("owner_operations_decision_pack_generated", False),
            "not_investment_decision_pack": summary.get("not_investment_decision_pack", False),
            "business_output_drift_count": summary.get("business_output_drift_count"),
            "protected_path_modifications_detected": summary.get("protected_path_modifications_detected"),
            "automatic_action_count": summary.get("automatic_action_count"),
            "execute_remediation_actions": summary.get("execute_remediation_actions", True),
            "external_notifications_sent": summary.get("external_notifications_sent", True),
            "no_forbidden_decision_categories": not summary.get("forbidden_decision_categories_detected", []),
            "no_forbidden_safe_action_types": not safe.get("forbidden_safe_action_type_hits", []),
        },
        "boundary": {**BOUNDARY, **{k: boundary.get(k, v) for k, v in BOUNDARY.items()}},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json_markdown(
        artifacts["owner_daily_pack_audit_json"],
        audit,
        artifacts["owner_daily_pack_audit_report"],
        render_audit_report(audit),
    )
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "daily_pack_checks": audit["daily_pack_checks"],
        "boundary": audit["boundary"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["owner_daily_pack_audit_json"]),
        "report_path": str(artifacts["owner_daily_pack_audit_report"]),
    }


def _checks(paths: ProjectPaths, artifacts: dict, payloads: dict) -> dict[str, bool]:
    availability = payloads.get("daily_pack_input_availability", {})
    resolution = payloads.get("daily_pack_source_resolution", {})
    trace = payloads.get("daily_pack_source_trace", {})
    boundary = payloads.get("daily_pack_boundary_check", {})
    manifest = payloads.get("daily_pack_manifest", {})
    summary = payloads.get("daily_pack_summary", {})
    decision = payloads.get("owner_operations_decision_pack", {})
    safe = payloads.get("safe_action_digest", {})
    as_of_date = summary.get("as_of_date") or payloads.get("daily_pack_config", {}).get("as_of_date")
    current_forbidden_artifacts = _forbidden_artifacts(paths, as_of_date) if as_of_date else []
    current_forbidden_wording = _forbidden_wording_hits(paths, as_of_date) if as_of_date else []
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload),
        "build_output_ops_refresh_audit_passed": availability.get("build_output_ops_refresh_audit_passed", False) is True,
        "build_output_dashboard_audit_passed": availability.get("build_output_dashboard_audit_passed", False) is True,
        "repeatability_audit_passed": availability.get("repeatability_audit_passed", False) is True,
        "gated_build_audit_passed": availability.get("gated_build_audit_passed", False) is True,
        "source_workflow_mode_build": resolution.get("source_workflow_mode") == "build_from_existing_data",
        "daily_pack_generated": summary.get("daily_pack_generated", False) is True,
        "owner_daily_runbook_generated": summary.get("owner_daily_runbook_generated", False) is True,
        "owner_operations_decision_pack_generated": summary.get("owner_operations_decision_pack_generated", False) is True,
        "not_investment_decision_pack": summary.get("not_investment_decision_pack", False) is True,
        "business_output_drift_count_zero": summary.get("business_output_drift_count") == 0,
        "protected_path_modification_clean": summary.get("protected_path_modifications_detected") is False,
        "automatic_action_count_zero": summary.get("automatic_action_count") == 0,
        "execute_remediation_actions_false": summary.get("execute_remediation_actions", True) is False,
        "external_notifications_sent_false": summary.get("external_notifications_sent", True) is False,
        "no_forbidden_decision_categories": not decision.get("forbidden_decision_categories_detected", []),
        "no_forbidden_safe_action_types": not safe.get("forbidden_safe_action_type_hits", []),
        "source_trace_complete": trace.get("source_trace_complete", False) is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_overall_passed": boundary.get("overall_passed", False) is True,
        "boundary_clean": all(boundary.get(key) is value for key, value in BOUNDARY.items()),
        "forbidden_artifacts_absent": not boundary.get("forbidden_artifacts_present", []) and not current_forbidden_artifacts,
        "forbidden_positive_wording_absent": not boundary.get("forbidden_wording_positive_hits", []) and not current_forbidden_wording,
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-DAILY-PACK-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-DAILY-PACK-SUMMARY",
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
