"""Audit for v0.8.15 owner readiness recovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_readiness_recovery.io import load_json, write_json, write_text
from trading_core.equity_owner_readiness_recovery.recovery_config import (
    BOUNDARY,
    DEFAULT_AS_OF_DATE,
    FILES,
    FORBIDDEN_COMMAND_FRAGMENTS,
    FORBIDDEN_POSITIVE_WORDING,
    FORBIDDEN_TASK_CATEGORIES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    TARGET_VERSION,
    artifact_paths,
)
from trading_core.equity_owner_readiness_recovery.recovery_report import render_audit
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_readiness_recovery(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)

    availability = payloads.get("recovery_input_availability", {})
    gap = payloads.get("readiness_gap_summary", {})
    backlog = payloads.get("recovery_task_backlog", {})
    developer = payloads.get("developer_follow_up_recovery_plan", {})
    checklist = payloads.get("gate_reevaluation_readiness_checklist", {})
    blocked_state = payloads.get("blocked_state_preservation_check", {})
    boundary = payloads.get("recovery_boundary_check", {})

    audit = {
        "audit_id": "A-SHARE-OWNER-READINESS-RECOVERY-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("recovery_plan_config", {}).get("mode", "build_quality_improvement_plan"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "quality_exception_workflow_audit_passed": availability.get("quality_exception_workflow_audit_passed") is True,
            "source_gate_decision": availability.get("source_gate_decision"),
            "blocked_gate_decision_preserved": availability.get("blocked_gate_decision_preserved") is True,
        },
        "recovery_checks": {
            "minimum_owner_readiness_score": gap.get("minimum_owner_readiness_score"),
            "actual_owner_readiness_score": gap.get("actual_owner_readiness_score"),
            "actual_owner_readiness_grade": gap.get("actual_owner_readiness_grade"),
            "readiness_score_gap": gap.get("readiness_score_gap"),
            "recovery_tasks_generated": backlog.get("task_count", 0) > 0,
            "developer_follow_up_converted": developer.get("follow_up_count", 0) > 0,
            "tasks_marked_complete_by_default": backlog.get("tasks_marked_complete_by_default"),
            "recovery_plan_changes_gate_decision": blocked_state.get("recovery_plan_changes_gate_decision"),
            "threshold_lowered": blocked_state.get("threshold_lowered"),
            "auto_waiver_allowed": blocked_state.get("auto_waiver_allowed"),
            "manual_waiver_approval_recorded": blocked_state.get("manual_waiver_approval_recorded"),
            "execute_recovery_tasks": payloads.get("recovery_plan_config", {}).get("execute_recovery_tasks"),
            "ready_for_future_gate_reevaluation": checklist.get("ready_for_future_gate_reevaluation"),
            "no_forbidden_recovery_task_categories": not backlog.get("forbidden_recovery_task_categories_detected"),
            "no_forbidden_verification_commands": not payloads.get("recovery_verification_plan", {}).get("forbidden_verification_commands_detected"),
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json(artifacts["recovery_audit_json"], audit)
    write_text(artifacts["recovery_audit_report"], render_audit(audit))
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "recovery_checks": audit["recovery_checks"],
        "boundary": audit["boundary"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["recovery_audit_json"]),
        "report_path": str(artifacts["recovery_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    config = payloads.get("recovery_plan_config", {})
    availability = payloads.get("recovery_input_availability", {})
    resolution = payloads.get("recovery_source_resolution", {})
    alignment = payloads.get("recovery_date_alignment", {})
    gap = payloads.get("readiness_gap_summary", {})
    root_map = payloads.get("quality_exception_root_cause_map", {})
    target_policy = payloads.get("quality_improvement_target_policy", {})
    backlog = payloads.get("recovery_task_backlog", {})
    developer = payloads.get("developer_follow_up_recovery_plan", {})
    owner = payloads.get("owner_follow_up_recovery_plan", {})
    impact = payloads.get("recovery_score_impact_model", {})
    verification = payloads.get("recovery_verification_plan", {})
    checklist = payloads.get("gate_reevaluation_readiness_checklist", {})
    blocked_state = payloads.get("blocked_state_preservation_check", {})
    trace = payloads.get("recovery_source_trace", {})
    boundary = payloads.get("recovery_boundary_check", {})
    manifest = payloads.get("recovery_manifest", {})
    summary = payloads.get("recovery_summary", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "config_preserves_boundaries": _config_preserves_boundaries(config),
        "input_quality_exception_workflow_audit_passed": availability.get("quality_exception_workflow_audit_passed") is True,
        "input_availability_passed": availability.get("overall_passed") is True,
        "source_resolution_passed": resolution.get("overall_passed") is True,
        "date_alignment_passed": alignment.get("overall_passed") is True,
        "source_gate_decision_preserved": gap.get("source_gate_decision") == "blocked",
        "blocked_gate_decision_preserved": gap.get("blocked_state_preserved") is True and blocked_state.get("overall_passed") is True,
        "owner_operationally_acceptable_false": gap.get("owner_operationally_acceptable") is False,
        "readiness_score_gap_represented": gap.get("readiness_score_gap") == max(gap.get("minimum_owner_readiness_score", 0) - gap.get("actual_owner_readiness_score", 0), 0),
        "root_cause_map_generated": root_map.get("mapped_count", 0) > 0,
        "target_policy_does_not_lower_threshold": target_policy.get("target_owner_readiness_score", 0) >= gap.get("minimum_owner_readiness_score", 75),
        "recovery_tasks_generated": backlog.get("task_count", 0) > 0,
        "developer_follow_up_converted": developer.get("follow_up_count", 0) > 0,
        "owner_follow_up_plan_generated": owner.get("owner_follow_up_count", 0) > 0,
        "tasks_not_marked_complete_by_default": backlog.get("tasks_marked_complete_by_default") is False,
        "recovery_score_impact_does_not_rewrite_source": impact.get("does_not_rewrite_source_score") is True,
        "recovery_plan_does_not_change_gate_decision": blocked_state.get("recovery_plan_changes_gate_decision") is False,
        "threshold_not_lowered": blocked_state.get("threshold_lowered") is False,
        "auto_waiver_false": blocked_state.get("auto_waiver_allowed") is False,
        "manual_waiver_approval_false": blocked_state.get("manual_waiver_approval_recorded") is False,
        "execute_recovery_tasks_false": config.get("execute_recovery_tasks") is False,
        "ready_for_future_gate_reevaluation_false": checklist.get("ready_for_future_gate_reevaluation") is False,
        "no_forbidden_recovery_task_categories": _task_categories_clean(backlog),
        "no_forbidden_verification_commands": not verification.get("forbidden_verification_commands_detected"),
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and _boundary_fields_clean(boundary),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and _markdown_wording_clean(paths, as_of_date),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-READINESS-RECOVERY-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-READINESS-RECOVERY-SUMMARY",
    }


def _config_preserves_boundaries(config: dict[str, Any]) -> bool:
    expected_false = [
        "does_not_change_gate_decision",
        "does_not_lower_threshold",
        "does_not_auto_waive",
        "execute_recovery_tasks",
        "mark_tasks_complete_by_default",
        "rerun_build_from_existing_data",
        "rerun_owner_readiness_gate",
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
    true_fields = {"does_not_change_gate_decision", "does_not_lower_threshold", "does_not_auto_waive"}
    for key in expected_false:
        expected = True if key in true_fields else False
        if config.get(key) is not expected:
            return False
    return config.get("research_only") is True and config.get("virtual_only") is True


def _task_categories_clean(backlog: dict[str, Any]) -> bool:
    categories = {task.get("category") for task in backlog.get("tasks", [])}
    return not categories.intersection(FORBIDDEN_TASK_CATEGORIES) and not backlog.get("forbidden_recovery_task_categories_detected")


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


def _markdown_wording_clean(paths: ProjectPaths, as_of_date: str) -> bool:
    root = paths.outputs_dir / "equity_owner_readiness_recovery" / "daily" / as_of_date
    if not root.exists():
        return True
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if any(phrase in text for phrase in FORBIDDEN_POSITIVE_WORDING):
            return False
    return True


def verification_commands_clean(commands: list[str]) -> bool:
    return not forbidden_verification_commands(commands)


def forbidden_verification_commands(commands: list[str]) -> list[str]:
    hits = []
    for command in commands:
        lower = command.lower()
        for fragment in FORBIDDEN_COMMAND_FRAGMENTS:
            if fragment == "order":
                continue
            if fragment.lower() in lower:
                hits.append(command)
                break
    return hits
