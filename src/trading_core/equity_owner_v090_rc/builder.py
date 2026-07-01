"""Builder for v0.9.0 owner-readiness RC closeout."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v090_rc.audit_sweep import run_audit_sweep
from trading_core.equity_owner_v090_rc.boundary import build_boundary_check
from trading_core.equity_owner_v090_rc.boundary_sweep import build_boundary_sweep_result
from trading_core.equity_owner_v090_rc.date_alignment import build_date_alignment
from trading_core.equity_owner_v090_rc.documentation_freeze import build_documentation_freeze_result
from trading_core.equity_owner_v090_rc.full_pytest_result import load_reusable_full_pytest_result, run_full_pytest
from trading_core.equity_owner_v090_rc.input_availability import build_input_availability, input_paths
from trading_core.equity_owner_v090_rc.io import load_json, write_json
from trading_core.equity_owner_v090_rc.known_blocked_state import build_known_blocked_state_disclosure
from trading_core.equity_owner_v090_rc.manifest import build_manifest
from trading_core.equity_owner_v090_rc.owner_summary import build_owner_release_summary
from trading_core.equity_owner_v090_rc.rc_decision import build_release_candidate_decision
from trading_core.equity_owner_v090_rc.report import write_reports
from trading_core.equity_owner_v090_rc.source_resolution import build_source_resolution
from trading_core.equity_owner_v090_rc.source_trace import build_source_trace
from trading_core.equity_owner_v090_rc.source_trace_sweep import build_source_trace_sweep_result
from trading_core.equity_owner_v090_rc.v090_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    DEFAULT_AS_OF_DATE,
    FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    RUN_FULL_REGRESSION,
    V090RCConfig,
    artifact_paths,
    data_dir,
    output_dir,
    validate_config,
)
from trading_core.equity_owner_v090_rc.v090_rc_audit import audit_a_share_owner_v090_rc
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_v090_rc_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None, allow_date_mismatch: bool = False) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    payloads = {key: load_json(path) for key, path in input_paths(paths, as_of_date).items()}
    alignment = build_date_alignment(as_of_date=as_of_date, payloads=payloads, allow_date_mismatch=allow_date_mismatch)
    blocking = availability["blocking_reasons"] + resolution["blocking_reasons"] + alignment["blocking_reasons"]
    return {
        "builder_id": "A-SHARE-OWNER-V090-RC-INPUT-VALIDATOR",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability["warnings"]) + len(resolution["warnings"]) + len(alignment["warnings"]),
        "v0821_closeout_review_audit_passed": availability["v0821_closeout_review_audit_passed"],
        "source_gate_decision": availability["source_gate_decision"],
        "v090_rc_readiness_source_decision": availability["v090_rc_readiness_source_decision"],
        "owner_operationally_acceptable": availability["owner_operationally_acceptable"],
    }


def build_a_share_owner_v090_rc(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = RUN_FULL_REGRESSION,
    allow_date_mismatch: bool = False,
    skip_full_pytest: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        return audit_a_share_owner_v090_rc(as_of_date=as_of_date, paths=paths)
    config = V090RCConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch, skip_full_pytest=skip_full_pytest)
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
    config_payload = config.to_dict(source=availability)
    full_pytest = None
    if not skip_full_pytest:
        full_pytest = load_reusable_full_pytest_result(artifacts["v090_full_pytest_result"], as_of_date=as_of_date)
    if full_pytest is None:
        full_pytest = run_full_pytest(as_of_date=as_of_date, skip_full_pytest=skip_full_pytest)
    audit_sweep = run_audit_sweep(paths=paths, as_of_date=as_of_date)
    boundary_sweep = build_boundary_sweep_result(paths=paths, as_of_date=as_of_date)
    docs = build_documentation_freeze_result(paths=paths, as_of_date=as_of_date)
    disclosure = build_known_blocked_state_disclosure(as_of_date=as_of_date, availability=availability)
    trace_sweep = build_source_trace_sweep_result(paths=paths, as_of_date=as_of_date)
    decision = build_release_candidate_decision(
        as_of_date=as_of_date,
        full_pytest=full_pytest,
        audit_sweep=audit_sweep,
        boundary_sweep=boundary_sweep,
        source_trace_sweep=trace_sweep,
        documentation_freeze=docs,
        disclosure=disclosure,
    )
    summary = build_owner_release_summary(
        as_of_date=as_of_date,
        availability=availability,
        full_pytest=full_pytest,
        audit_sweep=audit_sweep,
        boundary_sweep=boundary_sweep,
        source_trace_sweep=trace_sweep,
        documentation_freeze=docs,
        disclosure=disclosure,
        decision=decision,
    )
    boundary = build_boundary_check(as_of_date=as_of_date, availability=availability, full_pytest=full_pytest, audit_sweep=audit_sweep, boundary_sweep=boundary_sweep)
    output_artifacts = {key: artifacts[key] for key in FILES | REPORTS}
    manifest = build_manifest(
        as_of_date=as_of_date,
        output_artifacts=output_artifacts,
        source_artifacts=sources,
        summary=summary,
        boundary=boundary,
        blocking_reasons=decision["blocking_reasons"] + boundary["blocking_reasons"],
        warnings=decision["warnings"] + boundary["warnings"],
    )
    payloads: dict[str, Any] = {
        "v090_rc_config": config_payload,
        "v090_input_availability": availability,
        "v090_source_resolution": resolution,
        "v090_date_alignment": alignment,
        "v090_full_pytest_result": full_pytest,
        "v090_audit_sweep_result": audit_sweep,
        "v090_boundary_sweep_result": boundary_sweep,
        "v090_source_trace_sweep_result": trace_sweep,
        "v090_documentation_freeze_result": docs,
        "v090_known_blocked_state_disclosure": disclosure,
        "v090_release_candidate_decision": decision,
        "v090_owner_release_summary": summary,
        "v090_boundary_check": boundary,
        "v090_manifest": manifest,
    }
    _write_payloads(artifacts, payloads)
    trace = build_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary, source_resolution=resolution)
    payloads["v090_source_trace"] = trace
    _write_payloads(artifacts, {"v090_source_trace": trace})
    write_reports(output_dir(paths, as_of_date), payloads)
    trace = build_source_trace(paths=paths, as_of_date=as_of_date, source_paths=sources, output_paths=output_artifacts, boundary=boundary, source_resolution=resolution)
    payloads["v090_source_trace"] = trace
    _write_payloads(artifacts, {"v090_source_trace": trace})
    return {
        "builder_id": "A-SHARE-OWNER-V090-RC-BUILDER",
        "overall_passed": decision["overall_passed"],
        "blocking_reasons": decision["blocking_reasons"] + boundary["blocking_reasons"],
        "warnings": len(decision["warnings"]) + len(boundary["warnings"]),
        **summary,
        "v090_rc_report": str(artifacts["v090_rc_report"]),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _write_payloads(artifacts: dict[str, Any], payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        if key in artifacts:
            write_json(artifacts[key], payload)
