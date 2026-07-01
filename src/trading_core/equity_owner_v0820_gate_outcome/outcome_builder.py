"""Builder for v0.8.20 owner gate outcome."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v0820_gate_outcome.boundary import build_boundary_check
from trading_core.equity_owner_v0820_gate_outcome.branch_decision import build_branch_decision
from trading_core.equity_owner_v0820_gate_outcome.controlled_reevaluation import build_controlled_gate_reevaluation_outcome
from trading_core.equity_owner_v0820_gate_outcome.date_alignment import build_date_alignment
from trading_core.equity_owner_v0820_gate_outcome.final_blocked_closeout import build_final_blocked_closeout
from trading_core.equity_owner_v0820_gate_outcome.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_v0820_gate_outcome.io import load_json, write_json
from trading_core.equity_owner_v0820_gate_outcome.manifest import build_manifest
from trading_core.equity_owner_v0820_gate_outcome.outcome_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    BUILD_AND_AUDIT,
    DEFAULT_AS_OF_DATE,
    EXECUTE_CONTROLLED,
    FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    V0820OutcomeConfig,
    artifact_paths,
    data_dir,
    output_dir,
    validate_config,
)
from trading_core.equity_owner_v0820_gate_outcome.outcome_summary import build_owner_outcome_summary
from trading_core.equity_owner_v0820_gate_outcome.preservation_checks import build_boundary_preservation_check, build_threshold_preservation_check, build_waiver_exclusion_check
from trading_core.equity_owner_v0820_gate_outcome.report import write_reports
from trading_core.equity_owner_v0820_gate_outcome.source_resolution import build_source_resolution
from trading_core.equity_owner_v0820_gate_outcome.source_trace import build_source_trace
from trading_core.equity_owner_v0820_gate_outcome.v0820_outcome_audit import audit_a_share_owner_v0820_gate_outcome
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_v0820_gate_outcome_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    payloads = {key: load_json(path) for key, path in input_paths(paths, as_of_date).items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=payloads)
    return _validation_result(availability, resolution, alignment)


def build_a_share_owner_v0820_gate_outcome(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_AND_AUDIT,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        return audit_a_share_owner_v0820_gate_outcome(as_of_date=as_of_date, paths=paths)
    config = V0820OutcomeConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
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
    minimum_score = int(availability.get("minimum_owner_readiness_score") or 75)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    payloads: dict[str, Any] = {
        "v0820_outcome_config": config.to_dict(source_gate_decision=source_gate_decision, minimum_owner_readiness_score=minimum_score),
        "v0820_input_availability": availability,
        "v0820_source_resolution": resolution,
        "v0820_date_alignment": alignment,
    }
    _write_payloads(artifacts, payloads)

    boundary_for_branch = build_boundary_check(paths=paths, as_of_date=as_of_date, source_gate_decision=source_gate_decision, blocking_reasons=availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"])
    branch = build_branch_decision(as_of_date=as_of_date, availability=availability, boundary_clean=boundary_for_branch["overall_passed"])
    if mode == EXECUTE_CONTROLLED and branch.get("selected_branch") != "controlled_gate_reevaluation":
        raise RuntimeError("controlled gate reevaluation refused because branch is not selected or not eligible")
    controlled = build_controlled_gate_reevaluation_outcome(as_of_date=as_of_date, branch=branch, availability=availability)
    closeout = build_final_blocked_closeout(as_of_date=as_of_date, branch=branch, availability=availability)
    threshold = build_threshold_preservation_check(as_of_date=as_of_date, availability=availability)
    waiver = build_waiver_exclusion_check(as_of_date=as_of_date)
    preservation = build_boundary_preservation_check(as_of_date=as_of_date)
    summary = build_owner_outcome_summary(as_of_date=as_of_date, branch=branch, controlled=controlled, closeout=closeout, availability=availability)
    payloads.update(
        {
            "v0820_branch_decision": branch,
            "controlled_gate_reevaluation_outcome": controlled,
            "final_blocked_closeout": closeout,
            "threshold_preservation_check": threshold,
            "waiver_exclusion_check": waiver,
            "boundary_preservation_check": preservation,
            "v0820_owner_outcome_summary": summary,
            "v0820_boundary_check": boundary_for_branch,
        }
    )
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    manifest = build_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        summary=summary,
        boundary=boundary_for_branch,
        blocking_reasons=boundary_for_branch["blocking_reasons"],
        warnings=boundary_for_branch["warnings"],
    )
    payloads["v0820_manifest"] = manifest
    _write_payloads(artifacts, payloads)
    trace = build_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary_for_branch)
    payloads["v0820_source_trace"] = trace
    _write_payloads(artifacts, {"v0820_source_trace": trace})
    write_reports(output_dir(paths, as_of_date), payloads)
    trace = build_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary_for_branch)
    payloads["v0820_source_trace"] = trace
    _write_payloads(artifacts, {"v0820_source_trace": trace})
    if mode == BUILD_AND_AUDIT:
        audit_a_share_owner_v0820_gate_outcome(as_of_date=as_of_date, paths=paths)
    return {
        "builder_id": "A-SHARE-OWNER-V0820-GATE-OUTCOME-BUILDER",
        "overall_passed": availability["overall_passed"] and resolution["overall_passed"] and alignment["overall_passed"] and boundary_for_branch["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + boundary_for_branch["blocking_reasons"],
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]) + len(boundary_for_branch["warnings"]),
        **summary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "v0820_owner_outcome_report": str(artifacts["v0820_owner_gate_outcome_report"]),
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)


def _validation_result(availability: dict[str, Any], resolution: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-V0820-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "evidence_backed_prep_audit_passed": availability["evidence_backed_prep_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "source_gate_decision_preserved": availability["source_gate_decision_preserved"],
        "v0819_eligibility_decision": availability["v0819_eligibility_decision"],
        "v0819_ready_for_controlled_gate_reevaluation": availability["v0819_ready_for_controlled_gate_reevaluation"],
        "reevaluation_input_package_generated": availability["reevaluation_input_package_generated"],
    }

