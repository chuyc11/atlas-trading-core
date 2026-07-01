"""Builder for evidence-backed reevaluation prep."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.date_alignment import build_date_alignment
from trading_core.equity_owner_evidence_backed_reevaluation_prep.evidence_backed_prep_audit import audit_a_share_owner_evidence_backed_reevaluation_prep
from trading_core.equity_owner_evidence_backed_reevaluation_prep.evidence_sufficiency import build_evidence_sufficiency_decision
from trading_core.equity_owner_evidence_backed_reevaluation_prep.evidence_to_gate_mapping import build_evidence_to_gate_mapping
from trading_core.equity_owner_evidence_backed_reevaluation_prep.eligibility_decision import build_controlled_reevaluation_eligibility_decision
from trading_core.equity_owner_evidence_backed_reevaluation_prep.gap_decision import build_remaining_evidence_gap_decision
from trading_core.equity_owner_evidence_backed_reevaluation_prep.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_evidence_backed_reevaluation_prep.io import load_json, write_json
from trading_core.equity_owner_evidence_backed_reevaluation_prep.next_execution_plan import build_next_gate_reevaluation_execution_plan
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_boundary import build_prep_boundary_check
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import ALLOWED_MODES, AUDIT_EXISTING, DEFAULT_AS_OF_DATE, EVALUATE_SUFFICIENCY, FILES, RECOMMENDED_NEXT_VERSION, REPORTS, EvidenceBackedPrepConfig, artifact_paths, data_dir, output_dir, validate_config
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_manifest import build_prep_manifest, build_prep_summary
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_report import write_reports
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_source_trace import build_prep_source_trace
from trading_core.equity_owner_evidence_backed_reevaluation_prep.preservation_packages import build_boundary_preservation_package, build_gate_threshold_preservation_package, build_waiver_exclusion_package
from trading_core.equity_owner_evidence_backed_reevaluation_prep.readiness_checklist import build_evidence_backed_readiness_checklist
from trading_core.equity_owner_evidence_backed_reevaluation_prep.reevaluation_input_package import build_reevaluation_input_package
from trading_core.equity_owner_evidence_backed_reevaluation_prep.score_impact_readiness import build_score_impact_readiness_summary
from trading_core.equity_owner_evidence_backed_reevaluation_prep.source_resolution import build_source_resolution
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_evidence_backed_reevaluation_prep_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    payloads = {key: load_json(path) for key, path in input_paths(paths, as_of_date).items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=payloads)
    return _validation_result(availability, resolution, alignment)


def build_a_share_owner_evidence_backed_reevaluation_prep(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = EVALUATE_SUFFICIENCY,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        return audit_a_share_owner_evidence_backed_reevaluation_prep(as_of_date=as_of_date, paths=paths)
    config = EvidenceBackedPrepConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
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
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    source_gate_decision = availability.get("source_gate_decision", "blocked")
    source_score = int(availability.get("source_readiness_score", 0) or 0)
    minimum_score = int(availability.get("minimum_owner_readiness_score", 0) or 0)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    payloads: dict[str, Any] = {
        "evidence_backed_prep_config": config.to_dict(source_gate_decision=source_gate_decision, source_readiness_score=source_score, minimum_owner_readiness_score=minimum_score),
        "evidence_backed_prep_input_availability": availability,
        "evidence_backed_prep_source_resolution": resolution,
        "evidence_backed_prep_date_alignment": alignment,
    }
    _write_payloads(artifacts, payloads)

    quality = source_payloads["evidence_quality_grading"]
    gaps = source_payloads["evidence_gap_register"]
    blockers = source_payloads["remaining_blocker_register"]
    sufficiency = build_evidence_sufficiency_decision(as_of_date=as_of_date, availability=availability, quality=quality, blockers=blockers)
    mapping = build_evidence_to_gate_mapping(as_of_date=as_of_date, gaps=gaps, sufficiency=sufficiency)
    package = build_reevaluation_input_package(as_of_date=as_of_date, availability=availability, sufficiency=sufficiency, mapping=mapping, source_artifacts=availability["source_artifacts"])
    score = build_score_impact_readiness_summary(as_of_date=as_of_date, availability=availability, source_score_estimate=source_payloads["evidence_backed_score_impact_estimate"], sufficiency=sufficiency)
    threshold = build_gate_threshold_preservation_package(as_of_date=as_of_date, availability=availability)
    waiver = build_waiver_exclusion_package(as_of_date=as_of_date)
    preservation = build_boundary_preservation_package(as_of_date=as_of_date)
    checklist = build_evidence_backed_readiness_checklist(as_of_date=as_of_date, sufficiency=sufficiency, package=package)
    gap_decision = build_remaining_evidence_gap_decision(as_of_date=as_of_date, gaps=gaps, blockers=blockers, sufficiency=sufficiency)
    eligibility = build_controlled_reevaluation_eligibility_decision(as_of_date=as_of_date, sufficiency=sufficiency, gap_decision=gap_decision)
    plan = build_next_gate_reevaluation_execution_plan(as_of_date=as_of_date, eligibility=eligibility)
    boundary = build_prep_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        source_gate_decision=source_gate_decision,
        blocking_reasons=availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"],
    )
    payloads.update(
        {
            "evidence_sufficiency_for_reevaluation_decision": sufficiency,
            "evidence_to_gate_mapping": mapping,
            "reevaluation_input_package": package,
            "score_impact_readiness_summary": score,
            "gate_threshold_preservation_package": threshold,
            "waiver_exclusion_package": waiver,
            "boundary_preservation_package": preservation,
            "evidence_backed_readiness_checklist": checklist,
            "remaining_evidence_gap_decision": gap_decision,
            "controlled_reevaluation_eligibility_decision": eligibility,
            "next_gate_reevaluation_execution_plan": plan,
            "evidence_backed_prep_boundary_check": boundary,
        }
    )
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    manifest = build_prep_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        availability=availability,
        sufficiency=sufficiency,
        eligibility=eligibility,
        gap_decision=gap_decision,
        boundary=boundary,
        blocking_reasons=boundary["blocking_reasons"],
        warnings=boundary["warnings"],
    )
    summary = build_prep_summary(as_of_date=as_of_date, manifest=manifest, input_package=package)
    payloads.update({"evidence_backed_prep_manifest": manifest, "evidence_backed_prep_summary": summary})
    _write_payloads(artifacts, payloads)
    trace = build_prep_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    payloads["evidence_backed_prep_source_trace"] = trace
    _write_payloads(artifacts, {"evidence_backed_prep_source_trace": trace})
    write_reports(output_dir(paths, as_of_date), payloads)
    trace = build_prep_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    payloads["evidence_backed_prep_source_trace"] = trace
    _write_payloads(artifacts, {"evidence_backed_prep_source_trace": trace})
    return {
        "builder_id": "A-SHARE-OWNER-EVIDENCE-BACKED-REEVALUATION-PREP-BUILDER",
        "overall_passed": availability["overall_passed"] and resolution["overall_passed"] and alignment["overall_passed"] and boundary["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + boundary["blocking_reasons"],
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]) + len(boundary["warnings"]),
        "source_gate_decision": source_gate_decision,
        "source_readiness_score": source_score,
        "minimum_owner_readiness_score": minimum_score,
        "score_gap": max(minimum_score - source_score, 0),
        "evidence_record_count": availability.get("evidence_record_count"),
        "strong_evidence_count": availability.get("strong_evidence_count"),
        "audit_verified_evidence_count": availability.get("audit_verified_evidence_count"),
        "missing_evidence_count": availability.get("missing_evidence_count"),
        "overall_evidence_quality": availability.get("overall_evidence_quality"),
        "remaining_gap_count": gap_decision.get("remaining_gap_count"),
        "blocking_gap_count": gap_decision.get("blocking_gap_count"),
        "evidence_ready_for_next_reevaluation_prep": availability.get("evidence_ready_for_next_reevaluation_prep"),
        "ready_for_controlled_gate_reevaluation": eligibility.get("ready_for_controlled_gate_reevaluation"),
        "eligibility_decision": eligibility.get("eligibility_decision"),
        "reevaluation_input_package_generated": package.get("reevaluation_input_package_generated"),
        "reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "source_gate_decision_preserved": True,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "score_impact_readiness_is_not_official_score": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "evidence_backed_prep_report": str(artifacts["evidence_backed_gate_reevaluation_prep_report"]),
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)


def _validation_result(availability: dict[str, Any], resolution: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-EVIDENCE-BACKED-REEVALUATION-PREP-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "recovery_evidence_audit_passed": availability["recovery_evidence_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "source_gate_decision_preserved": availability["source_gate_decision_preserved"],
        "source_readiness_score": availability["source_readiness_score"],
        "minimum_owner_readiness_score": availability["minimum_owner_readiness_score"],
        "evidence_ready_for_next_reevaluation_prep": availability["evidence_ready_for_next_reevaluation_prep"],
        "new_gate_score_generated": availability["new_gate_score_generated"],
        "new_gate_decision_generated": availability["new_gate_decision_generated"],
    }

