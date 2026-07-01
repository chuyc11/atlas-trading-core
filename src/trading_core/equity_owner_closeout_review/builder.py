"""Builder for v0.8.21 owner-readiness closeout review."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.blocked_decision_lineage import build_blocked_decision_lineage
from trading_core.equity_owner_closeout_review.boundary import build_boundary_check
from trading_core.equity_owner_closeout_review.closeout_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    BUILD_RC_SCOPE,
    DEFAULT_AS_OF_DATE,
    FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    CloseoutReviewConfig,
    artifact_paths,
    data_dir,
    output_dir,
    validate_config,
)
from trading_core.equity_owner_closeout_review.closeout_review_audit import audit_a_share_owner_closeout_review
from trading_core.equity_owner_closeout_review.date_alignment import build_date_alignment
from trading_core.equity_owner_closeout_review.evidence_insufficiency_lineage import build_evidence_insufficiency_lineage
from trading_core.equity_owner_closeout_review.final_blocked_closeout_review import build_final_blocked_closeout_review
from trading_core.equity_owner_closeout_review.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_closeout_review.io import load_json, write_json
from trading_core.equity_owner_closeout_review.lineage_review import build_lineage_review
from trading_core.equity_owner_closeout_review.manifest import build_manifest
from trading_core.equity_owner_closeout_review.readiness_score_lineage import build_readiness_score_lineage
from trading_core.equity_owner_closeout_review.report import write_reports
from trading_core.equity_owner_closeout_review.source_resolution import build_source_resolution
from trading_core.equity_owner_closeout_review.source_trace import build_source_trace
from trading_core.equity_owner_closeout_review.unresolved_blockers import build_unresolved_blocker_register
from trading_core.equity_owner_closeout_review.v090_audit_sweep_plan import build_v090_audit_sweep_plan
from trading_core.equity_owner_closeout_review.v090_documentation_freeze import build_v090_documentation_freeze_checklist
from trading_core.equity_owner_closeout_review.v090_full_regression_plan import build_v090_full_regression_plan
from trading_core.equity_owner_closeout_review.v090_rc_decision import build_v090_release_candidate_readiness_decision
from trading_core.equity_owner_closeout_review.v090_rc_scope import build_v090_rc_scope_proposal
from trading_core.equity_owner_closeout_review.v090_risk_register import build_v090_release_risk_register
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_closeout_review_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None, allow_date_mismatch: bool = False) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    payloads = {key: load_json(path) for key, path in input_paths(paths, as_of_date).items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=payloads, allow_date_mismatch=allow_date_mismatch)
    return _validation_result(availability, resolution, alignment)


def build_a_share_owner_closeout_review(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_RC_SCOPE,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        return audit_a_share_owner_closeout_review(as_of_date=as_of_date, paths=paths)
    config = CloseoutReviewConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
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
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    base_blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    config_payload = config.to_dict(
        source_gate_decision=availability.get("source_gate_decision"),
        selected_v0820_branch=availability.get("selected_v0820_branch"),
        previous_readiness_score=availability.get("previous_readiness_score"),
        minimum_owner_readiness_score=availability.get("minimum_owner_readiness_score"),
        score_gap=availability.get("score_gap"),
    )
    boundary = build_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        source_gate_decision=availability.get("source_gate_decision", "blocked"),
        selected_v0820_branch=availability.get("selected_v0820_branch", "final_blocked_closeout"),
        blocking_reasons=base_blocking,
    )
    lineage = build_lineage_review(as_of_date=as_of_date, payloads=source_payloads)
    blocked_lineage = build_blocked_decision_lineage(as_of_date=as_of_date, lineage=lineage)
    score_lineage = build_readiness_score_lineage(as_of_date=as_of_date, lineage=lineage, availability=availability)
    evidence_lineage = build_evidence_insufficiency_lineage(as_of_date=as_of_date, lineage=lineage, availability=availability)
    final_review = build_final_blocked_closeout_review(as_of_date=as_of_date, availability=availability)
    blockers = build_unresolved_blocker_register(as_of_date=as_of_date, availability=availability)
    rc_scope = build_v090_rc_scope_proposal(as_of_date=as_of_date, blockers=blockers)
    regression_plan = build_v090_full_regression_plan(as_of_date=as_of_date)
    audit_sweep_plan = build_v090_audit_sweep_plan(as_of_date=as_of_date)
    docs_freeze = build_v090_documentation_freeze_checklist(as_of_date=as_of_date)
    risk_register = build_v090_release_risk_register(as_of_date=as_of_date)
    rc_decision = build_v090_release_candidate_readiness_decision(
        as_of_date=as_of_date,
        final_review=final_review,
        regression_plan=regression_plan,
        audit_sweep_plan=audit_sweep_plan,
        boundary=boundary,
    )
    summary = _summary(
        as_of_date=as_of_date,
        availability=availability,
        final_review=final_review,
        blockers=blockers,
        rc_decision=rc_decision,
    )
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    manifest = build_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        summary=summary,
        boundary=boundary,
        blocking_reasons=boundary["blocking_reasons"],
        warnings=boundary["warnings"],
    )
    payloads: dict[str, Any] = {
        "closeout_review_config": config_payload,
        "closeout_input_availability": availability,
        "closeout_source_resolution": resolution,
        "closeout_date_alignment": alignment,
        "v0813_to_v0820_lineage_review": lineage,
        "blocked_decision_lineage": blocked_lineage,
        "readiness_score_lineage": score_lineage,
        "evidence_insufficiency_lineage": evidence_lineage,
        "final_blocked_closeout_review": final_review,
        "unresolved_blocker_register": blockers,
        "v090_rc_scope_proposal": rc_scope,
        "v090_full_regression_plan": regression_plan,
        "v090_audit_sweep_plan": audit_sweep_plan,
        "v090_documentation_freeze_checklist": docs_freeze,
        "v090_release_risk_register": risk_register,
        "v090_release_candidate_readiness_decision": rc_decision,
        "closeout_boundary_check": boundary,
        "closeout_manifest": manifest,
        "closeout_summary": summary,
    }
    _write_payloads(artifacts, payloads)
    trace = build_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary, source_resolution=resolution)
    payloads["closeout_source_trace"] = trace
    _write_payloads(artifacts, {"closeout_source_trace": trace})
    write_reports(output_dir(paths, as_of_date), payloads)
    trace = build_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary, source_resolution=resolution)
    payloads["closeout_source_trace"] = trace
    _write_payloads(artifacts, {"closeout_source_trace": trace})
    if mode == BUILD_RC_SCOPE:
        audit_a_share_owner_closeout_review(as_of_date=as_of_date, paths=paths)
    return {
        "builder_id": "A-SHARE-OWNER-CLOSEOUT-REVIEW-BUILDER",
        "overall_passed": not boundary["blocking_reasons"] and rc_decision["overall_passed"],
        "blocking_reasons": boundary["blocking_reasons"] + rc_decision["blocking_reasons"],
        "warnings": len(boundary["warnings"]) + len(rc_decision["warnings"]),
        **summary,
        "closeout_review_report": str(artifacts["closeout_review_report"]),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _summary(*, as_of_date: str, availability: dict[str, Any], final_review: dict[str, Any], blockers: dict[str, Any], rc_decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-CLOSEOUT-REVIEW-SUMMARY",
        "target_version": final_review["target_version"],
        "as_of_date": as_of_date,
        "source_gate_decision": availability.get("source_gate_decision"),
        "selected_v0820_branch": availability.get("selected_v0820_branch"),
        "previous_readiness_score": availability.get("previous_readiness_score"),
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "score_gap": availability.get("score_gap"),
        "owner_operationally_acceptable": availability.get("owner_operationally_acceptable"),
        "blocked_state_intentional": final_review.get("blocked_state_intentional"),
        "blocked_state_audited": final_review.get("blocked_state_audited"),
        "blocked_state_misrepresented_as_acceptable": final_review.get("blocked_state_misrepresented_as_acceptable"),
        "new_gate_score_generated": availability.get("new_gate_score_generated"),
        "new_gate_decision_generated": availability.get("new_gate_decision_generated"),
        "execute_full_pytest": False,
        "v090_rc_scope_generated": True,
        "v090_full_regression_plan_generated": True,
        "v090_audit_sweep_plan_generated": True,
        "v090_documentation_freeze_checklist_generated": True,
        "v090_release_risk_register_generated": True,
        "v090_release_candidate_readiness_decision": rc_decision.get("decision"),
        "unresolved_blocker_count": blockers.get("unresolved_blocker_count"),
        "blockers_that_block_owner_readiness_acceptance": blockers.get("blockers_that_block_owner_readiness_acceptance"),
        "blockers_that_block_v090_rc": blockers.get("blockers_that_block_v090_rc"),
        "full_pytest_run": False,
        "targeted_pytest_required": True,
        "full_pytest_deferred_until": "v0.9.0",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)


def _validation_result(availability: dict[str, Any], resolution: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-CLOSEOUT-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "v0820_outcome_audit_passed": availability["v0820_outcome_audit_passed"],
        "selected_v0820_branch": availability["selected_v0820_branch"],
        "source_gate_decision": availability["source_gate_decision"],
        "controlled_reevaluation_executed": availability["controlled_reevaluation_executed"],
        "final_blocked_closeout_generated": availability["final_blocked_closeout_generated"],
        "threshold_lowered": availability["threshold_lowered"],
        "auto_waiver_allowed": availability["auto_waiver_allowed"],
    }
