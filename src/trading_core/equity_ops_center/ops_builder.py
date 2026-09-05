"""Builder for the v0.8.5 A-share daily ops command center."""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from trading_core.equity_data_quality.common import write_json
from trading_core.equity_ops_center.action_summary import build_ops_action_summary
from trading_core.equity_ops_center.artifact_navigation import build_ops_artifact_navigation
from trading_core.equity_ops_center.command_reference import build_ops_command_reference
from trading_core.equity_ops_center.date_alignment import build_ops_date_alignment
from trading_core.equity_ops_center.health_score import build_ops_health_score_card
from trading_core.equity_ops_center.input_availability import build_ops_input_availability, load_json, ops_input_paths
from trading_core.equity_ops_center.issue_summary import build_ops_issue_summary
from trading_core.equity_ops_center.module_status_matrix import build_ops_module_status_matrix
from trading_core.equity_ops_center.ops_boundary import build_ops_boundary_check
from trading_core.equity_ops_center.ops_config import (
    AGGREGATE_EXISTING_OPS_ARTIFACTS,
    AUDIT_EXISTING_OPS_CENTER,
    DEFAULT_AS_OF_DATE,
    OPS_FILES,
    RUN_SAFE_OPS_VALIDATION_CHAIN,
    OpsCenterConfig,
    ops_artifact_paths,
    ops_output_dir,
    validate_ops_config,
)
from trading_core.equity_ops_center.ops_execution_record import build_ops_execution_record
from trading_core.equity_ops_center.ops_manifest import build_ops_manifest, build_ops_summary
from trading_core.equity_ops_center.ops_plan import build_ops_plan, safe_audit_commands
from trading_core.equity_ops_center.ops_report import write_ops_reports
from trading_core.equity_ops_center.ops_source_trace import build_ops_source_trace
from trading_core.equity_ops_center.owner_next_steps import build_ops_owner_next_steps
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_daily_ops_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_ops_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-DAILY-OPS-CENTER-INPUT-VALIDATION",
        "mode": "validate_ops_inputs",
        "as_of_date": as_of_date,
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": availability["warnings"],
        "required_modules_available": availability["required_modules_available"],
    }


