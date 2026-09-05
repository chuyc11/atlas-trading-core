"""Builder for v0.8.4 owner remediation runbooks and checklists."""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import write_json
from trading_core.equity_owner_remediation.action_checklist import build_safe_owner_action_checklist
from trading_core.equity_owner_remediation.dashboard_guide import build_dashboard_remediation_guide
from trading_core.equity_owner_remediation.data_guide import build_data_freshness_remediation_guide, build_schema_coverage_remediation_guide
from trading_core.equity_owner_remediation.dry_run_plan import build_dry_run_remediation_plan
from trading_core.equity_owner_remediation.input_availability import build_remediation_input_availability, load_json, remediation_input_paths
from trading_core.equity_owner_remediation.issue_catalog import build_issue_catalog
from trading_core.equity_owner_remediation.manual_verification import build_manual_verification_checklist
from trading_core.equity_owner_remediation.monitoring_guide import build_monitoring_remediation_guide
from trading_core.equity_owner_remediation.non_actionable_issues import build_non_actionable_issue_list
from trading_core.equity_owner_remediation.priority_summary import build_remediation_priority_summary
from trading_core.equity_owner_remediation.provider_guide import build_provider_remediation_guide
from trading_core.equity_owner_remediation.remediation_boundary import build_remediation_boundary_check
from trading_core.equity_owner_remediation.remediation_config import (
    AUDIT_EXISTING_REMEDIATION,
    BUILD_REMEDIATION_RUNBOOK,
    BUILD_SAFE_ACTION_CHECKLIST,
    DEFAULT_AS_OF_DATE,
    REMEDIATION_FILES,
    OwnerRemediationConfig,
    remediation_artifact_paths,
    remediation_output_dir,
    validate_remediation_config,
)
from trading_core.equity_owner_remediation.remediation_manifest import build_remediation_manifest, build_remediation_summary
from trading_core.equity_owner_remediation.remediation_mapping import build_alert_remediation_map, build_blocking_remediation_map, build_warning_remediation_map
from trading_core.equity_owner_remediation.remediation_report import write_remediation_reports
from trading_core.equity_owner_remediation.remediation_source_trace import build_remediation_source_trace
from trading_core.equity_owner_remediation.workflow_guide import build_workflow_remediation_guide
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_remediation_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_remediation_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-OWNER-REMEDIATION-INPUT-VALIDATION",
        "mode": "validate_remediation_inputs",
        "as_of_date": as_of_date,
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": availability["warnings"],
        "input_artifact_count": len(availability["input_artifacts"]),
    }


