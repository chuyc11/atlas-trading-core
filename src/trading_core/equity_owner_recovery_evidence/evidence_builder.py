"""Builder for owner recovery evidence."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.artifact_completeness import build_artifact_completeness_evidence
from trading_core.equity_owner_recovery_evidence.date_alignment import build_date_alignment
from trading_core.equity_owner_recovery_evidence.evidence_boundary import build_recovery_evidence_boundary_check
from trading_core.equity_owner_recovery_evidence.evidence_config import ALLOWED_MODES, AUDIT_EXISTING, BUILD_IMPROVEMENT, COLLECT_EVIDENCE, DEFAULT_AS_OF_DATE, FILES, GRADE_QUALITY, RECOMMENDED_NEXT_VERSION, REPORTS, TARGET_VERSION, VALIDATE_INPUTS, RecoveryEvidenceConfig, artifact_paths, data_dir, output_dir, validate_config
from trading_core.equity_owner_recovery_evidence.evidence_gaps import build_evidence_gap_register, build_remaining_blocker_register
from trading_core.equity_owner_recovery_evidence.evidence_manifest import build_recovery_evidence_manifest, build_recovery_evidence_summary
from trading_core.equity_owner_recovery_evidence.evidence_quality import build_evidence_quality_grading
from trading_core.equity_owner_recovery_evidence.evidence_report import write_reports
from trading_core.equity_owner_recovery_evidence.evidence_source_trace import build_recovery_evidence_source_trace
from trading_core.equity_owner_recovery_evidence.follow_up_evidence import build_developer_follow_up_evidence_package, build_owner_follow_up_evidence_package
from trading_core.equity_owner_recovery_evidence.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_recovery_evidence.io import load_json, write_json
from trading_core.equity_owner_recovery_evidence.markdown_quality import build_markdown_quality_improvement_evidence
from trading_core.equity_owner_recovery_evidence.quality_issue_evidence import build_quality_issue_evidence_package
from trading_core.equity_owner_recovery_evidence.readiness_ledger import build_readiness_improvement_evidence_ledger
from trading_core.equity_owner_recovery_evidence.recovery_evidence_audit import audit_a_share_owner_recovery_evidence
from trading_core.equity_owner_recovery_evidence.reevaluation_prep import build_next_reevaluation_prep_checklist
from trading_core.equity_owner_recovery_evidence.score_impact_estimate import build_evidence_backed_score_impact_estimate
from trading_core.equity_owner_recovery_evidence.source_resolution import build_source_resolution
from trading_core.equity_owner_recovery_evidence.source_trace_improvement import build_source_trace_improvement_evidence
from trading_core.equity_owner_recovery_evidence.task_evidence import build_recovery_task_evidence_collection
from trading_core.equity_owner_recovery_evidence.warning_mapping_evidence import build_warning_mapping_evidence_package
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_recovery_evidence_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    payloads = {key: load_json(path) for key, path in input_paths(paths, as_of_date).items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=payloads)
    return _validation_result(availability, resolution, alignment)


def build_a_share_owner_recovery_evidence(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = COLLECT_EVIDENCE,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        return audit_a_share_owner_recovery_evidence(as_of_date=as_of_date, paths=paths)
    config = RecoveryEvidenceConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
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
    controlled_summary = source_payloads["controlled_reevaluation_summary"]
    source_gate_decision = controlled_summary.get("source_gate_decision", "blocked")
    source_score = int(controlled_summary.get("actual_owner_readiness_score", 0) or 0)
    minimum_score = int(controlled_summary.get("minimum_owner_readiness_score", 0) or 0)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    payloads: dict[str, Any] = {
        "recovery_evidence_config": config.to_dict(source_gate_decision=source_gate_decision, source_readiness_score=source_score, minimum_owner_readiness_score=minimum_score),
        "recovery_evidence_input_availability": availability,
        "recovery_evidence_source_resolution": resolution,
        "recovery_evidence_date_alignment": alignment,
    }
    _write_payloads(artifacts, payloads)
    if mode == VALIDATE_INPUTS:
        return _validation_result(availability, resolution, alignment)

    task = build_recovery_task_evidence_collection(
        as_of_date=as_of_date,
        backlog=source_payloads["recovery_task_backlog"],
        evidence_registry=source_payloads["recovery_task_evidence_registry"],
        status_tracker=source_payloads["recovery_task_status_tracker"],
    )
    developer = build_developer_follow_up_evidence_package(
        as_of_date=as_of_date,
        recovery_plan=source_payloads["developer_follow_up_recovery_plan"],
        execution_tracker=source_payloads["developer_follow_up_evidence_tracker"],
        quality_tracker=source_payloads["developer_follow_up_tracker"],
    )
    owner = build_owner_follow_up_evidence_package(as_of_date=as_of_date, owner_plan=source_payloads["owner_follow_up_recovery_plan"], execution_tracker=source_payloads["owner_follow_up_evidence_tracker"])
    quality_issue = build_quality_issue_evidence_package(as_of_date=as_of_date, classification=source_payloads["quality_exception_classification"], blocked_gate_intake=source_payloads["blocked_gate_intake"])
    warning = build_warning_mapping_evidence_package(as_of_date=as_of_date, threshold_evaluation=source_payloads["quality_threshold_evaluation"], classification=source_payloads["quality_exception_classification"])
    payloads.update(
        {
            "recovery_task_evidence_collection": task,
            "developer_follow_up_evidence_package": developer,
            "owner_follow_up_evidence_package": owner,
            "quality_issue_evidence_package": quality_issue,
            "warning_mapping_evidence_package": warning,
        }
    )
    _write_payloads(artifacts, payloads)
    if mode == COLLECT_EVIDENCE:
        pass

    grading = build_evidence_quality_grading(as_of_date=as_of_date, task_evidence=task, developer=developer, owner=owner)
    ledger = build_readiness_improvement_evidence_ledger(as_of_date=as_of_date, source_readiness_score=source_score, minimum_owner_readiness_score=minimum_score, task_evidence=task, quality_grading=grading)
    score = build_evidence_backed_score_impact_estimate(as_of_date=as_of_date, ledger=ledger)
    source_trace_improvement = build_source_trace_improvement_evidence(
        as_of_date=as_of_date,
        traces={
            "v0.8.17_controlled_reevaluation": source_payloads["controlled_reevaluation_source_trace"],
            "v0.8.14_quality_exception": source_payloads["quality_exception_source_trace"],
        },
    )
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    markdown = build_markdown_quality_improvement_evidence(output_roots=[paths.outputs_dir / "equity_owner_controlled_gate_reevaluation" / "daily" / as_of_date, paths.outputs_dir / "equity_owner_readiness_recovery_execution" / "daily" / as_of_date], as_of_date=as_of_date)
    completeness = build_artifact_completeness_evidence(as_of_date=as_of_date, required_paths={key: path for key, path in sources.items()})
    gaps = build_evidence_gap_register(as_of_date=as_of_date, task_evidence=task, developer=developer, owner=owner)
    blockers = build_remaining_blocker_register(as_of_date=as_of_date, gap_register=gaps, score_gap=max(minimum_score - source_score, 0))
    prep_stub = build_next_reevaluation_prep_checklist(as_of_date=as_of_date, quality=grading, source_trace=source_trace_improvement, artifact_completeness=completeness)
    boundary = build_recovery_evidence_boundary_check(paths=paths, as_of_date=as_of_date, source_gate_decision=source_gate_decision, blocking_reasons=availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"])
    prep = build_next_reevaluation_prep_checklist(as_of_date=as_of_date, quality=grading, source_trace=source_trace_improvement, artifact_completeness=completeness, boundary=boundary)
    payloads.update(
        {
            "source_trace_improvement_evidence": source_trace_improvement,
            "markdown_quality_improvement_evidence": markdown,
            "artifact_completeness_evidence": completeness,
            "readiness_improvement_evidence_ledger": ledger,
            "evidence_backed_score_impact_estimate": score,
            "evidence_quality_grading": grading,
            "evidence_gap_register": gaps,
            "remaining_blocker_register": blockers,
            "next_reevaluation_prep_checklist": prep,
            "recovery_evidence_boundary_check": boundary,
        }
    )
    _write_payloads(artifacts, payloads)
    manifest = build_recovery_evidence_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        source_gate_decision=source_gate_decision,
        source_readiness_score=source_score,
        minimum_owner_readiness_score=minimum_score,
        quality=grading,
        score=score,
        prep=prep,
        boundary=boundary,
        blocking_reasons=boundary["blocking_reasons"],
        warnings=boundary["warnings"],
    )
    summary = build_recovery_evidence_summary(as_of_date=as_of_date, manifest=manifest, gap_register=gaps, blockers=blockers)
    payloads.update({"recovery_evidence_manifest": manifest, "recovery_evidence_summary": summary})
    _write_payloads(artifacts, payloads)
    trace = build_recovery_evidence_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    payloads["recovery_evidence_source_trace"] = trace
    _write_payloads(artifacts, {"recovery_evidence_source_trace": trace})
    write_reports(output_dir(paths, as_of_date), payloads)
    trace = build_recovery_evidence_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    payloads["recovery_evidence_source_trace"] = trace
    _write_payloads(artifacts, {"recovery_evidence_source_trace": trace})

    return {
        "builder_id": "A-SHARE-OWNER-RECOVERY-EVIDENCE-BUILDER",
        "overall_passed": availability["overall_passed"] and resolution["overall_passed"] and alignment["overall_passed"] and boundary["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + boundary["blocking_reasons"],
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]) + len(boundary["warnings"]),
        "source_gate_decision": source_gate_decision,
        "source_readiness_score": source_score,
        "minimum_owner_readiness_score": minimum_score,
        "score_gap": max(minimum_score - source_score, 0),
        "evidence_record_count": grading["evidence_record_count"],
        "strong_evidence_count": grading["strong_evidence_count"],
        "audit_verified_evidence_count": grading["audit_verified_evidence_count"],
        "missing_evidence_count": grading["missing_evidence_count"],
        "overall_evidence_quality": grading["overall_evidence_quality"],
        "evidence_ready_for_next_reevaluation_prep": prep["ready_for_evidence_backed_gate_prep"],
        "actual_audited_score_changed": score["actual_audited_score_changed"],
        "new_audited_score": score["new_audited_score"],
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "source_gate_decision_preserved": True,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "forbidden_evidence_types_detected": task["forbidden_evidence_types_detected"],
        "forbidden_owner_developer_actions_detected": developer["forbidden_owner_developer_actions_detected"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "recovery_evidence_report": str(artifacts["recovery_evidence_collection_report"]),
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)


def _validation_result(availability: dict[str, Any], resolution: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-RECOVERY-EVIDENCE-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "controlled_reevaluation_audit_passed": availability["controlled_reevaluation_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "reevaluation_skipped": availability["reevaluation_skipped"],
        "new_gate_score_generated": availability["new_gate_score_generated"],
        "new_gate_decision_generated": availability["new_gate_decision_generated"],
        "source_readiness_score": availability["source_readiness_score"],
        "minimum_owner_readiness_score": availability["minimum_owner_readiness_score"],
    }
