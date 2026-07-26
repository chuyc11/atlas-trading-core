"""Builder for v0.8.15 owner readiness recovery."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.blocked_state import build_blocked_state_preservation_check
from trading_core.equity_owner_readiness_recovery.date_alignment import build_date_alignment
from trading_core.equity_owner_readiness_recovery.follow_up_plans import build_developer_follow_up_recovery_plan, build_owner_follow_up_recovery_plan
from trading_core.equity_owner_readiness_recovery.improvement_loop import build_quality_improvement_loop_definition
from trading_core.equity_owner_readiness_recovery.improvement_targets import build_quality_improvement_target_policy
from trading_core.equity_owner_readiness_recovery.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_readiness_recovery.io import load_json, write_json
from trading_core.equity_owner_readiness_recovery.milestone_plan import build_recovery_milestone_plan
from trading_core.equity_owner_readiness_recovery.non_actionable_items import build_non_actionable_recovery_items
from trading_core.equity_owner_readiness_recovery.readiness_gap import build_readiness_gap_summary
from trading_core.equity_owner_readiness_recovery.recovery_audit import audit_a_share_owner_readiness_recovery
from trading_core.equity_owner_readiness_recovery.recovery_boundary import build_boundary_check
from trading_core.equity_owner_readiness_recovery.recovery_config import (
    ALLOWED_MODES,
    ANALYZE_GAP,
    AUDIT_EXISTING,
    BUILD_IMPROVEMENT,
    DEFAULT_AS_OF_DATE,
    FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    VALIDATE_INPUTS,
    RecoveryPlanConfig,
    artifact_paths,
    data_dir,
    output_dir,
    validate_config,
)
from trading_core.equity_owner_readiness_recovery.recovery_manifest import build_recovery_manifest, build_recovery_summary
from trading_core.equity_owner_readiness_recovery.recovery_report import write_reports
from trading_core.equity_owner_readiness_recovery.recovery_source_trace import build_recovery_source_trace
from trading_core.equity_owner_readiness_recovery.reevaluation_checklist import build_gate_reevaluation_readiness_checklist
from trading_core.equity_owner_readiness_recovery.risk_register import build_recovery_risk_register
from trading_core.equity_owner_readiness_recovery.root_cause_map import build_quality_exception_root_cause_map
from trading_core.equity_owner_readiness_recovery.score_driver_analysis import build_score_driver_analysis
from trading_core.equity_owner_readiness_recovery.score_impact_model import build_recovery_score_impact_model
from trading_core.equity_owner_readiness_recovery.source_resolution import build_source_resolution
from trading_core.equity_owner_readiness_recovery.task_backlog import build_recovery_task_backlog
from trading_core.equity_owner_readiness_recovery.verification_plan import build_recovery_verification_plan
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_readiness_recovery_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    sources = input_paths(default_paths(paths), as_of_date)
    payloads = {key: load_json(path) for key, path in sources.items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=payloads)
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-READINESS-RECOVERY-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "quality_exception_workflow_audit_passed": availability["quality_exception_workflow_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "blocked_gate_decision_preserved": availability["blocked_gate_decision_preserved"],
        "owner_operationally_acceptable": availability["owner_operationally_acceptable"],
        "auto_waiver_allowed": availability["auto_waiver_allowed"],
        "waiver_changes_gate_decision": availability["waiver_changes_gate_decision"],
    }


def build_a_share_owner_readiness_recovery(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_IMPROVEMENT,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        return audit_a_share_owner_readiness_recovery(as_of_date=as_of_date, paths=paths)
    config = RecoveryPlanConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
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
    intake = source_payloads["blocked_gate_intake"]
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    payloads: dict[str, Any] = {
        "recovery_plan_config": config.to_dict(
            source_gate_decision=intake.get("source_gate_decision", "blocked"),
            minimum_score=intake.get("minimum_owner_readiness_score", 0),
            actual_score=intake.get("actual_owner_readiness_score", 0),
            score_gap=intake.get("readiness_score_gap", 0),
        ),
        "recovery_input_availability": availability,
        "recovery_source_resolution": resolution,
        "recovery_date_alignment": alignment,
    }
    _write_payloads(artifacts, payloads)
    if mode == VALIDATE_INPUTS:
        return _validation_result(availability, resolution, alignment)

    registry = source_payloads["quality_exception_registry"]
    classification = source_payloads["quality_exception_classification"]
    developer_tracker = source_payloads["developer_follow_up_tracker"]
    owner_checklist = source_payloads["owner_follow_up_checklist"]
    gap = build_readiness_gap_summary(as_of_date=as_of_date, intake=intake, registry=registry, developer_tracker=developer_tracker)
    score_driver = build_score_driver_analysis(
        as_of_date=as_of_date,
        gap=gap,
        source_gap_analysis=source_payloads["owner_readiness_gap_analysis"],
        classification=classification,
    )
    root_map = build_quality_exception_root_cause_map(as_of_date=as_of_date, classification=classification, developer_tracker=developer_tracker)
    payloads.update(
        {
            "readiness_gap_summary": gap,
            "score_driver_analysis": score_driver,
            "quality_exception_root_cause_map": root_map,
        }
    )
    _write_payloads(artifacts, payloads)
    if mode == ANALYZE_GAP:
        return _gap_result(gap, root_map, artifacts)

    target_policy = build_quality_improvement_target_policy(as_of_date=as_of_date, minimum_score=gap["minimum_owner_readiness_score"])
    backlog = build_recovery_task_backlog(as_of_date=as_of_date, root_map=root_map, score_gap=gap["readiness_score_gap"])
    developer_plan = build_developer_follow_up_recovery_plan(as_of_date=as_of_date, developer_tracker=developer_tracker)
    owner_plan = build_owner_follow_up_recovery_plan(as_of_date=as_of_date, owner_checklist=owner_checklist)
    non_actionable = build_non_actionable_recovery_items(as_of_date=as_of_date, root_map=root_map)
    impact_model = build_recovery_score_impact_model(as_of_date=as_of_date, gap=gap, backlog=backlog)
    milestone = build_recovery_milestone_plan(as_of_date=as_of_date)
    improvement_loop = build_quality_improvement_loop_definition(as_of_date=as_of_date)
    verification = build_recovery_verification_plan(as_of_date=as_of_date, backlog=backlog)
    checklist = build_gate_reevaluation_readiness_checklist(as_of_date=as_of_date)
    blocked_state = build_blocked_state_preservation_check(as_of_date=as_of_date, intake=intake)
    risk = build_recovery_risk_register(as_of_date=as_of_date)
    boundary = build_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        source_gate_decision=gap["source_gate_decision"],
        blocking_reasons=availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"],
    )
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    payloads.update(
        {
            "quality_improvement_target_policy": target_policy,
            "recovery_task_backlog": backlog,
            "developer_follow_up_recovery_plan": developer_plan,
            "owner_follow_up_recovery_plan": owner_plan,
            "non_actionable_recovery_items": non_actionable,
            "recovery_score_impact_model": impact_model,
            "recovery_milestone_plan": milestone,
            "quality_improvement_loop_definition": improvement_loop,
            "recovery_verification_plan": verification,
            "gate_reevaluation_readiness_checklist": checklist,
            "blocked_state_preservation_check": blocked_state,
            "recovery_risk_register": risk,
            "recovery_boundary_check": boundary,
        }
    )
    _write_payloads(artifacts, payloads)
    trace = build_recovery_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    manifest = build_recovery_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        gap=gap,
        backlog=backlog,
        developer_plan=developer_plan,
        owner_plan=owner_plan,
        checklist=checklist,
        blocked_state=blocked_state,
        boundary=boundary,
    )
    summary = build_recovery_summary(as_of_date=as_of_date, gap=gap, backlog=backlog, developer_plan=developer_plan, owner_plan=owner_plan, checklist=checklist)
    payloads.update({"recovery_source_trace": trace, "recovery_manifest": manifest, "recovery_summary": summary})
    _write_payloads(artifacts, payloads)
    write_reports(output_dir(paths, as_of_date), payloads)
    trace = build_recovery_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    payloads["recovery_source_trace"] = trace
    _write_payloads(artifacts, {"recovery_source_trace": trace})

    return {
        "builder_id": "A-SHARE-OWNER-READINESS-RECOVERY-BUILDER",
        "overall_passed": availability["overall_passed"] and resolution["overall_passed"] and alignment["overall_passed"] and boundary["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + boundary["blocking_reasons"],
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]) + len(boundary["warnings"]),
        "source_gate_decision": gap["source_gate_decision"],
        "blocked_gate_decision_preserved": gap["blocked_state_preserved"],
        "minimum_owner_readiness_score": gap["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": gap["actual_owner_readiness_score"],
        "actual_owner_readiness_grade": gap["actual_owner_readiness_grade"],
        "readiness_score_gap": gap["readiness_score_gap"],
        "recovery_task_count": backlog["task_count"],
        "developer_follow_up_task_count": developer_plan["follow_up_count"],
        "owner_follow_up_task_count": owner_plan["owner_follow_up_count"],
        "ready_for_future_gate_reevaluation": checklist["ready_for_future_gate_reevaluation"],
        "recovery_plan_changes_gate_decision": blocked_state["recovery_plan_changes_gate_decision"],
        "threshold_lowered": blocked_state["threshold_lowered"],
        "auto_waiver_allowed": blocked_state["auto_waiver_allowed"],
        "manual_waiver_approval_recorded": blocked_state["manual_waiver_approval_recorded"],
        "execute_recovery_tasks": payloads["recovery_plan_config"]["execute_recovery_tasks"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "owner_readiness_recovery_plan_report": str(artifacts["owner_readiness_recovery_plan_report"]),
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)


def _validation_result(availability: dict[str, Any], resolution: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-READINESS-RECOVERY-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "quality_exception_workflow_audit_passed": availability["quality_exception_workflow_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "blocked_gate_decision_preserved": availability["blocked_gate_decision_preserved"],
        "owner_operationally_acceptable": availability["owner_operationally_acceptable"],
        "auto_waiver_allowed": availability["auto_waiver_allowed"],
        "waiver_changes_gate_decision": availability["waiver_changes_gate_decision"],
    }


def _gap_result(gap: dict[str, Any], root_map: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-OWNER-READINESS-GAP-ANALYZER",
        "overall_passed": gap["source_gate_decision"] == "blocked" and root_map["mapped_count"] > 0,
        "blocking_reasons": [] if root_map["mapped_count"] > 0 else ["root_cause_map_empty"],
        "warnings": 0,
        "source_gate_decision": gap["source_gate_decision"],
        "minimum_owner_readiness_score": gap["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": gap["actual_owner_readiness_score"],
        "readiness_score_gap": gap["readiness_score_gap"],
        "mapped_count": root_map["mapped_count"],
        "readiness_gap_summary": str(artifacts["readiness_gap_summary"]),
    }