def build_a_share_owner_remediation(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_REMEDIATION_RUNBOOK,
    allow_date_mismatch: bool = False,
    allow_safe_local_dry_run: bool = False,
    allow_data_refresh_rerun: bool = False,
    allow_research_workflow_rerun: bool = False,
    allow_dashboard_rerun: bool = False,
    allow_monitoring_rerun: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING_REMEDIATION:
        from trading_core.equity_owner_remediation.remediation_audit import audit_a_share_owner_remediation

        return audit_a_share_owner_remediation(as_of_date=as_of_date, paths=paths)
    config = OwnerRemediationConfig(
        as_of_date=as_of_date,
        resolved_as_of_date=as_of_date,
        mode=mode,
        allow_date_mismatch=allow_date_mismatch,
        allow_safe_local_dry_run=allow_safe_local_dry_run,
        allow_data_refresh_rerun=allow_data_refresh_rerun,
        allow_research_workflow_rerun=allow_research_workflow_rerun,
        allow_dashboard_rerun=allow_dashboard_rerun,
        allow_monitoring_rerun=allow_monitoring_rerun,
    )
    issues = validate_remediation_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    availability = build_remediation_input_availability(paths=paths, as_of_date=as_of_date)
    if not availability["overall_passed"]:
        raise ValueError("; ".join(availability["blocking_reasons"]))
    artifacts = remediation_artifact_paths(paths, as_of_date)
    input_paths = remediation_input_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in input_paths.items()}
    generated_at = datetime.now(UTC).isoformat()
    issue_catalog = build_issue_catalog(as_of_date=as_of_date, payloads=payloads)
    issue_codes = [issue["issue_code"] for issue in issue_catalog.get("issues", [])]
    alert_codes = [str(event.get("rule_id")) for event in payloads.get("alert_event_log", {}).get("events", [])]
    warning_map = build_warning_remediation_map(issue_codes, as_of_date=as_of_date)
    blocking_map = build_blocking_remediation_map(issue_codes, as_of_date=as_of_date)
    alert_map = build_alert_remediation_map(alert_codes, as_of_date=as_of_date)
    guides = {
        "provider_remediation_guide": build_provider_remediation_guide(as_of_date),
        "data_freshness_remediation_guide": build_data_freshness_remediation_guide(as_of_date),
        "schema_coverage_remediation_guide": build_schema_coverage_remediation_guide(as_of_date),
        "workflow_remediation_guide": build_workflow_remediation_guide(as_of_date),
        "dashboard_remediation_guide": build_dashboard_remediation_guide(as_of_date),
        "monitoring_remediation_guide": build_monitoring_remediation_guide(as_of_date),
    }
    checklist = build_safe_owner_action_checklist(as_of_date=as_of_date, issue_catalog=issue_catalog)
    non_actionable = build_non_actionable_issue_list(as_of_date=as_of_date, payloads=payloads, issue_catalog=issue_catalog)
    dry_run_plan = build_dry_run_remediation_plan(as_of_date=as_of_date, checklist=checklist)
    priority_summary = build_remediation_priority_summary(as_of_date=as_of_date, issue_catalog=issue_catalog)
    boundary = build_remediation_boundary_check(paths=paths, as_of_date=as_of_date, warnings=availability["warnings"], blocking_reasons=[])
    manual_checklist = build_manual_verification_checklist(as_of_date=as_of_date, availability=availability, boundary=boundary)
    output_paths = _output_paths_for_trace(artifacts)
    source_trace = build_remediation_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        source_paths=list(input_paths.values()),
        output_paths=output_paths,
        issue_catalog=issue_catalog,
    )
    payload: dict[str, Any] = {
        "remediation_config": config.to_dict(),
        "remediation_input_availability": availability,
        "issue_catalog": issue_catalog,
        "warning_remediation_map": warning_map,
        "blocking_remediation_map": blocking_map,
        "alert_remediation_map": alert_map,
        **guides,
        "safe_owner_action_checklist": checklist,
        "manual_verification_checklist": manual_checklist,
        "non_actionable_issue_list": non_actionable,
        "dry_run_remediation_plan": dry_run_plan,
        "remediation_priority_summary": priority_summary,
        "remediation_source_trace": source_trace,
        "remediation_boundary_check": boundary,
    }
    manifest = build_remediation_manifest(
        as_of_date=as_of_date,
        generated_at=generated_at,
        mode=mode,
        issue_catalog=issue_catalog,
        priority_summary=priority_summary,
        checklist=checklist,
        output_artifacts={key: artifacts[key] for key in REMEDIATION_FILES},
        source_artifacts=input_paths,
        boundary=boundary,
    )
    summary = build_remediation_summary(as_of_date=as_of_date, mode=mode, manifest=manifest, priority_summary=priority_summary)
    payload["remediation_manifest"] = manifest
    payload["remediation_summary"] = summary
    for key, value in payload.items():
        if key in artifacts:
            write_json(artifacts[key], value)
    if mode in {BUILD_REMEDIATION_RUNBOOK, BUILD_SAFE_ACTION_CHECKLIST}:
        write_remediation_reports(remediation_output_dir(paths, as_of_date), payload)
    return {
        "builder_id": "A-SHARE-OWNER-REMEDIATION-BUILDER",
        "mode": mode,
        "as_of_date": as_of_date,
        "overall_passed": boundary["overall_passed"] and not checklist["blocking_reasons"],
        "blocking_reasons": sorted(set(boundary["blocking_reasons"] + checklist["blocking_reasons"])),
        "warnings": availability["warnings"],
        "issue_count": issue_catalog["issue_count"],
        "safe_action_count": checklist["safe_action_count"],
        "automatic_action_count": checklist["automatic_action_count"],
        "execute_remediation_actions": False,
        "remediation_manifest_path": str(artifacts["remediation_manifest"]),
        "remediation_summary_path": str(artifacts["remediation_summary"]),
        "owner_remediation_runbook_report": str(artifacts["owner_remediation_runbook_report"]),
    }


def _output_paths_for_trace(artifacts: dict[str, Path]) -> list[Path]:
    return [path for key, path in artifacts.items() if key not in {"remediation_audit_json", "remediation_audit_report"}]
