"""Audit for v0.8.20 owner gate outcome."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_v0820_gate_outcome.io import load_json, write_json, write_text
from trading_core.equity_owner_v0820_gate_outcome.outcome_config import BOUNDARY, DEFAULT_AS_OF_DATE, FILES, FORBIDDEN_POSITIVE_WORDING, RECOMMENDED_NEXT_VERSION, REPORTS, TARGET_VERSION, artifact_paths
from trading_core.equity_owner_v0820_gate_outcome.report import render_audit
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_v0820_gate_outcome(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)
    availability = payloads.get("v0820_input_availability", {})
    branch = payloads.get("v0820_branch_decision", {})
    controlled = payloads.get("controlled_gate_reevaluation_outcome", {})
    closeout = payloads.get("final_blocked_closeout", {})
    summary = payloads.get("v0820_owner_outcome_summary", {})
    boundary = payloads.get("v0820_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-V0820-GATE-OUTCOME-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("v0820_outcome_config", {}).get("mode", "build_and_audit_v0820_outcome"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "evidence_backed_prep_audit_passed": availability.get("evidence_backed_prep_audit_passed") is True,
            "source_gate_decision": availability.get("source_gate_decision"),
            "source_gate_decision_preserved": availability.get("source_gate_decision_preserved"),
        },
        "outcome_checks": {
            "selected_branch": branch.get("selected_branch"),
            "branch_decision_consistent": summary.get("branch_decision_consistent") is True,
            "controlled_reevaluation_executed": controlled.get("controlled_reevaluation_executed") is True,
            "final_blocked_closeout_generated": closeout.get("final_blocked_closeout_generated") is True,
            "new_controlled_readiness_score_generated": controlled.get("new_controlled_readiness_score_generated") is True,
            "new_controlled_gate_decision_generated": controlled.get("new_controlled_gate_decision_generated") is True,
            "threshold_lowered": False,
            "auto_waiver_allowed": False,
            "manual_waiver_approval_recorded": False,
            "waiver_used_for_outcome": False,
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "test_policy": {
            "full_pytest_run": False,
            "targeted_pytest_required": True,
            "full_pytest_deferred_until": "v0.9.0-or-big-version-closeout",
        },
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json(artifacts["v0820_outcome_audit_json"], audit)
    write_text(artifacts["v0820_outcome_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "outcome_checks": audit["outcome_checks"],
        "boundary": audit["boundary"],
        "test_policy": audit["test_policy"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["v0820_outcome_audit_json"]),
        "report_path": str(artifacts["v0820_outcome_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    config = payloads.get("v0820_outcome_config", {})
    availability = payloads.get("v0820_input_availability", {})
    resolution = payloads.get("v0820_source_resolution", {})
    alignment = payloads.get("v0820_date_alignment", {})
    branch = payloads.get("v0820_branch_decision", {})
    controlled = payloads.get("controlled_gate_reevaluation_outcome", {})
    closeout = payloads.get("final_blocked_closeout", {})
    threshold = payloads.get("threshold_preservation_check", {})
    waiver = payloads.get("waiver_exclusion_check", {})
    preservation = payloads.get("boundary_preservation_check", {})
    summary = payloads.get("v0820_owner_outcome_summary", {})
    trace = payloads.get("v0820_source_trace", {})
    boundary = payloads.get("v0820_boundary_check", {})
    manifest = payloads.get("v0820_manifest", {})
    branch_is_closeout = branch.get("selected_branch") == "final_blocked_closeout"
    branch_is_controlled = branch.get("selected_branch") == "controlled_gate_reevaluation"
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "config_preserves_boundaries": _config_preserves_boundaries(config),
        "input_availability_passed": availability.get("overall_passed") is True,
        "source_resolution_passed": resolution.get("overall_passed") is True,
        "date_alignment_passed": alignment.get("overall_passed") is True,
        "input_evidence_backed_prep_audit_passed": availability.get("evidence_backed_prep_audit_passed") is True,
        "branch_decision_generated": branch.get("decision_id") == "A-SHARE-V0820-BRANCH-DECISION",
        "branch_decision_consistent_with_v0819": _branch_consistent(branch, availability),
        "controlled_outcome_generated": controlled.get("outcome_id") == "A-SHARE-CONTROLLED-GATE-REEVALUATION-OUTCOME",
        "final_blocked_closeout_generated": closeout.get("closeout_id") == "A-SHARE-FINAL-BLOCKED-CLOSEOUT",
        "controlled_branch_only_when_eligible": not branch_is_controlled or (availability.get("v0819_ready_for_controlled_gate_reevaluation") is True and availability.get("blocking_gap_count") in (0, None)),
        "closeout_branch_does_not_execute_reevaluation": not branch_is_closeout or controlled.get("controlled_reevaluation_executed") is False,
        "closeout_branch_no_new_score_or_decision": not branch_is_closeout or (controlled.get("new_controlled_readiness_score_generated") is False and controlled.get("new_controlled_gate_decision_generated") is False),
        "controlled_branch_generates_score_and_decision": not branch_is_controlled or (controlled.get("new_controlled_readiness_score_generated") is True and controlled.get("new_controlled_gate_decision_generated") is True),
        "threshold_preserved": threshold.get("threshold_preserved") is True and threshold.get("threshold_lowered") is False,
        "waiver_excluded": waiver.get("auto_waiver_allowed") is False and waiver.get("manual_waiver_approval_recorded") is False and waiver.get("waiver_used_for_outcome") is False,
        "boundary_preserved": all(preservation.get(key) is expected for key, expected in BOUNDARY.items()),
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-V0820-OUTCOME-SUMMARY",
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and all(boundary.get(key) is expected for key, expected in BOUNDARY.items()),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and _markdown_wording_clean(paths, as_of_date),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-V0820-GATE-OUTCOME-MANIFEST",
        "targeted_pytest_required": manifest.get("targeted_pytest_required") is True,
        "full_pytest_run_false": manifest.get("full_pytest_run") is False,
    }


def _branch_consistent(branch: dict[str, Any], availability: dict[str, Any]) -> bool:
    eligible = (
        availability.get("v0819_ready_for_controlled_gate_reevaluation") is True
        and availability.get("v0819_eligibility_decision") in {"eligible", "ready_for_controlled_gate_reevaluation"}
        and int(availability.get("blocking_gap_count") or 0) == 0
    )
    return (branch.get("selected_branch") == "controlled_gate_reevaluation") == eligible


def _config_preserves_boundaries(config: dict[str, Any]) -> bool:
    false_fields = [
        "rerun_build_from_existing_data",
        "rerun_daily_pack",
        "allow_broker",
        "allow_real_orders",
        "allow_order_preview",
        "allow_buy_sell_signals",
        "allow_public_network_refresh",
        "allow_full_research_run",
        "allow_old_run_daily",
        "execute_official_forward_dry_run_day2",
        "execute_remediation_actions",
        "send_external_notifications",
    ]
    return all(config.get(key) is False for key in false_fields) and config.get("does_not_lower_threshold") is True and config.get("does_not_auto_waive") is True


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


def _markdown_wording_clean(paths: ProjectPaths, as_of_date: str) -> bool:
    root = paths.outputs_dir / "equity_owner_v0820_gate_outcome" / "daily" / as_of_date
    if not root.exists():
        return True
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if any(phrase in text for phrase in FORBIDDEN_POSITIVE_WORDING):
            return False
    return True

