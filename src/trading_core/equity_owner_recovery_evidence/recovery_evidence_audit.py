"""Audit for owner recovery evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_recovery_evidence.evidence_config import BOUNDARY, DEFAULT_AS_OF_DATE, FILES, FORBIDDEN_POSITIVE_WORDING, RECOMMENDED_NEXT_VERSION, REPORTS, TARGET_VERSION, artifact_paths
from trading_core.equity_owner_recovery_evidence.evidence_report import render_audit
from trading_core.equity_owner_recovery_evidence.io import load_json, write_json, write_text
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_recovery_evidence(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)
    availability = payloads.get("recovery_evidence_input_availability", {})
    task = payloads.get("recovery_task_evidence_collection", {})
    score = payloads.get("evidence_backed_score_impact_estimate", {})
    prep = payloads.get("next_reevaluation_prep_checklist", {})
    boundary = payloads.get("recovery_evidence_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-RECOVERY-EVIDENCE-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("recovery_evidence_config", {}).get("mode", "collect_recovery_evidence"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "controlled_reevaluation_audit_passed": availability.get("controlled_reevaluation_audit_passed") is True,
            "source_gate_decision": availability.get("source_gate_decision"),
            "reevaluation_skipped": availability.get("reevaluation_skipped"),
        },
        "evidence_checks": {
            "no_fabricated_evidence": not task.get("forbidden_evidence_types_detected"),
            "task_completion_not_fabricated": task.get("task_completion_not_fabricated") is True,
            "actual_audited_score_changed": score.get("actual_audited_score_changed"),
            "new_gate_score_generated": False,
            "new_gate_decision_generated": False,
            "source_gate_decision_preserved": True,
            "evidence_ready_for_next_reevaluation_prep": prep.get("ready_for_evidence_backed_gate_prep"),
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
    write_json(artifacts["recovery_evidence_audit_json"], audit)
    write_text(artifacts["recovery_evidence_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "evidence_checks": audit["evidence_checks"],
        "boundary": audit["boundary"],
        "test_policy": audit["test_policy"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["recovery_evidence_audit_json"]),
        "report_path": str(artifacts["recovery_evidence_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    config = payloads.get("recovery_evidence_config", {})
    availability = payloads.get("recovery_evidence_input_availability", {})
    resolution = payloads.get("recovery_evidence_source_resolution", {})
    alignment = payloads.get("recovery_evidence_date_alignment", {})
    task = payloads.get("recovery_task_evidence_collection", {})
    developer = payloads.get("developer_follow_up_evidence_package", {})
    owner = payloads.get("owner_follow_up_evidence_package", {})
    quality_issue = payloads.get("quality_issue_evidence_package", {})
    warning = payloads.get("warning_mapping_evidence_package", {})
    source_trace_improvement = payloads.get("source_trace_improvement_evidence", {})
    markdown = payloads.get("markdown_quality_improvement_evidence", {})
    completeness = payloads.get("artifact_completeness_evidence", {})
    ledger = payloads.get("readiness_improvement_evidence_ledger", {})
    score = payloads.get("evidence_backed_score_impact_estimate", {})
    grading = payloads.get("evidence_quality_grading", {})
    gaps = payloads.get("evidence_gap_register", {})
    blockers = payloads.get("remaining_blocker_register", {})
    prep = payloads.get("next_reevaluation_prep_checklist", {})
    trace = payloads.get("recovery_evidence_source_trace", {})
    boundary = payloads.get("recovery_evidence_boundary_check", {})
    manifest = payloads.get("recovery_evidence_manifest", {})
    summary = payloads.get("recovery_evidence_summary", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "config_preserves_boundaries": _config_preserves_boundaries(config),
        "input_availability_passed": availability.get("overall_passed") is True,
        "source_resolution_passed": resolution.get("overall_passed") is True,
        "date_alignment_passed": alignment.get("overall_passed") is True,
        "input_controlled_reevaluation_audit_passed": availability.get("controlled_reevaluation_audit_passed") is True,
        "source_gate_decision_preserved": availability.get("source_gate_decision") == "blocked",
        "task_evidence_collection_generated": task.get("collection_id") == "A-SHARE-RECOVERY-TASK-EVIDENCE-COLLECTION",
        "developer_follow_up_evidence_package_generated": developer.get("package_id") == "A-SHARE-DEVELOPER-FOLLOW-UP-EVIDENCE-PACKAGE",
        "owner_follow_up_evidence_package_generated": owner.get("package_id") == "A-SHARE-OWNER-FOLLOW-UP-EVIDENCE-PACKAGE",
        "quality_issue_evidence_package_generated": quality_issue.get("package_id") == "A-SHARE-QUALITY-ISSUE-EVIDENCE-PACKAGE",
        "warning_mapping_evidence_package_generated": warning.get("package_id") == "A-SHARE-WARNING-MAPPING-EVIDENCE-PACKAGE",
        "improvement_evidence_generated": source_trace_improvement.get("evidence_id") and markdown.get("evidence_id") and completeness.get("evidence_id"),
        "readiness_ledger_does_not_rewrite_score": ledger.get("actual_audited_score_changed") is False and ledger.get("new_audited_score") is None,
        "score_estimate_not_gate_score": score.get("not_a_gate_score") is True and score.get("actual_audited_score_changed") is False,
        "evidence_quality_grading_generated": grading.get("grading_id") == "A-SHARE-EVIDENCE-QUALITY-GRADING",
        "evidence_gap_register_generated": gaps.get("register_id") == "A-SHARE-EVIDENCE-GAP-REGISTER",
        "remaining_blocker_register_generated": blockers.get("register_id") == "A-SHARE-REMAINING-BLOCKER-REGISTER",
        "next_reevaluation_prep_defaults_false": prep.get("ready_for_evidence_backed_gate_prep") is False,
        "no_fabricated_evidence": not task.get("forbidden_evidence_types_detected"),
        "task_completion_not_fabricated": task.get("task_completion_not_fabricated") is True,
        "new_gate_score_not_generated": score.get("not_a_gate_score") is True and boundary.get("new_gate_score_generated") is False,
        "new_gate_decision_not_generated": boundary.get("new_gate_decision_generated") is False,
        "threshold_not_lowered": boundary.get("threshold_lowered") is False,
        "waiver_not_approved": boundary.get("auto_waiver_allowed") is False and boundary.get("manual_waiver_approval_recorded") is False,
        "no_forbidden_owner_developer_actions": not developer.get("forbidden_owner_developer_actions_detected"),
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and _boundary_fields_clean(boundary),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and _markdown_wording_clean(paths, as_of_date),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-RECOVERY-EVIDENCE-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-RECOVERY-EVIDENCE-SUMMARY",
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
    return all(config.get(key) is False for key in false_fields) and config.get("does_not_change_gate_decision") is True and config.get("does_not_lower_threshold") is True and config.get("does_not_auto_waive") is True


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


def _markdown_wording_clean(paths: ProjectPaths, as_of_date: str) -> bool:
    root = paths.outputs_dir / "equity_owner_recovery_evidence" / "daily" / as_of_date
    if not root.exists():
        return True
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if any(phrase in text for phrase in FORBIDDEN_POSITIVE_WORDING):
            return False
    return True

