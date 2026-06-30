"""Audit for controlled owner-readiness gate reevaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import BOUNDARY, DEFAULT_AS_OF_DATE, FILES, FORBIDDEN_POSITIVE_WORDING, RECOMMENDED_NEXT_VERSION, REPORTS, TARGET_VERSION, artifact_paths
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_report import render_audit
from trading_core.equity_owner_controlled_gate_reevaluation.io import load_json, write_json, write_text
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_controlled_gate_reevaluation(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)

    availability = payloads.get("controlled_reevaluation_input_availability", {})
    guard = payloads.get("reevaluation_readiness_guard", {})
    skip = payloads.get("reevaluation_skip_decision", {})
    decision = payloads.get("controlled_reevaluation_decision", {})
    evidence = payloads.get("evidence_sufficiency_check", {})
    source_gate = payloads.get("source_gate_preservation_check", {})
    threshold = payloads.get("threshold_preservation_check", {})
    waiver = payloads.get("waiver_preservation_check", {})
    boundary = payloads.get("controlled_reevaluation_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("controlled_reevaluation_config", {}).get("mode", "record_reevaluation_skip_decision"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "recovery_execution_audit_passed": availability.get("recovery_execution_audit_passed") is True,
            "owner_readiness_gate_audit_passed": availability.get("owner_readiness_gate_audit_passed") is True,
            "source_gate_decision": availability.get("source_gate_decision"),
            "blocked_gate_decision_preserved": availability.get("blocked_gate_decision_preserved") is True,
        },
        "reevaluation_checks": {
            "readiness_guard_passed": guard.get("readiness_guard_passed"),
            "reevaluation_allowed": guard.get("reevaluation_allowed"),
            "reevaluation_skipped": skip.get("reevaluation_skipped"),
            "reevaluation_skip_reason": skip.get("reevaluation_skip_reason"),
            "controlled_reevaluation_decision": decision.get("decision"),
            "source_gate_decision_preserved": source_gate.get("source_gate_decision_preserved"),
            "evidence_sufficient_for_gate_reevaluation": evidence.get("evidence_sufficient_for_gate_reevaluation"),
            "gate_reevaluation_executed": decision.get("gate_reevaluation_executed"),
            "new_gate_score_generated": decision.get("new_gate_score_generated"),
            "new_gate_decision_generated": decision.get("new_gate_decision_generated"),
            "threshold_lowered": threshold.get("threshold_lowered"),
            "auto_waiver_allowed": waiver.get("auto_waiver_allowed"),
            "manual_waiver_approval_recorded": waiver.get("manual_waiver_approval_recorded"),
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json(artifacts["controlled_reevaluation_audit_json"], audit)
    write_text(artifacts["controlled_reevaluation_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "reevaluation_checks": audit["reevaluation_checks"],
        "boundary": audit["boundary"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["controlled_reevaluation_audit_json"]),
        "report_path": str(artifacts["controlled_reevaluation_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    config = payloads.get("controlled_reevaluation_config", {})
    availability = payloads.get("controlled_reevaluation_input_availability", {})
    resolution = payloads.get("controlled_reevaluation_source_resolution", {})
    alignment = payloads.get("controlled_reevaluation_date_alignment", {})
    guard = payloads.get("reevaluation_readiness_guard", {})
    prerequisite = payloads.get("reevaluation_prerequisite_validation", {})
    plan = payloads.get("reevaluation_execution_plan", {})
    skip = payloads.get("reevaluation_skip_decision", {})
    not_ready = payloads.get("not_ready_reason_summary", {})
    source_gate = payloads.get("source_gate_preservation_check", {})
    threshold = payloads.get("threshold_preservation_check", {})
    waiver = payloads.get("waiver_preservation_check", {})
    evidence = payloads.get("evidence_sufficiency_check", {})
    decision = payloads.get("controlled_reevaluation_decision", {})
    trace = payloads.get("controlled_reevaluation_source_trace", {})
    boundary = payloads.get("controlled_reevaluation_boundary_check", {})
    manifest = payloads.get("controlled_reevaluation_manifest", {})
    summary = payloads.get("controlled_reevaluation_summary", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "config_preserves_boundaries": _config_preserves_boundaries(config),
        "input_availability_passed": availability.get("overall_passed") is True,
        "source_resolution_passed": resolution.get("overall_passed") is True,
        "date_alignment_passed": alignment.get("overall_passed") is True,
        "source_gate_decision_blocked": availability.get("source_gate_decision") == "blocked",
        "source_gate_decision_preserved": source_gate.get("overall_passed") is True,
        "readiness_guard_blocks_reevaluation": guard.get("readiness_guard_passed") is False and guard.get("reevaluation_allowed") is False,
        "not_ready_reasons_recorded": bool(guard.get("block_reasons")) and not_ready.get("not_ready") is True,
        "prerequisites_not_met": prerequisite.get("reevaluation_prerequisites_met") is False,
        "execution_plan_not_executed": plan.get("execution_status") == "not_executed" and plan.get("gate_reevaluation_executed") is False,
        "skip_decision_recorded": skip.get("reevaluation_skipped") is True and skip.get("reevaluation_skip_reason") == "not_ready",
        "controlled_decision_skipped_not_ready": decision.get("decision") == "skipped_not_ready",
        "evidence_insufficient_represented": evidence.get("evidence_sufficient_for_gate_reevaluation") is False,
        "threshold_not_lowered": threshold.get("threshold_lowered") is False,
        "waiver_not_approved": waiver.get("auto_waiver_allowed") is False and waiver.get("manual_waiver_approval_recorded") is False,
        "no_new_gate_score_or_decision": decision.get("new_gate_score_generated") is False and decision.get("new_gate_decision_generated") is False,
        "gate_reevaluation_not_executed": decision.get("gate_reevaluation_executed") is False and summary.get("gate_reevaluation_executed") is False,
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and _boundary_fields_clean(boundary),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and _markdown_wording_clean(paths, as_of_date),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-SUMMARY",
    }


def _config_preserves_boundaries(config: dict[str, Any]) -> bool:
    false_fields = [
        "rerun_owner_readiness_gate",
        "rerun_build_from_existing_data",
        "rerun_daily_pack",
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
    root = paths.outputs_dir / "equity_owner_controlled_gate_reevaluation" / "daily" / as_of_date
    if not root.exists():
        return True
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if any(phrase in text for phrase in FORBIDDEN_POSITIVE_WORDING):
            return False
    return True