def build_a_share_daily_ops_center(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = AGGREGATE_EXISTING_OPS_ARTIFACTS,
    allow_date_mismatch: bool = False,
    allow_safe_validation_chain: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING_OPS_CENTER:
        from trading_core.equity_ops_center.ops_audit import audit_a_share_daily_ops_center

        return audit_a_share_daily_ops_center(as_of_date=as_of_date, paths=paths)
    config = OpsCenterConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch, allow_safe_validation_chain=allow_safe_validation_chain)
    issues = validate_ops_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    commands_executed = _run_safe_validation_chain(as_of_date, paths) if mode == RUN_SAFE_OPS_VALIDATION_CHAIN else []
    availability = build_ops_input_availability(paths=paths, as_of_date=as_of_date)
    if not availability["overall_passed"]:
        raise ValueError("; ".join(availability["blocking_reasons"]))
    artifacts = ops_artifact_paths(paths, as_of_date)
    input_paths = ops_input_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in input_paths.items()}
    date_alignment = build_ops_date_alignment(as_of_date=as_of_date, payloads=payloads, allow_date_mismatch=allow_date_mismatch)
    if date_alignment["blocking_reasons"]:
        raise ValueError("; ".join(date_alignment["blocking_reasons"]))
    plan = build_ops_plan(as_of_date=as_of_date, mode=mode)
    execution_record = build_ops_execution_record(as_of_date=as_of_date, mode=mode, commands_executed=commands_executed, safe_validation_chain_run=bool(commands_executed))
    issue_summary = build_ops_issue_summary(as_of_date=as_of_date, payloads=payloads)
    module_matrix = build_ops_module_status_matrix(as_of_date=as_of_date, availability=availability)
    health_score = build_ops_health_score_card(
        as_of_date=as_of_date,
        required_modules_passed=module_matrix["required_modules_passed"],
        issue_summary=issue_summary,
        critical_alert_count=int(payloads.get("owner_monitoring_audit", {}).get("alert_counts", {}).get("critical", 0)),
    )
    action_summary = build_ops_action_summary(as_of_date=as_of_date, payloads=payloads)
    command_reference = build_ops_command_reference(as_of_date=as_of_date)
    next_steps = build_ops_owner_next_steps(as_of_date=as_of_date, health_score=health_score, action_summary=action_summary)
    boundary = build_ops_boundary_check(paths=paths, as_of_date=as_of_date, warnings=availability["warnings"], blocking_reasons=[], commands_executed=commands_executed)
    output_paths = {key: artifacts[key] for key in artifacts if key not in {"ops_audit_json", "ops_audit_report"}}
    navigation = build_ops_artifact_navigation(paths=paths, as_of_date=as_of_date, input_paths=input_paths, output_paths=output_paths)
    generated_at = datetime.now(UTC).isoformat()
    source_trace = build_ops_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        source_paths=input_paths,
        output_paths=output_paths,
        command_policy_decisions={
            "mode": mode,
            "aggregate_existing_artifacts_only": mode == AGGREGATE_EXISTING_OPS_ARTIFACTS,
            "allow_safe_validation_chain": allow_safe_validation_chain,
            "commands_executed": commands_executed,
        },
    )
    payload: dict[str, Any] = {
        "ops_center_config": config.to_dict(),
        "ops_input_availability": availability,
        "ops_date_alignment": date_alignment,
        "ops_plan": plan,
        "ops_execution_record": execution_record,
        "ops_health_score_card": health_score,
        "ops_module_status_matrix": module_matrix,
        "ops_issue_summary": issue_summary,
        "ops_action_summary": action_summary,
        "ops_artifact_navigation": navigation,
        "ops_command_reference": command_reference,
        "ops_owner_next_steps": next_steps,
        "ops_source_trace": source_trace,
        "ops_boundary_check": boundary,
    }
    manifest = build_ops_manifest(
        as_of_date=as_of_date,
        generated_at=generated_at,
        mode=mode,
        health_score=health_score,
        issue_summary=issue_summary,
        action_summary=action_summary,
        execution_record=execution_record,
        output_artifacts={key: artifacts[key] for key in OPS_FILES},
        source_artifacts=input_paths,
        boundary=boundary,
    )
    summary = build_ops_summary(as_of_date=as_of_date, mode=mode, manifest=manifest, health_score=health_score)
    payload["ops_manifest"] = manifest
    payload["ops_summary"] = summary
    for key, value in payload.items():
        if key in artifacts:
            write_json(artifacts[key], value)
    write_ops_reports(ops_output_dir(paths, as_of_date), payload)
    return {
        "builder_id": "A-SHARE-DAILY-OPS-CENTER-BUILDER",
        "mode": mode,
        "as_of_date": as_of_date,
        "overall_passed": boundary["overall_passed"] and module_matrix["required_modules_passed"],
        "blocking_reasons": sorted(set(boundary["blocking_reasons"])),
        "warnings": availability["warnings"],
        "ops_health_score": health_score["score"],
        "ops_health_grade": health_score["grade"],
        "overall_status": health_score["overall_status"],
        "required_modules_available": availability["required_modules_available"],
        "commands_executed": commands_executed,
        "ops_manifest_path": str(artifacts["ops_manifest"]),
        "ops_summary_path": str(artifacts["ops_summary"]),
        "ops_command_center_report": str(artifacts["ops_command_center_report"]),
    }


def _run_safe_validation_chain(as_of_date: str, paths: ProjectPaths) -> list[str]:
    from trading_core.equity_current_day.current_day_audit import audit_a_share_current_day_research_run
    from trading_core.equity_data_refresh.data_refresh_audit import audit_a_share_daily_data_refresh
    from trading_core.equity_owner_dashboard.dashboard_audit import audit_a_share_owner_dashboard
    from trading_core.equity_owner_monitoring.monitoring_audit import audit_a_share_owner_monitoring
    from trading_core.equity_owner_remediation.remediation_audit import audit_a_share_owner_remediation

    audits = [
        audit_a_share_daily_data_refresh(as_of_date=as_of_date, paths=paths),
        audit_a_share_current_day_research_run(as_of_date=as_of_date, paths=paths),
        audit_a_share_owner_dashboard(as_of_date=as_of_date, paths=paths),
        audit_a_share_owner_monitoring(as_of_date=as_of_date, paths=paths),
        audit_a_share_owner_remediation(as_of_date=as_of_date, paths=paths),
    ]
    failures = [audit["audit_id"] for audit in audits if not audit.get("overall_passed")]
    if failures:
        raise ValueError("; ".join(f"{item}=failed" for item in failures))
    return safe_audit_commands(as_of_date)[:5]
