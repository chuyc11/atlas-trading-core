"""Builder for controlled owner-readiness gate reevaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_boundary import build_boundary_check
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import ALLOWED_MODES, AUDIT_EXISTING, BUILD_PLAN, DEFAULT_AS_OF_DATE, EVALUATE_GUARD, FILES, RECOMMENDED_NEXT_VERSION, RECORD_SKIP, REPORTS, VALIDATE_INPUTS, ControlledReevaluationConfig, artifact_paths, data_dir, output_dir, validate_config
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_decision import build_controlled_reevaluation_decision
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_manifest import build_controlled_reevaluation_manifest, build_controlled_reevaluation_summary
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_reevaluation_audit import audit_a_share_owner_controlled_gate_reevaluation
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_report import write_reports
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_source_trace import build_controlled_source_trace
from trading_core.equity_owner_controlled_gate_reevaluation.date_alignment import build_date_alignment
from trading_core.equity_owner_controlled_gate_reevaluation.evidence_sufficiency import build_evidence_sufficiency_check
from trading_core.equity_owner_controlled_gate_reevaluation.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_controlled_gate_reevaluation.io import load_json, write_json
from trading_core.equity_owner_controlled_gate_reevaluation.not_ready_summary import build_not_ready_reason_summary
from trading_core.equity_owner_controlled_gate_reevaluation.prerequisite_validation import build_reevaluation_prerequisite_validation
from trading_core.equity_owner_controlled_gate_reevaluation.preservation_checks import build_source_gate_preservation_check, build_threshold_preservation_check, build_waiver_preservation_check
from trading_core.equity_owner_controlled_gate_reevaluation.readiness_guard import build_reevaluation_readiness_guard
from trading_core.equity_owner_controlled_gate_reevaluation.execution_plan import build_reevaluation_execution_plan
from trading_core.equity_owner_controlled_gate_reevaluation.skip_decision import build_reevaluation_skip_decision
from trading_core.equity_owner_controlled_gate_reevaluation.source_resolution import build_source_resolution
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_controlled_gate_reevaluation_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    payloads = {key: load_json(path) for key, path in input_paths(paths, as_of_date).items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=payloads)
    return _validation_result(availability, resolution, alignment)


def build_a_share_owner_controlled_gate_reevaluation(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = RECORD_SKIP,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        return audit_a_share_owner_controlled_gate_reevaluation(as_of_date=as_of_date, paths=paths)
    config = ControlledReevaluationConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
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
    source_summary = source_payloads["recovery_execution_summary"]
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    payloads: dict[str, Any] = {
        "controlled_reevaluation_config": config.to_dict(
            source_gate_decision=source_summary.get("source_gate_decision", "blocked"),
            minimum_score=source_summary.get("minimum_owner_readiness_score", 0),
            actual_score=source_summary.get("actual_owner_readiness_score", 0),
        ),
        "controlled_reevaluation_input_availability": availability,
        "controlled_reevaluation_source_resolution": resolution,
        "controlled_reevaluation_date_alignment": alignment,
    }
    _write_payloads(artifacts, payloads)
    if mode == VALIDATE_INPUTS:
        return _validation_result(availability, resolution, alignment)

    status_tracker = source_payloads["recovery_task_status_tracker"]
    evidence_registry = source_payloads["recovery_task_evidence_registry"]
    readiness_decision = source_payloads["gate_reevaluation_readiness_decision"]
    source_threshold = source_payloads["threshold_preservation_check"]
    source_waiver = source_payloads["waiver_preservation_check"]
    guard = build_reevaluation_readiness_guard(
        as_of_date=as_of_date,
        source_summary=source_summary,
        status_tracker=status_tracker,
        evidence_registry=evidence_registry,
        readiness_decision=readiness_decision,
        threshold=source_threshold,
        waiver=source_waiver,
    )
    prerequisite = build_reevaluation_prerequisite_validation(as_of_date=as_of_date, guard=guard)
    payloads.update({"reevaluation_readiness_guard": guard, "reevaluation_prerequisite_validation": prerequisite})
    _write_payloads(artifacts, payloads)
    if mode == EVALUATE_GUARD:
        return _guard_result(guard, artifacts)

    execution_plan = build_reevaluation_execution_plan(as_of_date=as_of_date, prerequisite_validation=prerequisite)
    payloads["reevaluation_execution_plan"] = execution_plan
    _write_payloads(artifacts, payloads)
    if mode == BUILD_PLAN:
        return _plan_result(execution_plan, artifacts)

    skip = build_reevaluation_skip_decision(as_of_date=as_of_date, guard=guard, execution_plan=execution_plan)
    not_ready = build_not_ready_reason_summary(as_of_date=as_of_date, guard=guard)
    source_gate = build_source_gate_preservation_check(as_of_date=as_of_date, source_summary=source_summary, gate_decision=source_payloads["owner_readiness_gate_decision"])
    threshold = build_threshold_preservation_check(as_of_date=as_of_date, source_summary=source_summary)
    waiver = build_waiver_preservation_check(as_of_date=as_of_date)
    evidence = build_evidence_sufficiency_check(as_of_date=as_of_date, evidence_registry=evidence_registry, status_tracker=status_tracker)
    decision = build_controlled_reevaluation_decision(as_of_date=as_of_date, skip_decision=skip)
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + source_gate["blocking_reasons"]
    boundary = build_boundary_check(paths=paths, as_of_date=as_of_date, blocking_reasons=blocking)
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    payloads.update(
        {
            "reevaluation_skip_decision": skip,
            "not_ready_reason_summary": not_ready,
            "source_gate_preservation_check": source_gate,
            "threshold_preservation_check": threshold,
            "waiver_preservation_check": waiver,
            "evidence_sufficiency_check": evidence,
            "controlled_reevaluation_decision": decision,
            "controlled_reevaluation_boundary_check": boundary,
        }
    )
    _write_payloads(artifacts, payloads)
    trace = build_controlled_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    manifest = build_controlled_reevaluation_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        source_summary=source_summary,
        guard=guard,
        skip_decision=skip,
        controlled_decision=decision,
        boundary=boundary,
    )
    summary = build_controlled_reevaluation_summary(
        as_of_date=as_of_date,
        source_summary=source_summary,
        guard=guard,
        skip_decision=skip,
        controlled_decision=decision,
    )
    payloads.update(
        {
            "controlled_reevaluation_source_trace": trace,
            "controlled_reevaluation_manifest": manifest,
            "controlled_reevaluation_summary": summary,
        }
    )
    _write_payloads(artifacts, payloads)
    write_reports(output_dir(paths, as_of_date), payloads)
    trace = build_controlled_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    payloads["controlled_reevaluation_source_trace"] = trace
    _write_payloads(artifacts, {"controlled_reevaluation_source_trace": trace})

    return {
        "builder_id": "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-BUILDER",
        "overall_passed": availability["overall_passed"] and resolution["overall_passed"] and alignment["overall_passed"] and boundary["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + boundary["blocking_reasons"],
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]) + len(boundary["warnings"]),
        "source_gate_decision": source_summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": source_summary.get("blocked_gate_decision_preserved"),
        "readiness_guard_passed": guard["readiness_guard_passed"],
        "reevaluation_allowed": guard["reevaluation_allowed"],
        "reevaluation_skipped": skip["reevaluation_skipped"],
        "reevaluation_skip_reason": skip["reevaluation_skip_reason"],
        "controlled_reevaluation_decision": decision["decision"],
        "gate_reevaluation_executed": decision["gate_reevaluation_executed"],
        "new_gate_score_generated": decision["new_gate_score_generated"],
        "new_gate_decision_generated": decision["new_gate_decision_generated"],
        "threshold_lowered": threshold["threshold_lowered"],
        "auto_waiver_allowed": waiver["auto_waiver_allowed"],
        "manual_waiver_approval_recorded": waiver["manual_waiver_approval_recorded"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "controlled_reevaluation_report": str(artifacts["controlled_reevaluation_report"]),
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)


def _validation_result(availability: dict[str, Any], resolution: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "recovery_execution_audit_passed": availability["recovery_execution_audit_passed"],
        "owner_readiness_gate_audit_passed": availability["owner_readiness_gate_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "blocked_gate_decision_preserved": availability["blocked_gate_decision_preserved"],
        "source_ready_for_future_gate_reevaluation": availability["source_ready_for_future_gate_reevaluation"],
        "source_gate_reevaluation_executed": availability["source_gate_reevaluation_executed"],
        "threshold_lowered": availability["threshold_lowered"],
        "auto_waiver_allowed": availability["auto_waiver_allowed"],
    }


def _guard_result(guard: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-OWNER-REEVALUATION-READINESS-GUARD-EVALUATOR",
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": 0,
        "readiness_guard_passed": guard["readiness_guard_passed"],
        "reevaluation_allowed": guard["reevaluation_allowed"],
        "reevaluation_block_reason": guard["reevaluation_block_reason"],
        "block_reasons": guard["block_reasons"],
        "reevaluation_readiness_guard": str(artifacts["reevaluation_readiness_guard"]),
    }


def _plan_result(execution_plan: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-OWNER-CONTROLLED-REEVALUATION-PLAN-BUILDER",
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": 0,
        "execution_status": execution_plan["execution_status"],
        "gate_reevaluation_executed": execution_plan["gate_reevaluation_executed"],
        "rerun_owner_readiness_gate": execution_plan["rerun_owner_readiness_gate"],
        "reevaluation_execution_plan": str(artifacts["reevaluation_execution_plan"]),
    }

