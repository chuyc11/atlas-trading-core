"""Builder for v0.9.1 owner/operator experience."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_operator_experience.action_menu import build_operator_action_menu
from trading_core.equity_owner_operator_experience.artifact_navigation import build_artifact_navigation_index
from trading_core.equity_owner_operator_experience.audit_test_summary import build_audit_and_test_status_summary
from trading_core.equity_owner_operator_experience.blocker_digest import build_unresolved_blocker_digest
from trading_core.equity_owner_operator_experience.boundary import build_operator_boundary_check
from trading_core.equity_owner_operator_experience.capability_matrix import build_operator_capability_matrix
from trading_core.equity_owner_operator_experience.daily_status_card import build_owner_daily_status_card
from trading_core.equity_owner_operator_experience.date_alignment import build_date_alignment
from trading_core.equity_owner_operator_experience.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_operator_experience.io import load_json, write_json
from trading_core.equity_owner_operator_experience.known_blocked_state import build_known_blocked_state_banner, build_known_blocked_state_explanation
from trading_core.equity_owner_operator_experience.manifest import build_operator_manifest
from trading_core.equity_owner_operator_experience.next_step_decision_aid import build_owner_next_step_decision_aid
from trading_core.equity_owner_operator_experience.operator_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    BUILD_STATUS,
    DEFAULT_AS_OF_DATE,
    FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    OperatorExperienceConfig,
    artifact_paths,
    data_dir,
    output_dir,
    validate_config,
)
from trading_core.equity_owner_operator_experience.operator_experience_audit import audit_a_share_owner_operator_experience
from trading_core.equity_owner_operator_experience.rc_status_summary import build_rc_status_summary
from trading_core.equity_owner_operator_experience.report import write_reports
from trading_core.equity_owner_operator_experience.safety_boundary_panel import build_safety_boundary_status_panel
from trading_core.equity_owner_operator_experience.source_resolution import build_source_resolution
from trading_core.equity_owner_operator_experience.source_trace import build_operator_source_trace
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_operator_experience_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None, allow_date_mismatch: bool = False) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    payloads = {key: load_json(path) if path.suffix.lower() == ".json" else {} for key, path in input_paths(paths, as_of_date).items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=payloads, allow_date_mismatch=allow_date_mismatch)
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "source_release_candidate": availability["source_release_candidate"],
        "known_owner_readiness_state": availability["known_owner_readiness_state"],
        "owner_operationally_acceptable": availability["owner_operationally_acceptable"],
        "v090_full_pytest_passed": availability["v090_full_pytest_passed"],
        "v090_audit_sweep_passed": availability["v090_audit_sweep_passed"],
    }


def build_a_share_owner_operator_experience(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_STATUS,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        return audit_a_share_owner_operator_experience(as_of_date=as_of_date, paths=paths)
    config = OperatorExperienceConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
    issues = validate_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of {ALLOWED_MODES}")
    artifacts = artifact_paths(paths, as_of_date)
    data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    output_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    sources = input_paths(paths, as_of_date)
    source_payloads = {key: load_json(path) if path.suffix.lower() == ".json" else {} for key, path in sources.items()}
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    config_payload = config.to_dict(source=availability)
    full_pytest = source_payloads.get("v090_full_pytest_result", {})
    v090_summary = source_payloads.get("v090_owner_release_summary", {})
    v090_boundary = source_payloads.get("v090_boundary_check", {})
    rc_audit = source_payloads.get("v090_rc_audit", {})
    rc_decision = source_payloads.get("v090_release_candidate_decision", {})
    blocker_register = source_payloads.get("v0821_unresolved_blocker_register", {})

    status = build_owner_daily_status_card(as_of_date=as_of_date, availability=availability, full_pytest=full_pytest, summary=v090_summary, boundary=v090_boundary)
    banner = build_known_blocked_state_banner(as_of_date=as_of_date, availability=availability)
    explanation = build_known_blocked_state_explanation(as_of_date=as_of_date, availability=availability)
    capability = build_operator_capability_matrix(as_of_date=as_of_date)
    menu = build_operator_action_menu(as_of_date=as_of_date)
    navigation = build_artifact_navigation_index(paths=paths, as_of_date=as_of_date)
    next_step = build_owner_next_step_decision_aid(as_of_date=as_of_date)
    rc_summary = build_rc_status_summary(as_of_date=as_of_date, audit=rc_audit, decision=rc_decision, summary=v090_summary)
    audit_test = build_audit_and_test_status_summary(as_of_date=as_of_date, full_pytest=full_pytest, rc_summary=rc_summary)
    safety = build_safety_boundary_status_panel(as_of_date=as_of_date)
    blockers = build_unresolved_blocker_digest(as_of_date=as_of_date, register=blocker_register)
    boundary = build_operator_boundary_check(paths=paths, as_of_date=as_of_date)
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + boundary["blocking_reasons"]
    warnings = availability["warnings"] + resolution["warnings"] + alignment["warnings"] + boundary["warnings"]
    summary = {
        "summary_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-SUMMARY",
        "target_version": config_payload["target_version"],
        "as_of_date": as_of_date,
        "source_release_candidate": config_payload["source_release_candidate"],
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": availability["owner_operationally_acceptable"],
        "readiness_score": availability["previous_readiness_score"],
        "minimum_owner_readiness_score": availability["minimum_owner_readiness_score"],
        "score_gap": availability["score_gap"],
        "owner_daily_status_generated": True,
        "known_blocked_state_banner_generated": True,
        "known_blocked_state_explanation_generated": True,
        "operator_action_menu_generated": True,
        "artifact_navigation_index_generated": True,
        "forbidden_operator_actions_present": menu["forbidden_operator_actions_present"],
        "v090_full_pytest_passed": availability["v090_full_pytest_passed"],
        "v090_audit_sweep_passed": availability["v090_audit_sweep_passed"],
        "run_full_pytest": False,
        "targeted_pytest_required": True,
        "full_pytest_deferred_until": "next-major-closeout-or-explicit-request",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    manifest = build_operator_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        summary=summary,
        boundary=boundary,
        blocking_reasons=blocking,
        warnings=warnings,
    )
    payloads: dict[str, Any] = {
        "operator_experience_config": config_payload,
        "operator_input_availability": availability,
        "operator_source_resolution": resolution,
        "operator_date_alignment": alignment,
        "owner_daily_status_card": status,
        "known_blocked_state_banner": banner,
        "known_blocked_state_explanation": explanation,
        "operator_capability_matrix": capability,
        "operator_action_menu": menu,
        "artifact_navigation_index": navigation,
        "owner_next_step_decision_aid": next_step,
        "rc_status_summary": rc_summary,
        "audit_and_test_status_summary": audit_test,
        "safety_boundary_status_panel": safety,
        "unresolved_blocker_digest": blockers,
        "operator_boundary_check": boundary,
        "operator_manifest": manifest,
        "operator_summary": summary,
    }
    _write_payloads(artifacts, payloads)
    trace = build_operator_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary, source_resolution=resolution)
    payloads["operator_source_trace"] = trace
    _write_payloads(artifacts, {"operator_source_trace": trace})
    write_reports(output_dir(paths, as_of_date), payloads)
    boundary = build_operator_boundary_check(paths=paths, as_of_date=as_of_date)
    payloads["operator_boundary_check"] = boundary
    _write_payloads(artifacts, {"operator_boundary_check": boundary})
    trace = build_operator_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary, source_resolution=resolution)
    payloads["operator_source_trace"] = trace
    _write_payloads(artifacts, {"operator_source_trace": trace})
    return {
        "builder_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-BUILDER",
        "overall_passed": summary["overall_passed"] and boundary["overall_passed"],
        "blocking_reasons": summary["blocking_reasons"] + boundary["blocking_reasons"],
        "warnings": len(summary["warnings"]) + len(boundary["warnings"]),
        **summary,
        "owner_daily_status_report": str(artifacts["owner_daily_status_report"]),
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)
