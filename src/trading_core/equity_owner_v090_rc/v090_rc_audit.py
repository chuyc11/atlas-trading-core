"""Audit for v0.9.0 owner-readiness RC closeout."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_v090_rc.io import load_json, write_json, write_text
from trading_core.equity_owner_v090_rc.report import render_audit
from trading_core.equity_owner_v090_rc.v090_config import BOUNDARY, DEFAULT_AS_OF_DATE, FILES, FORBIDDEN_POSITIVE_WORDING, RECOMMENDED_NEXT_VERSION, REPORTS, TARGET_VERSION, artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_v090_rc(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)
    availability = payloads.get("v090_input_availability", {})
    full_pytest = payloads.get("v090_full_pytest_result", {})
    audit_sweep = payloads.get("v090_audit_sweep_result", {})
    boundary_sweep = payloads.get("v090_boundary_sweep_result", {})
    trace_sweep = payloads.get("v090_source_trace_sweep_result", {})
    docs = payloads.get("v090_documentation_freeze_result", {})
    disclosure = payloads.get("v090_known_blocked_state_disclosure", {})
    boundary = payloads.get("v090_boundary_check", {})
    decision = payloads.get("v090_release_candidate_decision", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-V090-RC-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("v090_rc_config", {}).get("mode", "run_v090_full_regression"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "v0821_closeout_review_audit_passed": availability.get("v0821_closeout_review_audit_passed") is True,
            "source_gate_decision": availability.get("source_gate_decision"),
            "v090_rc_readiness_source_decision": availability.get("v090_rc_readiness_source_decision"),
        },
        "regression_checks": {
            "full_pytest_run": full_pytest.get("full_pytest_run") is True,
            "full_pytest_passed": full_pytest.get("overall_passed") is True,
            "audit_sweep_run": audit_sweep.get("audit_sweep_run") is True,
            "audit_sweep_passed": audit_sweep.get("audit_sweep_passed") is True,
            "boundary_sweep_passed": boundary_sweep.get("boundary_sweep_passed") is True,
            "source_trace_sweep_passed": trace_sweep.get("source_trace_sweep_passed") is True,
            "documentation_freeze_passed": docs.get("documentation_freeze_passed") is True,
        },
        "known_blocked_state_checks": {
            "owner_readiness_state": disclosure.get("owner_readiness_state"),
            "owner_operationally_acceptable": disclosure.get("owner_operationally_acceptable"),
            "blocked_state_intentional": disclosure.get("blocked_state_intentional"),
            "blocked_state_audited": disclosure.get("blocked_state_audited"),
            "blocked_state_misrepresented_as_acceptable": disclosure.get("blocked_state_misrepresented_as_acceptable"),
            "blocks_v090_rc": disclosure.get("blocks_v090_rc"),
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "release_candidate_decision": decision.get("decision") if not blocking else "v090_rc_failed",
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json(artifacts["v090_rc_audit_json"], audit)
    write_text(artifacts["v090_rc_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "regression_checks": audit["regression_checks"],
        "known_blocked_state_checks": audit["known_blocked_state_checks"],
        "boundary": audit["boundary"],
        "release_candidate_decision": audit["release_candidate_decision"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["v090_rc_audit_json"]),
        "report_path": str(artifacts["v090_rc_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    config = payloads.get("v090_rc_config", {})
    availability = payloads.get("v090_input_availability", {})
    resolution = payloads.get("v090_source_resolution", {})
    alignment = payloads.get("v090_date_alignment", {})
    full_pytest = payloads.get("v090_full_pytest_result", {})
    audit_sweep = payloads.get("v090_audit_sweep_result", {})
    boundary_sweep = payloads.get("v090_boundary_sweep_result", {})
    trace_sweep = payloads.get("v090_source_trace_sweep_result", {})
    docs = payloads.get("v090_documentation_freeze_result", {})
    disclosure = payloads.get("v090_known_blocked_state_disclosure", {})
    decision = payloads.get("v090_release_candidate_decision", {})
    summary = payloads.get("v090_owner_release_summary", {})
    trace = payloads.get("v090_source_trace", {})
    boundary = payloads.get("v090_boundary_check", {})
    manifest = payloads.get("v090_manifest", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "config_preserves_boundaries": _config_preserves_boundaries(config),
        "input_availability_passed": availability.get("overall_passed") is True,
        "source_resolution_passed": resolution.get("overall_passed") is True,
        "date_alignment_passed": alignment.get("overall_passed") is True,
        "full_pytest_executed": full_pytest.get("full_pytest_run") is True,
        "full_pytest_passed": full_pytest.get("overall_passed") is True,
        "audit_sweep_passed": audit_sweep.get("audit_sweep_passed") is True,
        "boundary_sweep_passed": boundary_sweep.get("boundary_sweep_passed") is True,
        "source_trace_sweep_passed": trace_sweep.get("source_trace_sweep_passed") is True,
        "documentation_freeze_passed": docs.get("documentation_freeze_passed") is True,
        "known_blocked_state_disclosed": disclosure.get("owner_readiness_state") == "blocked" and disclosure.get("blocks_v090_rc") is False,
        "release_candidate_decision_passed": decision.get("decision") == "v090_rc_passed_with_known_blocked_owner_readiness",
        "owner_release_summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-V090-RC-RELEASE-SUMMARY",
        "owner_readiness_remains_blocked": disclosure.get("owner_readiness_state") == "blocked",
        "owner_operationally_acceptable_false": disclosure.get("owner_operationally_acceptable") is False,
        "blocked_state_not_misrepresented": disclosure.get("blocked_state_misrepresented_as_acceptable") is False,
        "new_gate_score_not_generated": summary.get("new_gate_score_generated") is False,
        "new_gate_decision_not_generated": summary.get("new_gate_decision_generated") is False,
        "threshold_not_lowered": boundary.get("threshold_lowered") is False,
        "auto_waiver_false": boundary.get("auto_waiver_allowed") is False,
        "manual_waiver_approval_false": boundary.get("manual_waiver_approval_recorded") is False,
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and all(boundary.get(key) is expected for key, expected in BOUNDARY.items()),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and _markdown_wording_clean(paths, as_of_date),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-V090-RC-MANIFEST",
    }


def _config_preserves_boundaries(config: dict[str, Any]) -> bool:
    false_fields = [
        "rerun_owner_readiness_gate",
        "rerun_build_from_existing_data",
        "rerun_daily_pack",
        "generate_new_gate_score",
        "generate_new_gate_decision",
        "execute_remediation_actions",
        "send_external_notifications",
        "allow_public_network_refresh",
        "allow_full_research_run",
        "allow_broker",
        "allow_real_orders",
        "allow_order_preview",
        "allow_buy_sell_signals",
        "allow_old_run_daily",
        "execute_official_forward_dry_run_day2",
    ]
    return all(config.get(key) is False for key in false_fields) and config.get("does_not_lower_threshold") is True and config.get("does_not_auto_waive") is True


def _source_hashes_match(paths: ProjectPaths, trace: dict[str, Any]) -> bool:
    for section in ("source_artifacts", "output_artifacts"):
        for row in trace.get(section, []):
            path = Path(row.get("path", ""))
            if not path.is_absolute():
                path = paths.project_root / path
            if row.get("required") is True and not path.exists():
                return False
            if row.get("artifact_key") == "v090_source_trace":
                continue
            if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
                return False
    return True


def _markdown_wording_clean(paths: ProjectPaths, as_of_date: str) -> bool:
    root = paths.outputs_dir / "equity_owner_v090_rc" / "daily" / as_of_date
    if not root.exists():
        return True
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if any(phrase in text for phrase in FORBIDDEN_POSITIVE_WORDING):
            return False
    return True
