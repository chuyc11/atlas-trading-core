"""Audit for v0.8.16 owner readiness recovery execution tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_readiness_recovery_execution.execution_config import BOUNDARY, DEFAULT_AS_OF_DATE, FILES, FORBIDDEN_POSITIVE_WORDING, RECOMMENDED_NEXT_VERSION, REPORTS, TARGET_VERSION, artifact_paths
from trading_core.equity_owner_readiness_recovery_execution.execution_report import render_audit
from trading_core.equity_owner_readiness_recovery_execution.io import load_json, write_json, write_text
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_readiness_recovery_execution(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)

    availability = payloads.get("recovery_execution_input_availability", {})
    status = payloads.get("recovery_task_status_tracker", {})
    evidence = payloads.get("recovery_task_evidence_registry", {})
    completion = payloads.get("recovery_task_completion_evaluation", {})
    score = payloads.get("score_impact_evidence_assessment", {})
    decision = payloads.get("gate_reevaluation_readiness_decision", {})
    threshold = payloads.get("threshold_preservation_check", {})
    waiver = payloads.get("waiver_preservation_check", {})
    audit_only = payloads.get("audit_only_verification_evidence", {})
    boundary = payloads.get("recovery_execution_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-READINESS-RECOVERY-EXECUTION-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("recovery_execution_config", {}).get("mode", "prepare_gate_reevaluation"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "recovery_audit_passed": availability.get("recovery_audit_passed") is True,
            "source_gate_decision": availability.get("source_gate_decision"),
            "blocked_gate_decision_preserved": availability.get("blocked_gate_decision_preserved") is True,
        },
        "execution_checks": {
            "task_completion_not_fabricated": completion.get("task_completion_not_fabricated") is True,
            "tasks_marked_complete_by_default": status.get("tasks_marked_complete_by_default"),
            "score_rewritten_without_audit_evidence": score.get("score_rewritten_without_audit_evidence"),
            "gate_reevaluation_executed": decision.get("gate_reevaluation_executed"),
            "ready_for_future_gate_reevaluation": decision.get("ready_for_future_gate_reevaluation"),
            "threshold_lowered": threshold.get("threshold_lowered"),
            "auto_waiver_allowed": waiver.get("auto_waiver_allowed"),
            "manual_waiver_approval_recorded": waiver.get("manual_waiver_approval_recorded"),
            "no_forbidden_evidence_types": not evidence.get("forbidden_evidence_types_detected"),
            "no_forbidden_verification_commands": not audit_only.get("forbidden_verification_commands_detected"),
            "task_count": status.get("task_count"),
            "evidence_available_count": status.get("evidence_available_count"),
            "verified_by_audit_only_count": status.get("verified_by_audit_only_count"),
            "completed_count": status.get("completed_count"),
            "gate_reevaluation_readiness_decision": decision.get("gate_reevaluation_readiness_decision"),
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json(artifacts["recovery_execution_audit_json"], audit)
    write_text(artifacts["recovery_execution_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "execution_checks": audit["execution_checks"],
        "boundary": audit["boundary"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["recovery_execution_audit_json"]),
        "report_path": str(artifacts["recovery_execution_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    config = payloads.get("recovery_execution_config", {})
    availability = payloads.get("recovery_execution_input_availability", {})
    resolution = payloads.get("recovery_execution_source_resolution", {})
    alignment = payloads.get("recovery_execution_date_alignment", {})
    evidence = payloads.get("recovery_task_evidence_registry", {})
    status = payloads.get("recovery_task_status_tracker", {})
    developer = payloads.get("developer_follow_up_evidence_tracker", {})
    owner = payloads.get("owner_follow_up_evidence_tracker", {})
    audit_only = payloads.get("audit_only_verification_evidence", {})
    completion = payloads.get("recovery_task_completion_evaluation", {})
    evidence_quality = payloads.get("recovery_evidence_quality_assessment", {})
    score = payloads.get("score_impact_evidence_assessment", {})
    improvement = payloads.get("readiness_improvement_evidence_summary", {})
    prereq = payloads.get("gate_reevaluation_prerequisite_checklist", {})
    decision = payloads.get("gate_reevaluation_readiness_decision", {})
    plan = payloads.get("controlled_reevaluation_plan", {})
    blocked = payloads.get("blocked_state_preservation_check", {})
    threshold = payloads.get("threshold_preservation_check", {})
    waiver = payloads.get("waiver_preservation_check", {})
    trace = payloads.get("recovery_execution_source_trace", {})
    boundary = payloads.get("recovery_execution_boundary_check", {})
    manifest = payloads.get("recovery_execution_manifest", {})
    summary = payloads.get("recovery_execution_summary", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "config_preserves_boundaries": _config_preserves_boundaries(config),
        "input_recovery_audit_passed": availability.get("recovery_audit_passed") is True,
        "input_availability_passed": availability.get("overall_passed") is True,
        "source_resolution_passed": resolution.get("overall_passed") is True,
        "date_alignment_passed": alignment.get("overall_passed") is True,
        "source_gate_decision_preserved": availability.get("source_gate_decision") == "blocked",
        "blocked_gate_decision_preserved": blocked.get("overall_passed") is True,
        "evidence_registry_generated": evidence.get("evidence_record_count", -1) >= 0,
        "evidence_records_cite_real_or_unavailable": _evidence_records_clean(evidence),
        "task_status_tracker_generated": status.get("task_count", 0) >= 0,
        "developer_evidence_tracker_generated": developer.get("tracker_id") == "A-SHARE-DEVELOPER-FOLLOW-UP-EVIDENCE-TRACKER",
        "owner_evidence_tracker_generated": owner.get("tracker_id") == "A-SHARE-OWNER-FOLLOW-UP-EVIDENCE-TRACKER",
        "audit_only_evidence_generated": audit_only.get("evidence_id") == "A-SHARE-AUDIT-ONLY-VERIFICATION-EVIDENCE",
        "task_completion_not_fabricated": completion.get("task_completion_not_fabricated") is True,
        "tasks_not_marked_complete_by_default": status.get("tasks_marked_complete_by_default") is False,
        "evidence_quality_generated": bool(evidence_quality.get("assessment_id")),
        "score_not_rewritten_without_audit_evidence": score.get("score_rewritten_without_audit_evidence") is False,
        "readiness_improvement_not_claimed": improvement.get("readiness_improvement_claimed") is False,
        "prerequisite_checklist_generated": prereq.get("checklist_id") == "A-SHARE-GATE-REEVALUATION-PREREQUISITE-CHECKLIST",
        "ready_for_future_gate_reevaluation_represented": decision.get("ready_for_future_gate_reevaluation") is False,
        "gate_reevaluation_not_executed": decision.get("gate_reevaluation_executed") is False and plan.get("gate_reevaluation_executed") is False,
        "controlled_plan_does_not_execute_reevaluation": plan.get("rerun_owner_readiness_gate") is False,
        "threshold_not_lowered": threshold.get("threshold_lowered") is False,
        "waiver_not_approved": waiver.get("auto_waiver_allowed") is False and waiver.get("manual_waiver_approval_recorded") is False,
        "no_forbidden_evidence_types": not evidence.get("forbidden_evidence_types_detected"),
        "no_forbidden_verification_commands": not audit_only.get("forbidden_verification_commands_detected"),
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and _boundary_fields_clean(boundary),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and _markdown_wording_clean(paths, as_of_date),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-READINESS-RECOVERY-EXECUTION-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-READINESS-RECOVERY-EXECUTION-SUMMARY",
    }


def _config_preserves_boundaries(config: dict[str, Any]) -> bool:
    false_fields = [
        "execute_recovery_tasks",
        "rerun_owner_readiness_gate",
        "rerun_build_from_existing_data",
        "rerun_daily_pack",
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


def _evidence_records_clean(evidence: dict[str, Any]) -> bool:
    for row in evidence.get("records", []):
        path = Path(row.get("evidence_artifact_path", ""))
        if row.get("evidence_available") and not path.exists():
            return False
        if row.get("evidence_available") is False and row.get("evidence_sha256"):
            return False
    return True


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
    root = paths.outputs_dir / "equity_owner_readiness_recovery_execution" / "daily" / as_of_date
    if not root.exists():
        return True
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if any(phrase in text for phrase in FORBIDDEN_POSITIVE_WORDING):
            return False
    return True
