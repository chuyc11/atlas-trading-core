"""Builder for v0.8.14 owner quality exception workflow."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.blocked_gate_intake import build_blocked_gate_intake
from trading_core.equity_owner_quality_exceptions.date_alignment import build_date_alignment
from trading_core.equity_owner_quality_exceptions.developer_follow_up import build_developer_follow_up_tracker
from trading_core.equity_owner_quality_exceptions.escalation_workflow import (
    build_escalation_workflow,
    build_exception_routing_matrix,
    build_exception_severity_matrix,
    build_exception_sla_policy,
)
from trading_core.equity_owner_quality_exceptions.exception_audit_trail import build_exception_audit_trail
from trading_core.equity_owner_quality_exceptions.exception_boundary import build_boundary_check
from trading_core.equity_owner_quality_exceptions.exception_classification import classify_quality_exceptions
from trading_core.equity_owner_quality_exceptions.exception_manifest import build_manifest, build_summary
from trading_core.equity_owner_quality_exceptions.exception_registry import build_quality_exception_registry
from trading_core.equity_owner_quality_exceptions.exception_report import write_reports
from trading_core.equity_owner_quality_exceptions.exception_source_trace import build_source_trace
from trading_core.equity_owner_quality_exceptions.exception_workflow_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    BUILD_ESCALATION,
    CLASSIFY_EXCEPTIONS,
    DEFAULT_AS_OF_DATE,
    FILES,
    INTAKE_GATE,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    VALIDATE_INPUTS,
    QualityExceptionWorkflowConfig,
    artifact_paths,
    data_dir,
    output_dir,
    validate_config,
)
from trading_core.equity_owner_quality_exceptions.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_quality_exceptions.io import load_json, write_json
from trading_core.equity_owner_quality_exceptions.manual_waiver_policy import (
    build_manual_waiver_decision_record,
    build_manual_waiver_policy,
    build_manual_waiver_request_template,
)
from trading_core.equity_owner_quality_exceptions.owner_follow_up import build_owner_follow_up_checklist
from trading_core.equity_owner_quality_exceptions.owner_notice import build_blocked_daily_pack_owner_notice
from trading_core.equity_owner_quality_exceptions.readiness_gap_analysis import build_owner_readiness_gap_analysis
from trading_core.equity_owner_quality_exceptions.source_resolution import build_source_resolution
from trading_core.equity_owner_quality_exceptions.threshold_failure_explanation import build_threshold_failure_explanation
from trading_core.equity_owner_quality_exceptions.waiver_candidate_evaluation import build_waiver_candidate_evaluation
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_quality_exception_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-OWNER-QUALITY-EXCEPTION-INPUT-VALIDATOR",
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": len(availability["warnings"]),
        "owner_readiness_gate_audit_passed": availability["owner_readiness_gate_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "blocked_state_represented_correctly": availability["blocked_state_represented_correctly"],
        "no_automatic_waiver": availability["no_automatic_waiver"],
        "boundary_clean": availability["boundary_clean"],
    }


def build_a_share_owner_quality_exceptions(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_ESCALATION,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        from trading_core.equity_owner_quality_exceptions.quality_exception_audit import audit_a_share_owner_quality_exceptions

        return audit_a_share_owner_quality_exceptions(as_of_date=as_of_date, paths=paths)
    config = QualityExceptionWorkflowConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
    issues = validate_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of {ALLOWED_MODES}")

    artifacts = artifact_paths(paths, as_of_date)
    data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    sources = input_paths(paths, as_of_date)
    source_payloads = {key: load_json(path) for key, path in sources.items()}
    decision = source_payloads["owner_readiness_gate_decision"]
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    payloads: dict[str, Any] = {
        "quality_exception_workflow_config": config.to_dict(source_gate_decision=decision.get("decision", "blocked")),
        "quality_exception_input_availability": availability,
        "quality_exception_source_resolution": resolution,
        "quality_exception_date_alignment": alignment,
    }
    _write_payloads(artifacts, payloads)
    if mode == VALIDATE_INPUTS:
        return _validation_result(availability, resolution, alignment)

    intake = build_blocked_gate_intake(
        as_of_date=as_of_date,
        decision=decision,
        evaluation=source_payloads["quality_threshold_evaluation"],
        candidates=source_payloads["quality_exception_candidate_list"],
    )
    payloads["blocked_gate_intake"] = intake
    _write_payloads(artifacts, payloads)
    if mode == INTAKE_GATE:
        return _intake_result(intake, artifacts)

    registry = build_quality_exception_registry(as_of_date=as_of_date, intake=intake)
    classification = classify_quality_exceptions(
        as_of_date=as_of_date,
        registry=registry,
        intake=intake,
        score_gate=source_payloads["owner_readiness_score_gate"],
    )
    gap = build_owner_readiness_gap_analysis(
        as_of_date=as_of_date,
        intake=intake,
        score=source_payloads["owner_readiness_score"],
        evaluation=source_payloads["quality_threshold_evaluation"],
        classification=classification,
    )
    explanation = build_threshold_failure_explanation(as_of_date=as_of_date, intake=intake, classification=classification)
    payloads.update(
        {
            "quality_exception_registry": registry,
            "quality_exception_classification": classification,
            "owner_readiness_gap_analysis": gap,
            "threshold_failure_explanation": explanation,
        }
    )
    _write_payloads(artifacts, payloads)
    if mode == CLASSIFY_EXCEPTIONS:
        return _classification_result(classification, intake, artifacts)

    waiver_eval = build_waiver_candidate_evaluation(as_of_date=as_of_date, classification=classification)
    waiver_policy = build_manual_waiver_policy(as_of_date=as_of_date)
    waiver_template = build_manual_waiver_request_template(as_of_date=as_of_date, evaluation=waiver_eval)
    waiver_record = build_manual_waiver_decision_record(as_of_date=as_of_date)
    severity = build_exception_severity_matrix(as_of_date=as_of_date)
    routing = build_exception_routing_matrix(as_of_date=as_of_date)
    sla = build_exception_sla_policy(as_of_date=as_of_date)
    escalation = build_escalation_workflow(as_of_date=as_of_date, classification=classification, routing=routing, sla=sla)
    developer_tracker = build_developer_follow_up_tracker(as_of_date=as_of_date, classification=classification)
    owner_checklist = build_owner_follow_up_checklist(as_of_date=as_of_date, classification=classification)
    owner_notice = build_blocked_daily_pack_owner_notice(as_of_date=as_of_date, intake=intake)
    boundary = build_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        blocking_reasons=availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"],
        warnings=intake.get("warnings", []),
    )
    audit_trail = build_exception_audit_trail(
        as_of_date=as_of_date,
        source_artifacts=sources,
        exception_registry=registry,
        waiver_record=waiver_record,
        escalation=escalation,
        owner_notice=owner_notice,
        developer_tracker=developer_tracker,
        boundary=boundary,
    )
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    trace = build_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    payloads.update(
        {
            "waiver_candidate_evaluation": waiver_eval,
            "manual_waiver_policy": waiver_policy,
            "manual_waiver_request_template": waiver_template,
            "manual_waiver_decision_record": waiver_record,
            "escalation_workflow": escalation,
            "developer_follow_up_tracker": developer_tracker,
            "owner_follow_up_checklist": owner_checklist,
            "blocked_daily_pack_owner_notice": owner_notice,
            "exception_severity_matrix": severity,
            "exception_routing_matrix": routing,
            "exception_sla_policy": sla,
            "exception_audit_trail": audit_trail,
            "quality_exception_source_trace": trace,
            "quality_exception_boundary_check": boundary,
        }
    )
    manifest = build_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        intake=intake,
        registry=registry,
        developer_tracker=developer_tracker,
        owner_checklist=owner_checklist,
        waiver_record=waiver_record,
        boundary=boundary,
    )
    summary = build_summary(as_of_date=as_of_date, intake=intake, registry=registry, waiver_record=waiver_record)
    payloads.update({"quality_exception_manifest": manifest, "quality_exception_summary": summary})
    _write_payloads(artifacts, payloads)
    write_reports(output_dir(paths, as_of_date), payloads)
    return {
        "builder_id": "A-SHARE-OWNER-QUALITY-EXCEPTION-WORKFLOW-BUILDER",
        "overall_passed": availability["overall_passed"] and resolution["overall_passed"] and alignment["overall_passed"] and boundary["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + boundary["blocking_reasons"],
        "warnings": len(intake.get("warnings", [])),
        "source_gate_decision": intake["source_gate_decision"],
        "blocked_gate_decision_preserved": intake["blocked_state_preserved"],
        "owner_operationally_acceptable": intake["owner_operationally_acceptable"],
        "minimum_owner_readiness_score": intake["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": intake["actual_owner_readiness_score"],
        "readiness_score_gap": intake["readiness_score_gap"],
        "quality_exception_count": registry["exception_count"],
        "developer_follow_up_count": developer_tracker["follow_up_count"],
        "manual_waiver_decision_status": waiver_record["manual_waiver_decision_status"],
        "manual_waiver_approval_recorded": waiver_record["manual_waiver_approval_recorded"],
        "auto_waiver_allowed": waiver_record["auto_waiver_allowed"],
        "waiver_changes_gate_decision": waiver_record["waiver_changes_gate_decision"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "quality_exception_workflow_report": str(artifacts["quality_exception_workflow_report"]),
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)


def _validation_result(availability: dict[str, Any], resolution: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-QUALITY-EXCEPTION-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "owner_readiness_gate_audit_passed": availability["owner_readiness_gate_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "blocked_state_represented_correctly": availability["blocked_state_represented_correctly"],
        "no_automatic_waiver": availability["no_automatic_waiver"],
    }


def _intake_result(intake: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-BLOCKED-GATE-INTAKE-BUILDER",
        "overall_passed": intake["blocked_state_preserved"],
        "blocking_reasons": [] if intake["blocked_state_preserved"] else ["blocked_gate_state_not_preserved"],
        "warnings": len(intake.get("warnings", [])),
        "source_gate_decision": intake["source_gate_decision"],
        "readiness_score_gap": intake["readiness_score_gap"],
        "blocked_gate_intake": str(artifacts["blocked_gate_intake"]),
    }


def _classification_result(classification: dict[str, Any], intake: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-QUALITY-EXCEPTION-CLASSIFIER",
        "overall_passed": classification["quality_exceptions_classified"],
        "blocking_reasons": [] if classification["quality_exceptions_classified"] else ["quality_exceptions_not_classified"],
        "warnings": len(intake.get("warnings", [])),
        "classified_count": classification["classified_count"],
        "quality_exception_classification": str(artifacts["quality_exception_classification"]),
    }
