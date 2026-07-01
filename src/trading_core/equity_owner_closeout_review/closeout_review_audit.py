"""Audit for v0.8.21 owner-readiness closeout review."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_closeout_review.closeout_config import BOUNDARY, DEFAULT_AS_OF_DATE, FILES, FORBIDDEN_POSITIVE_WORDING, RECOMMENDED_NEXT_VERSION, REPORTS, TARGET_VERSION, artifact_paths
from trading_core.equity_owner_closeout_review.io import load_json, write_json, write_text
from trading_core.equity_owner_closeout_review.report import render_audit
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_closeout_review(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)
    availability = payloads.get("closeout_input_availability", {})
    final_review = payloads.get("final_blocked_closeout_review", {})
    boundary = payloads.get("closeout_boundary_check", {})
    summary = payloads.get("closeout_summary", {})
    rc_decision = payloads.get("v090_release_candidate_readiness_decision", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-CLOSEOUT-REVIEW-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("closeout_review_config", {}).get("mode", "build_v090_rc_scope"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "v0820_outcome_audit_passed": availability.get("v0820_outcome_audit_passed") is True,
            "selected_v0820_branch": availability.get("selected_v0820_branch"),
            "source_gate_decision": availability.get("source_gate_decision"),
        },
        "closeout_checks": {
            "blocked_state_lineage_represented": checks["blocked_state_lineage_represented"],
            "readiness_score_lineage_represented": checks["readiness_score_lineage_represented"],
            "score_gap_represented": checks["score_gap_represented"],
            "new_gate_score_generated": False,
            "new_gate_decision_generated": False,
            "full_pytest_executed": False,
            "v090_full_regression_plan_generated": checks["v090_full_regression_plan_generated"],
            "v090_audit_sweep_plan_generated": checks["v090_audit_sweep_plan_generated"],
            "v090_rc_decision_consistent": rc_decision.get("decision") == "ready_with_known_blocked_owner_readiness_state",
            "blocked_state_intentional": final_review.get("blocked_state_intentional"),
            "blocked_state_audited": final_review.get("blocked_state_audited"),
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "test_policy": {
            "full_pytest_run": False,
            "targeted_pytest_required": True,
            "full_pytest_deferred_until": "v0.9.0",
        },
        "summary": summary,
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json(artifacts["closeout_review_audit_json"], audit)
    write_text(artifacts["closeout_review_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "closeout_checks": audit["closeout_checks"],
        "boundary": audit["boundary"],
        "test_policy": audit["test_policy"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["closeout_review_audit_json"]),
        "report_path": str(artifacts["closeout_review_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    config = payloads.get("closeout_review_config", {})
    availability = payloads.get("closeout_input_availability", {})
    resolution = payloads.get("closeout_source_resolution", {})
    alignment = payloads.get("closeout_date_alignment", {})
    lineage = payloads.get("v0813_to_v0820_lineage_review", {})
    blocked_lineage = payloads.get("blocked_decision_lineage", {})
    score_lineage = payloads.get("readiness_score_lineage", {})
    evidence_lineage = payloads.get("evidence_insufficiency_lineage", {})
    final_review = payloads.get("final_blocked_closeout_review", {})
    blockers = payloads.get("unresolved_blocker_register", {})
    rc_scope = payloads.get("v090_rc_scope_proposal", {})
    regression_plan = payloads.get("v090_full_regression_plan", {})
    audit_sweep_plan = payloads.get("v090_audit_sweep_plan", {})
    docs_freeze = payloads.get("v090_documentation_freeze_checklist", {})
    risk_register = payloads.get("v090_release_risk_register", {})
    rc_decision = payloads.get("v090_release_candidate_readiness_decision", {})
    trace = payloads.get("closeout_source_trace", {})
    boundary = payloads.get("closeout_boundary_check", {})
    manifest = payloads.get("closeout_manifest", {})
    summary = payloads.get("closeout_summary", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "config_preserves_boundaries": _config_preserves_boundaries(config),
        "input_availability_passed": availability.get("overall_passed") is True,
        "source_resolution_passed": resolution.get("overall_passed") is True,
        "date_alignment_passed": alignment.get("overall_passed") is True,
        "v0820_outcome_audit_passed": availability.get("v0820_outcome_audit_passed") is True,
        "selected_branch_final_blocked_closeout": availability.get("selected_v0820_branch") == "final_blocked_closeout",
        "source_gate_decision_blocked": availability.get("source_gate_decision") == "blocked",
        "lineage_review_generated": lineage.get("lineage_id") == "A-SHARE-V0813-TO-V0820-LINEAGE-REVIEW",
        "blocked_state_lineage_represented": blocked_lineage.get("blocked_decision_preserved") is True,
        "readiness_score_lineage_represented": score_lineage.get("previous_readiness_score") == summary.get("previous_readiness_score") and score_lineage.get("minimum_owner_readiness_score") == summary.get("minimum_owner_readiness_score"),
        "score_gap_represented": score_lineage.get("score_gap") == summary.get("score_gap") and summary.get("score_gap") is not None,
        "evidence_insufficiency_lineage_generated": evidence_lineage.get("evidence_insufficient") is True,
        "final_blocked_closeout_review_generated": final_review.get("review_id") == "A-SHARE-FINAL-BLOCKED-CLOSEOUT-REVIEW",
        "blocked_state_not_misrepresented": final_review.get("blocked_state_misrepresented_as_acceptable") is False,
        "unresolved_blocker_register_generated": blockers.get("unresolved_blocker_count", 0) >= 7,
        "v090_rc_scope_generated": rc_scope.get("proposal_id") == "A-SHARE-V090-RC-SCOPE-PROPOSAL",
        "v090_full_regression_plan_generated": regression_plan.get("plan_id") == "A-SHARE-V090-FULL-REGRESSION-PLAN" and regression_plan.get("full_pytest_run") is False,
        "v090_audit_sweep_plan_generated": audit_sweep_plan.get("audit_count", 0) >= 9,
        "v090_documentation_freeze_checklist_generated": docs_freeze.get("checklist_id") == "A-SHARE-V090-DOCUMENTATION-FREEZE-CHECKLIST",
        "v090_release_risk_register_generated": risk_register.get("risk_count", 0) >= 10,
        "v090_rc_decision_consistent": rc_decision.get("decision") == "ready_with_known_blocked_owner_readiness_state",
        "new_gate_score_not_generated": summary.get("new_gate_score_generated") is False,
        "new_gate_decision_not_generated": summary.get("new_gate_decision_generated") is False,
        "full_pytest_not_executed": summary.get("full_pytest_run") is False and regression_plan.get("full_pytest_run") is False,
        "threshold_not_lowered": boundary.get("threshold_lowered") is False,
        "auto_waiver_false": boundary.get("auto_waiver_allowed") is False,
        "manual_waiver_approval_false": boundary.get("manual_waiver_approval_recorded") is False,
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and all(boundary.get(key) is expected for key, expected in BOUNDARY.items()),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and _markdown_wording_clean(paths, as_of_date),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-CLOSEOUT-REVIEW-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-CLOSEOUT-REVIEW-SUMMARY",
        "targeted_pytest_required": manifest.get("targeted_pytest_required") is True,
        "full_pytest_run_false": manifest.get("full_pytest_run") is False,
    }


def _config_preserves_boundaries(config: dict[str, Any]) -> bool:
    false_fields = [
        "rerun_owner_readiness_gate",
        "rerun_build_from_existing_data",
        "rerun_daily_pack",
        "generate_new_gate_score",
        "generate_new_gate_decision",
        "execute_full_pytest",
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
    for row in trace.get("source_artifacts", []):
        path = Path(row.get("path", ""))
        if not path.is_absolute():
            path = paths.project_root / path
        if row.get("required") is True and (not path.exists() or not row.get("sha256")):
            return False
        if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
            return False
    for row in trace.get("output_artifacts", []):
        path = Path(row.get("path", ""))
        if not path.is_absolute():
            path = paths.project_root / path
        if row.get("required") is True and not path.exists():
            return False
        if row.get("artifact_key") == "closeout_source_trace":
            continue
        if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
            return False
    return True


def _markdown_wording_clean(paths: ProjectPaths, as_of_date: str) -> bool:
    root = paths.outputs_dir / "equity_owner_closeout_review" / "daily" / as_of_date
    if not root.exists():
        return True
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if any(phrase in text for phrase in FORBIDDEN_POSITIVE_WORDING):
            return False
    return True
