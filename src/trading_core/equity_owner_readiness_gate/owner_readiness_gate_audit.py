"""Audit for v0.8.13 owner readiness gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_readiness_gate.gate_config import (
    BOUNDARY,
    DEFAULT_AS_OF_DATE,
    FILES,
    FORBIDDEN_RECOMMENDATIONS,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    TARGET_VERSION,
    artifact_paths,
)
from trading_core.equity_owner_readiness_gate.gate_report import render_audit
from trading_core.equity_owner_readiness_gate.io import load_json, write_json, write_text
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_readiness_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)
    availability = payloads.get("owner_readiness_gate_input_availability", {})
    decision = payloads.get("owner_readiness_gate_decision", {})
    score_gate = payloads.get("owner_readiness_score_gate", {})
    boundary = payloads.get("owner_readiness_gate_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-READINESS-GATE-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("owner_readiness_gate_config", {}).get("mode", "evaluate_owner_readiness_gate"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "owner_daily_pack_history_audit_passed": availability.get("owner_daily_pack_history_audit_passed") is True,
            "owner_daily_pack_audit_passed": availability.get("owner_daily_pack_audit_passed") is True,
        },
        "gate_checks": {
            "owner_readiness_score_valid": isinstance(score_gate.get("actual_value"), int) and 0 <= score_gate.get("actual_value") <= 100,
            "minimum_owner_readiness_score": score_gate.get("threshold"),
            "actual_owner_readiness_score": score_gate.get("actual_value"),
            "required_gates_passed": decision.get("required_gates_passed"),
            "decision": decision.get("decision"),
            "owner_operationally_acceptable": decision.get("owner_operationally_acceptable"),
            "gate_decision_consistent": _decision_consistent(payloads),
            "blocked_state_represented_correctly": _blocked_state_represented(payloads),
            "no_automatic_waiver": payloads.get("quality_exception_candidate_list", {}).get("auto_waiver_allowed") is False,
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json(artifacts["owner_readiness_gate_audit_json"], audit)
    write_text(artifacts["owner_readiness_gate_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "gate_checks": audit["gate_checks"],
        "boundary": audit["boundary"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["owner_readiness_gate_audit_json"]),
        "report_path": str(artifacts["owner_readiness_gate_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    availability = payloads.get("owner_readiness_gate_input_availability", {})
    decision = payloads.get("owner_readiness_gate_decision", {})
    recommendation = payloads.get("owner_release_recommendation", {})
    trace = payloads.get("owner_readiness_gate_source_trace", {})
    boundary = payloads.get("owner_readiness_gate_boundary_check", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "owner_daily_pack_history_audit_passed": availability.get("owner_daily_pack_history_audit_passed") is True,
        "owner_daily_pack_audit_passed": availability.get("owner_daily_pack_audit_passed") is True,
        "source_workflow_mode_build_from_existing_data": decision.get("source_workflow_mode") == "build_from_existing_data",
        "owner_readiness_score_valid": isinstance(decision.get("actual_owner_readiness_score"), int) and 0 <= decision.get("actual_owner_readiness_score") <= 100,
        "threshold_policy_applied_correctly": _threshold_policy_applied(payloads),
        "gate_decision_consistent": _decision_consistent(payloads),
        "blocked_state_represented_correctly": _blocked_state_represented(payloads),
        "no_automatic_waiver": payloads.get("quality_exception_candidate_list", {}).get("auto_waiver_allowed") is False,
        "no_forbidden_recommendation_categories": recommendation.get("recommendation") not in FORBIDDEN_RECOMMENDATIONS,
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and _boundary_fields_clean(boundary),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits"),
        "manifest_generated": payloads.get("owner_readiness_gate_manifest", {}).get("manifest_id") == "A-SHARE-OWNER-READINESS-GATE-MANIFEST",
        "summary_generated": payloads.get("owner_readiness_gate_summary", {}).get("summary_id") == "A-SHARE-OWNER-READINESS-GATE-SUMMARY",
    }


def _threshold_policy_applied(payloads: dict[str, Any]) -> bool:
    policy = payloads.get("owner_readiness_threshold_policy", {})
    score_gate = payloads.get("owner_readiness_score_gate", {})
    return policy.get("minimum_owner_readiness_score") == score_gate.get("threshold")


def _decision_consistent(payloads: dict[str, Any]) -> bool:
    decision = payloads.get("owner_readiness_gate_decision", {})
    gate_keys = [key for key in FILES if key.endswith("_gate") and key in payloads and key != "owner_readiness_gate"]
    failed = [key for key in gate_keys if payloads.get(key, {}).get("passed") is not True]
    if failed:
        return decision.get("decision") == "blocked" and decision.get("required_gates_passed") is False and decision.get("owner_operationally_acceptable") is False
    if decision.get("required_gates_passed") is not True or decision.get("owner_operationally_acceptable") is not True:
        return False
    if decision.get("warnings"):
        return decision.get("decision") == "owner_operationally_acceptable_with_warnings"
    return decision.get("decision") == "owner_operationally_acceptable"


def _blocked_state_represented(payloads: dict[str, Any]) -> bool:
    decision = payloads.get("owner_readiness_gate_decision", {})
    if decision.get("decision") != "blocked":
        return True
    return decision.get("owner_operationally_acceptable") is False and decision.get("required_gates_passed") is False and bool(decision.get("blocking_reasons"))


def _boundary_fields_clean(boundary: dict[str, Any]) -> bool:
    return all(boundary.get(key) is expected for key, expected in BOUNDARY.items())


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
