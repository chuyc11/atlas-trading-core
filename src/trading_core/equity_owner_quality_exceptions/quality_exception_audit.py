"""Audit for v0.8.14 owner quality exception workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_quality_exceptions.exception_report import render_audit
from trading_core.equity_owner_quality_exceptions.exception_workflow_config import (
    BOUNDARY,
    DEFAULT_AS_OF_DATE,
    FILES,
    FORBIDDEN_COMMAND_FRAGMENTS,
    FORBIDDEN_ROUTES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    TARGET_VERSION,
    artifact_paths,
)
from trading_core.equity_owner_quality_exceptions.io import load_json, write_json, write_text
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_quality_exceptions(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)
    intake = payloads.get("blocked_gate_intake", {})
    gap = payloads.get("owner_readiness_gap_analysis", {})
    waiver = payloads.get("manual_waiver_decision_record", {})
    boundary = payloads.get("quality_exception_boundary_check", {})
    availability = payloads.get("quality_exception_input_availability", {})
    classification = payloads.get("quality_exception_classification", {})
    routing = payloads.get("exception_routing_matrix", {})
    developer = payloads.get("developer_follow_up_tracker", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-QUALITY-EXCEPTION-WORKFLOW-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("quality_exception_workflow_config", {}).get("mode", "build_escalation_workflow"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "owner_readiness_gate_audit_passed": availability.get("owner_readiness_gate_audit_passed") is True,
            "source_gate_decision": availability.get("source_gate_decision"),
            "blocked_state_represented_correctly": availability.get("blocked_state_represented_correctly") is True,
        },
        "exception_checks": {
            "blocked_gate_decision_preserved": intake.get("blocked_state_preserved") is True,
            "owner_operationally_acceptable": intake.get("owner_operationally_acceptable"),
            "minimum_owner_readiness_score": intake.get("minimum_owner_readiness_score"),
            "actual_owner_readiness_score": intake.get("actual_owner_readiness_score"),
            "readiness_score_gap": gap.get("score_gap"),
            "quality_exceptions_classified": classification.get("quality_exceptions_classified") is True,
            "waiver_policy_exists": bool(payloads.get("manual_waiver_policy")),
            "auto_waiver_allowed": waiver.get("auto_waiver_allowed"),
            "manual_waiver_approval_recorded": waiver.get("manual_waiver_approval_recorded"),
            "waiver_changes_gate_decision": waiver.get("waiver_changes_gate_decision"),
            "no_forbidden_escalation_routes": routing.get("no_forbidden_routes") is True,
            "no_forbidden_follow_up_commands": developer.get("no_forbidden_follow_up_commands") is True,
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json(artifacts["quality_exception_audit_json"], audit)
    write_text(artifacts["quality_exception_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "exception_checks": audit["exception_checks"],
        "boundary": audit["boundary"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["quality_exception_audit_json"]),
        "report_path": str(artifacts["quality_exception_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    intake = payloads.get("blocked_gate_intake", {})
    gap = payloads.get("owner_readiness_gap_analysis", {})
    waiver = payloads.get("manual_waiver_decision_record", {})
    boundary = payloads.get("quality_exception_boundary_check", {})
    trace = payloads.get("quality_exception_source_trace", {})
    manifest = payloads.get("quality_exception_manifest", {})
    summary = payloads.get("quality_exception_summary", {})
    classification = payloads.get("quality_exception_classification", {})
    escalation = payloads.get("escalation_workflow", {})
    developer = payloads.get("developer_follow_up_tracker", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "input_owner_readiness_gate_audit_passed": payloads.get("quality_exception_input_availability", {}).get("owner_readiness_gate_audit_passed") is True,
        "source_gate_decision_preserved": intake.get("source_gate_decision") == "blocked",
        "blocked_gate_decision_preserved": intake.get("blocked_state_preserved") is True,
        "owner_operationally_acceptable_false": intake.get("owner_operationally_acceptable") is False,
        "readiness_score_gap_represented": gap.get("score_gap") == max(intake.get("minimum_owner_readiness_score", 0) - intake.get("actual_owner_readiness_score", 0), 0),
        "quality_exceptions_classified": classification.get("quality_exceptions_classified") is True,
        "auto_waiver_false": waiver.get("auto_waiver_allowed") is False,
        "manual_waiver_approval_false": waiver.get("manual_waiver_approval_recorded") is False,
        "waiver_does_not_change_gate_decision": waiver.get("waiver_changes_gate_decision") is False,
        "no_forbidden_escalation_routes": _routes_clean(escalation),
        "no_forbidden_follow_up_commands": developer.get("no_forbidden_follow_up_commands") is True and _follow_up_commands_clean(developer),
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and _boundary_fields_clean(boundary),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits"),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-QUALITY-EXCEPTION-WORKFLOW-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-QUALITY-EXCEPTION-WORKFLOW-SUMMARY",
    }


def _routes_clean(escalation: dict[str, Any]) -> bool:
    return not any(step.get("route") in FORBIDDEN_ROUTES for step in escalation.get("steps", []))


def _follow_up_commands_clean(developer: dict[str, Any]) -> bool:
    for item in developer.get("items", []):
        for command in item.get("safe_audit_only_commands", []):
            lower = command.lower()
            if any(fragment.lower() in lower for fragment in FORBIDDEN_COMMAND_FRAGMENTS if fragment != "run-daily"):
                return False
            if "run-daily" in lower:
                return False
    return True


def _boundary_fields_clean(boundary: dict[str, Any]) -> bool:
    for key, expected in BOUNDARY.items():
        if boundary.get(key) is not expected:
            return False
    return True


def _source_hashes_match(paths: ProjectPaths, trace: dict[str, Any]) -> bool:
    for row in trace.get("source_artifacts", []):
        path = Path(row.get("path", ""))
        if not path.is_absolute():
            path = paths.project_root / path
        if row.get("required") is True and (not path.exists() or not row.get("sha256")):
            return False
        if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
            return False
    return True
