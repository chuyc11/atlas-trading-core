"""Audit for evidence-backed reevaluation prep."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_evidence_backed_reevaluation_prep.io import load_json, write_json, write_text
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import BOUNDARY, DEFAULT_AS_OF_DATE, FILES, FORBIDDEN_POSITIVE_WORDING, RECOMMENDED_NEXT_VERSION, REPORTS, TARGET_VERSION, artifact_paths
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_report import render_audit
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_evidence_backed_reevaluation_prep(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)
    availability = payloads.get("evidence_backed_prep_input_availability", {})
    sufficiency = payloads.get("evidence_sufficiency_for_reevaluation_decision", {})
    package = payloads.get("reevaluation_input_package", {})
    score = payloads.get("score_impact_readiness_summary", {})
    eligibility = payloads.get("controlled_reevaluation_eligibility_decision", {})
    boundary = payloads.get("evidence_backed_prep_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-EVIDENCE-BACKED-REEVALUATION-PREP-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("evidence_backed_prep_config", {}).get("mode", "evaluate_evidence_sufficiency_for_reevaluation"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "recovery_evidence_audit_passed": availability.get("recovery_evidence_audit_passed") is True,
            "source_gate_decision": availability.get("source_gate_decision"),
            "source_gate_decision_preserved": availability.get("source_gate_decision_preserved"),
        },
        "prep_checks": {
            "evidence_sufficiency_decision_consistent": sufficiency.get("ready_for_controlled_gate_reevaluation") == (sufficiency.get("eligibility_decision") == "eligible"),
            "ready_for_controlled_gate_reevaluation": eligibility.get("ready_for_controlled_gate_reevaluation"),
            "eligibility_decision": eligibility.get("eligibility_decision"),
            "reevaluation_input_package_generated": package.get("reevaluation_input_package_generated") is True,
            "reevaluation_executed": False,
            "new_gate_score_generated": False,
            "new_gate_decision_generated": False,
            "threshold_lowered": False,
            "auto_waiver_allowed": False,
            "manual_waiver_approval_recorded": False,
            "score_impact_readiness_is_not_official_score": score.get("score_impact_readiness_is_not_official_score") is True,
            "eligibility_decision_consistent": eligibility.get("ready_for_controlled_gate_reevaluation") is False if sufficiency.get("remaining_blocker_count", 0) else True,
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
    write_json(artifacts["evidence_backed_prep_audit_json"], audit)
    write_text(artifacts["evidence_backed_prep_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "prep_checks": audit["prep_checks"],
        "boundary": audit["boundary"],
        "test_policy": audit["test_policy"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["evidence_backed_prep_audit_json"]),
        "report_path": str(artifacts["evidence_backed_prep_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    config = payloads.get("evidence_backed_prep_config", {})
    availability = payloads.get("evidence_backed_prep_input_availability", {})
    resolution = payloads.get("evidence_backed_prep_source_resolution", {})
    alignment = payloads.get("evidence_backed_prep_date_alignment", {})
    sufficiency = payloads.get("evidence_sufficiency_for_reevaluation_decision", {})
    mapping = payloads.get("evidence_to_gate_mapping", {})
    package = payloads.get("reevaluation_input_package", {})
    score = payloads.get("score_impact_readiness_summary", {})
    threshold = payloads.get("gate_threshold_preservation_package", {})
    waiver = payloads.get("waiver_exclusion_package", {})
    preservation = payloads.get("boundary_preservation_package", {})
    checklist = payloads.get("evidence_backed_readiness_checklist", {})
    gap = payloads.get("remaining_evidence_gap_decision", {})
    eligibility = payloads.get("controlled_reevaluation_eligibility_decision", {})
    plan = payloads.get("next_gate_reevaluation_execution_plan", {})
    trace = payloads.get("evidence_backed_prep_source_trace", {})
    boundary = payloads.get("evidence_backed_prep_boundary_check", {})
    manifest = payloads.get("evidence_backed_prep_manifest", {})
    summary = payloads.get("evidence_backed_prep_summary", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "config_preserves_boundaries": _config_preserves_boundaries(config),
        "input_availability_passed": availability.get("overall_passed") is True,
        "source_resolution_passed": resolution.get("overall_passed") is True,
        "date_alignment_passed": alignment.get("overall_passed") is True,
        "recovery_evidence_audit_passed": availability.get("recovery_evidence_audit_passed") is True,
        "source_gate_decision_preserved": availability.get("source_gate_decision") == "blocked" and availability.get("source_gate_decision_preserved") is True,
        "evidence_sufficiency_decision_generated": sufficiency.get("decision_id") == "A-SHARE-EVIDENCE-SUFFICIENCY-FOR-REEVALUATION-DECISION",
        "evidence_quality_none_or_weak_not_eligible": not (sufficiency.get("overall_evidence_quality") in {"none", "weak"} and sufficiency.get("ready_for_controlled_gate_reevaluation") is True),
        "remaining_blockers_prevent_eligibility": not (sufficiency.get("remaining_blocker_count", 0) and eligibility.get("ready_for_controlled_gate_reevaluation") is True),
        "evidence_to_gate_mapping_generated": mapping.get("mapping_id") == "A-SHARE-EVIDENCE-TO-GATE-MAPPING",
        "reevaluation_input_package_generated": package.get("reevaluation_input_package_generated") is True and package.get("reevaluation_executed") is False,
        "score_impact_readiness_not_official_score": score.get("score_impact_readiness_is_not_official_score") is True and score.get("new_gate_score_generated") is False,
        "threshold_preserved": threshold.get("threshold_preserved") is True and threshold.get("threshold_lowered") is False,
        "waiver_excluded": waiver.get("auto_waiver_allowed") is False and waiver.get("manual_waiver_approval_recorded") is False,
        "boundary_preserved": all(preservation.get(key) is expected for key, expected in BOUNDARY.items()),
        "readiness_checklist_generated": checklist.get("checklist_id") == "A-SHARE-EVIDENCE-BACKED-READINESS-CHECKLIST",
        "remaining_gap_decision_generated": gap.get("decision_id") == "A-SHARE-REMAINING-EVIDENCE-GAP-DECISION",
        "eligibility_decision_consistent": eligibility.get("ready_for_controlled_gate_reevaluation") == (eligibility.get("eligibility_decision") == "eligible"),
        "next_execution_plan_generated": plan.get("plan_id") == "A-SHARE-NEXT-GATE-REEVALUATION-EXECUTION-PLAN" and plan.get("reevaluation_executed") is False,
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and all(boundary.get(key) is expected for key, expected in BOUNDARY.items()),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and _markdown_wording_clean(paths, as_of_date),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-EVIDENCE-BACKED-PREP-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-EVIDENCE-BACKED-PREP-SUMMARY",
        "new_gate_score_not_generated": summary.get("new_gate_score_generated") is False and sufficiency.get("new_gate_score_generated") is False,
        "new_gate_decision_not_generated": summary.get("new_gate_decision_generated") is False and sufficiency.get("new_gate_decision_generated") is False,
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
    root = paths.outputs_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / as_of_date
    if not root.exists():
        return True
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if any(phrase in text for phrase in FORBIDDEN_POSITIVE_WORDING):
            return False
    return True

