"""Builder for v0.8.16 owner readiness recovery execution tracking."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.audit_only_evidence import build_audit_only_verification_evidence
from trading_core.equity_owner_readiness_recovery_execution.date_alignment import build_date_alignment
from trading_core.equity_owner_readiness_recovery_execution.evidence_quality import build_recovery_evidence_quality_assessment
from trading_core.equity_owner_readiness_recovery_execution.evidence_registry import build_recovery_task_evidence_registry
from trading_core.equity_owner_readiness_recovery_execution.execution_boundary import build_boundary_check
from trading_core.equity_owner_readiness_recovery_execution.execution_config import ALLOWED_MODES, AUDIT_EXISTING, COLLECT_EVIDENCE, DEFAULT_AS_OF_DATE, EVALUATE_STATUS, FILES, PREPARE_REEVALUATION, RECOMMENDED_NEXT_VERSION, REPORTS, VALIDATE_INPUTS, RecoveryExecutionConfig, artifact_paths, data_dir, output_dir, validate_config
from trading_core.equity_owner_readiness_recovery_execution.execution_manifest import build_execution_manifest, build_execution_summary
from trading_core.equity_owner_readiness_recovery_execution.execution_report import write_reports
from trading_core.equity_owner_readiness_recovery_execution.execution_source_trace import build_execution_source_trace
from trading_core.equity_owner_readiness_recovery_execution.follow_up_evidence import build_developer_follow_up_evidence_tracker, build_owner_follow_up_evidence_tracker
from trading_core.equity_owner_readiness_recovery_execution.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_readiness_recovery_execution.io import load_json, write_json
from trading_core.equity_owner_readiness_recovery_execution.preservation_checks import build_blocked_state_preservation_check, build_threshold_preservation_check, build_waiver_preservation_check
from trading_core.equity_owner_readiness_recovery_execution.recovery_execution_audit import audit_a_share_owner_readiness_recovery_execution
from trading_core.equity_owner_readiness_recovery_execution.reevaluation_prep import build_controlled_reevaluation_plan, build_gate_reevaluation_prerequisite_checklist, build_gate_reevaluation_readiness_decision
from trading_core.equity_owner_readiness_recovery_execution.score_impact_evidence import build_readiness_improvement_evidence_summary, build_score_impact_evidence_assessment
from trading_core.equity_owner_readiness_recovery_execution.source_resolution import build_source_resolution
from trading_core.equity_owner_readiness_recovery_execution.task_completion import build_recovery_task_completion_evaluation
from trading_core.equity_owner_readiness_recovery_execution.task_status_tracker import build_recovery_task_status_tracker
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_readiness_recovery_execution_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    payloads = {key: load_json(path) for key, path in input_paths(paths, as_of_date).items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=payloads)
    return _validation_result(availability, resolution, alignment)


def build_a_share_owner_readiness_recovery_execution(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = PREPARE_REEVALUATION,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        return audit_a_share_owner_readiness_recovery_execution(as_of_date=as_of_date, paths=paths)
    config = RecoveryExecutionConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
    issues = validate_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of {ALLOWED_MODES}")

    artifacts = artifact_paths(paths, as_of_date)
    data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    output_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    sources = input_paths(paths, as_of_date)
    source_payloads = {key: load_json(path) for key, path in sources.items()}
    source_summary = source_payloads["recovery_summary"]
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    payloads: dict[str, Any] = {
        "recovery_execution_config": config.to_dict(
            source_gate_decision=source_summary.get("source_gate_decision", "blocked"),
            minimum_score=source_summary.get("minimum_owner_readiness_score", 0),
            actual_score=source_summary.get("actual_owner_readiness_score", 0),
        ),
        "recovery_execution_input_availability": availability,
        "recovery_execution_source_resolution": resolution,
        "recovery_execution_date_alignment": alignment,
    }
    _write_payloads(artifacts, payloads)
    if mode == VALIDATE_INPUTS:
        return _validation_result(availability, resolution, alignment)

    backlog = source_payloads["recovery_task_backlog"]
    evidence_registry = build_recovery_task_evidence_registry(paths=paths, as_of_date=as_of_date, backlog=backlog)
    status_tracker = build_recovery_task_status_tracker(as_of_date=as_of_date, backlog=backlog, evidence_registry=evidence_registry, source_gate_decision=source_summary.get("source_gate_decision", "blocked"))
    developer = build_developer_follow_up_evidence_tracker(as_of_date=as_of_date, developer_plan=source_payloads["developer_follow_up_recovery_plan"], evidence_registry=evidence_registry)
    owner = build_owner_follow_up_evidence_tracker(as_of_date=as_of_date, owner_plan=source_payloads["owner_follow_up_recovery_plan"])
    audit_only = build_audit_only_verification_evidence(as_of_date=as_of_date, verification_plan=source_payloads["recovery_verification_plan"])
    payloads.update(
        {
            "recovery_task_evidence_registry": evidence_registry,
            "recovery_task_status_tracker": status_tracker,
            "developer_follow_up_evidence_tracker": developer,
            "owner_follow_up_evidence_tracker": owner,
            "audit_only_verification_evidence": audit_only,
        }
    )
    _write_payloads(artifacts, payloads)
    if mode == COLLECT_EVIDENCE:
        return _evidence_result(evidence_registry, status_tracker, artifacts)

    completion = build_recovery_task_completion_evaluation(as_of_date=as_of_date, status_tracker=status_tracker, evidence_registry=evidence_registry)
    evidence_quality = build_recovery_evidence_quality_assessment(as_of_date=as_of_date, evidence_registry=evidence_registry)
    score = build_score_impact_evidence_assessment(as_of_date=as_of_date, source_summary=source_summary, status_tracker=status_tracker)
    improvement = build_readiness_improvement_evidence_summary(as_of_date=as_of_date, score_assessment=score, evidence_quality=evidence_quality)
    payloads.update(
        {
            "recovery_task_completion_evaluation": completion,
            "recovery_evidence_quality_assessment": evidence_quality,
            "score_impact_evidence_assessment": score,
            "readiness_improvement_evidence_summary": improvement,
        }
    )
    _write_payloads(artifacts, payloads)
    if mode == EVALUATE_STATUS:
        return _status_result(status_tracker, completion, artifacts)

    prereq = build_gate_reevaluation_prerequisite_checklist(as_of_date=as_of_date, status_tracker=status_tracker, evidence_quality=evidence_quality, audit_only=audit_only)
    decision = build_gate_reevaluation_readiness_decision(as_of_date=as_of_date, prerequisite_checklist=prereq)
    plan = build_controlled_reevaluation_plan(as_of_date=as_of_date, readiness_decision=decision)
    blocked = build_blocked_state_preservation_check(as_of_date=as_of_date, source_summary=source_summary)
    threshold = build_threshold_preservation_check(as_of_date=as_of_date, source_summary=source_summary)
    waiver = build_waiver_preservation_check(as_of_date=as_of_date)
    boundary = build_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        source_gate_decision=source_summary.get("source_gate_decision", "blocked"),
        blocking_reasons=availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"],
    )
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    payloads.update(
        {
            "gate_reevaluation_prerequisite_checklist": prereq,
            "gate_reevaluation_readiness_decision": decision,
            "controlled_reevaluation_plan": plan,
            "blocked_state_preservation_check": blocked,
            "threshold_preservation_check": threshold,
            "waiver_preservation_check": waiver,
            "recovery_execution_boundary_check": boundary,
        }
    )
    _write_payloads(artifacts, payloads)
    trace = build_execution_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    manifest = build_execution_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        source_summary=source_summary,
        status_tracker=status_tracker,
        evidence_registry=evidence_registry,
        readiness_decision=decision,
        boundary=boundary,
    )
    summary = build_execution_summary(as_of_date=as_of_date, source_summary=source_summary, status_tracker=status_tracker, evidence_registry=evidence_registry, readiness_decision=decision)
    payloads.update({"recovery_execution_source_trace": trace, "recovery_execution_manifest": manifest, "recovery_execution_summary": summary})
    _write_payloads(artifacts, payloads)
    write_reports(output_dir(paths, as_of_date), payloads)
    trace = build_execution_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    payloads["recovery_execution_source_trace"] = trace
    _write_payloads(artifacts, {"recovery_execution_source_trace": trace})

    return {
        "builder_id": "A-SHARE-OWNER-READINESS-RECOVERY-EXECUTION-BUILDER",
        "overall_passed": availability["overall_passed"] and resolution["overall_passed"] and alignment["overall_passed"] and boundary["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + boundary["blocking_reasons"],
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]) + len(boundary["warnings"]),
        "source_gate_decision": source_summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": source_summary.get("blocked_gate_decision_preserved"),
        "task_count": status_tracker["task_count"],
        "evidence_available_count": status_tracker["evidence_available_count"],
        "verified_by_audit_only_count": status_tracker["verified_by_audit_only_count"],
        "completed_count": status_tracker["completed_count"],
        "tasks_marked_complete_by_default": status_tracker["tasks_marked_complete_by_default"],
        "ready_for_future_gate_reevaluation": decision["ready_for_future_gate_reevaluation"],
        "gate_reevaluation_readiness_decision": decision["gate_reevaluation_readiness_decision"],
        "gate_reevaluation_executed": decision["gate_reevaluation_executed"],
        "threshold_lowered": threshold["threshold_lowered"],
        "auto_waiver_allowed": waiver["auto_waiver_allowed"],
        "manual_waiver_approval_recorded": waiver["manual_waiver_approval_recorded"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "recovery_execution_tracker_report": str(artifacts["recovery_execution_tracker_report"]),
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)


def _validation_result(availability: dict[str, Any], resolution: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-READINESS-RECOVERY-EXECUTION-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "recovery_audit_passed": availability["recovery_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "blocked_gate_decision_preserved": availability["blocked_gate_decision_preserved"],
        "recovery_plan_changes_gate_decision": availability["recovery_plan_changes_gate_decision"],
        "threshold_lowered": availability["threshold_lowered"],
        "auto_waiver_allowed": availability["auto_waiver_allowed"],
    }


def _evidence_result(evidence_registry: dict[str, Any], status_tracker: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-RECOVERY-EVIDENCE-COLLECTOR",
        "overall_passed": not evidence_registry["forbidden_evidence_types_detected"],
        "blocking_reasons": [] if not evidence_registry["forbidden_evidence_types_detected"] else ["forbidden_evidence_types_detected"],
        "warnings": 0,
        "task_count": status_tracker["task_count"],
        "evidence_available_count": evidence_registry["evidence_available_count"],
        "recovery_task_evidence_registry": str(artifacts["recovery_task_evidence_registry"]),
    }


def _status_result(status_tracker: dict[str, Any], completion: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-RECOVERY-TASK-STATUS-EVALUATOR",
        "overall_passed": completion["task_completion_not_fabricated"],
        "blocking_reasons": [] if completion["task_completion_not_fabricated"] else ["task_completion_fabricated"],
        "warnings": 0,
        "task_count": status_tracker["task_count"],
        "completed_count": status_tracker["completed_count"],
        "tasks_marked_complete_by_default": status_tracker["tasks_marked_complete_by_default"],
        "recovery_task_status_tracker": str(artifacts["recovery_task_status_tracker"]),
    }
