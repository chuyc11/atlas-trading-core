"""Builder for v0.8.13 owner readiness gate."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_gate.date_alignment import build_date_alignment
from trading_core.equity_owner_readiness_gate.gate_boundary import build_boundary_check
from trading_core.equity_owner_readiness_gate.gate_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    BUILD_POLICY,
    BUILD_REPORT,
    DEFAULT_AS_OF_DATE,
    DEFAULT_MINIMUM_OWNER_READINESS_SCORE,
    EVALUATE_GATE,
    FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    OwnerReadinessGateConfig,
    artifact_paths,
    data_dir,
    output_dir,
    validate_config,
)
from trading_core.equity_owner_readiness_gate.gate_decision import build_gate_decision, build_quality_threshold_evaluation
from trading_core.equity_owner_readiness_gate.gate_manifest import build_manifest, build_summary
from trading_core.equity_owner_readiness_gate.gate_report import write_reports
from trading_core.equity_owner_readiness_gate.gate_source_trace import build_source_trace
from trading_core.equity_owner_readiness_gate.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_readiness_gate.io import load_json, write_json
from trading_core.equity_owner_readiness_gate.quality_exception_candidates import build_quality_exception_candidates
from trading_core.equity_owner_readiness_gate.quality_gates import (
    build_artifact_navigation_quality_gate,
    build_boundary_quality_gate,
    build_daily_pack_completeness_gate,
    build_markdown_report_quality_gate,
    build_owner_next_step_quality_gate,
    build_protected_path_quality_gate,
    build_safe_action_quality_gate,
    build_source_trace_quality_gate,
    build_trend_sufficiency_quality_gate,
    build_warning_issue_quality_gate,
)
from trading_core.equity_owner_readiness_gate.release_recommendation import build_owner_release_recommendation
from trading_core.equity_owner_readiness_gate.score_gate import build_owner_readiness_score_gate
from trading_core.equity_owner_readiness_gate.source_resolution import build_source_resolution
from trading_core.equity_owner_readiness_gate.threshold_policy import build_daily_pack_quality_threshold_policy, build_owner_readiness_threshold_policy
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_readiness_gate_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-OWNER-READINESS-GATE-INPUT-VALIDATOR",
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": len(availability["warnings"]),
        "owner_daily_pack_history_audit_passed": availability["owner_daily_pack_history_audit_passed"],
        "owner_daily_pack_audit_passed": availability["owner_daily_pack_audit_passed"],
        "source_workflow_mode": availability["source_workflow_mode"],
        "boundary_clean": availability["boundary_clean"],
    }


def build_a_share_owner_readiness_gate(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = EVALUATE_GATE,
    minimum_owner_readiness_score: int = DEFAULT_MINIMUM_OWNER_READINESS_SCORE,
    allow_date_mismatch: bool = False,
    allow_known_non_blocking_warnings: bool = True,
    allow_insufficient_history_if_correctly_flagged: bool = True,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        from trading_core.equity_owner_readiness_gate.owner_readiness_gate_audit import audit_a_share_owner_readiness_gate

        return audit_a_share_owner_readiness_gate(as_of_date=as_of_date, paths=paths)
    config = OwnerReadinessGateConfig(
        as_of_date=as_of_date,
        mode=mode,
        minimum_owner_readiness_score=minimum_owner_readiness_score,
        allow_date_mismatch=allow_date_mismatch,
        allow_known_non_blocking_warnings=allow_known_non_blocking_warnings,
        allow_insufficient_history_if_correctly_flagged=allow_insufficient_history_if_correctly_flagged,
    )
    issues = validate_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of {ALLOWED_MODES}")

    artifacts = artifact_paths(paths, as_of_date)
    data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    sources = input_paths(paths, as_of_date)
    source_payloads = {key: load_json(path) for key, path in sources.items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=source_payloads, allow_date_mismatch=allow_date_mismatch)
    owner_policy = build_owner_readiness_threshold_policy(
        as_of_date=as_of_date,
        minimum_owner_readiness_score=minimum_owner_readiness_score,
        allow_known_non_blocking_warnings=allow_known_non_blocking_warnings,
        allow_insufficient_history_if_correctly_flagged=allow_insufficient_history_if_correctly_flagged,
    )
    quality_policy = build_daily_pack_quality_threshold_policy(
        as_of_date=as_of_date,
        minimum_owner_readiness_score=minimum_owner_readiness_score,
        allow_known_non_blocking_warnings=allow_known_non_blocking_warnings,
        allow_insufficient_history_if_correctly_flagged=allow_insufficient_history_if_correctly_flagged,
    )
    payloads: dict[str, Any] = {
        "owner_readiness_gate_config": config.to_dict(),
        "owner_readiness_gate_input_availability": availability,
        "owner_readiness_gate_source_resolution": resolution,
        "owner_readiness_gate_date_alignment": alignment,
        "owner_readiness_threshold_policy": owner_policy,
        "daily_pack_quality_threshold_policy": quality_policy,
    }
    _write_payloads(artifacts, payloads)
    if mode == "validate_owner_readiness_gate_inputs":
        return _validation_result(availability, resolution, alignment)
    if mode == BUILD_POLICY:
        return _policy_result(owner_policy, quality_policy, artifacts)

    gates = _build_gates(as_of_date=as_of_date, payloads=source_payloads, policy=owner_policy)
    payloads.update(gates)
    provisional_exceptions = build_quality_exception_candidates(as_of_date=as_of_date, gates=gates)
    decision = build_gate_decision(
        as_of_date=as_of_date,
        gates=gates,
        score=source_payloads["owner_readiness_score"],
        policy=owner_policy,
        exceptions=provisional_exceptions["candidates"],
    )
    exceptions = build_quality_exception_candidates(as_of_date=as_of_date, gates=gates)
    evaluation = build_quality_threshold_evaluation(as_of_date=as_of_date, gates=gates, decision=decision)
    recommendation = build_owner_release_recommendation(as_of_date=as_of_date, decision=decision)
    boundary = build_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        blocking_reasons=availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"],
        warnings=decision["warnings"],
    )
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    trace = build_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary)
    payloads.update(
        {
            "owner_readiness_gate_decision": decision,
            "quality_threshold_evaluation": evaluation,
            "quality_exception_candidate_list": exceptions,
            "owner_release_recommendation": recommendation,
            "owner_readiness_gate_source_trace": trace,
            "owner_readiness_gate_boundary_check": boundary,
        }
    )
    manifest = build_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        decision=decision,
        score=source_payloads["owner_readiness_score"],
        boundary=boundary,
        exceptions=exceptions,
    )
    summary = build_summary(as_of_date=as_of_date, decision=decision, recommendation=recommendation, audit_ready=True)
    payloads.update({"owner_readiness_gate_manifest": manifest, "owner_readiness_gate_summary": summary})
    _write_payloads(artifacts, payloads)
    if mode in {EVALUATE_GATE, BUILD_REPORT}:
        write_reports(output_dir(paths, as_of_date), payloads)
    return {
        "builder_id": "A-SHARE-OWNER-READINESS-GATE-BUILDER",
        "overall_passed": availability["overall_passed"] and resolution["overall_passed"] and alignment["overall_passed"] and boundary["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"] + boundary["blocking_reasons"],
        "warnings": len(decision["warnings"]),
        "source_workflow_mode": decision["source_workflow_mode"],
        "decision": decision["decision"],
        "owner_operationally_acceptable": decision["owner_operationally_acceptable"],
        "required_gates_passed": decision["required_gates_passed"],
        "minimum_owner_readiness_score": decision["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": decision["actual_owner_readiness_score"],
        "actual_owner_readiness_grade": decision["actual_owner_readiness_grade"],
        "quality_exception_candidate_count": exceptions["candidate_count"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "owner_readiness_gate_report": str(artifacts["owner_readiness_gate_report"]),
    }


def _build_gates(*, as_of_date: str, payloads: dict[str, Any], policy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "owner_readiness_score_gate": build_owner_readiness_score_gate(as_of_date=as_of_date, score=payloads["owner_readiness_score"], policy=policy),
        "daily_pack_completeness_gate": build_daily_pack_completeness_gate(as_of_date=as_of_date, completeness=payloads["daily_pack_completeness_trend"], policy=policy),
        "warning_issue_quality_gate": build_warning_issue_quality_gate(as_of_date=as_of_date, warning=payloads["warning_issue_trend_baseline"], policy=policy),
        "safe_action_quality_gate": build_safe_action_quality_gate(as_of_date=as_of_date, safe=payloads["safe_action_trend_baseline"], policy=policy),
        "protected_path_quality_gate": build_protected_path_quality_gate(as_of_date=as_of_date, protected=payloads["protected_path_trend_baseline"], policy=policy),
        "boundary_quality_gate": build_boundary_quality_gate(as_of_date=as_of_date, boundary=payloads["boundary_trend_baseline"], policy=policy),
        "source_trace_quality_gate": build_source_trace_quality_gate(as_of_date=as_of_date, trace=payloads["source_trace_quality_trend"], policy=policy),
        "trend_sufficiency_quality_gate": build_trend_sufficiency_quality_gate(as_of_date=as_of_date, sufficiency=payloads["owner_readiness_trend_sufficiency"], policy=policy),
        "markdown_report_quality_gate": build_markdown_report_quality_gate(as_of_date=as_of_date, completeness=payloads["daily_pack_completeness_trend"], policy=policy),
        "artifact_navigation_quality_gate": build_artifact_navigation_quality_gate(as_of_date=as_of_date, manifest=payloads["daily_pack_history_manifest"], source_trace=payloads["daily_pack_history_source_trace"]),
        "owner_next_step_quality_gate": build_owner_next_step_quality_gate(as_of_date=as_of_date, next_step=payloads["owner_next_step_trend"]),
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)


def _validation_result(availability: dict[str, Any], resolution: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-READINESS-GATE-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "owner_daily_pack_history_audit_passed": availability["owner_daily_pack_history_audit_passed"],
        "owner_daily_pack_audit_passed": availability["owner_daily_pack_audit_passed"],
        "source_workflow_mode": availability["source_workflow_mode"],
        "boundary_clean": availability["boundary_clean"],
    }


def _policy_result(owner_policy: dict[str, Any], quality_policy: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-OWNER-READINESS-GATE-POLICY-BUILDER",
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": 0,
        "minimum_owner_readiness_score": owner_policy["minimum_owner_readiness_score"],
        "owner_readiness_threshold_policy": str(artifacts["owner_readiness_threshold_policy"]),
        "daily_pack_quality_threshold_policy": str(artifacts["daily_pack_quality_threshold_policy"]),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
