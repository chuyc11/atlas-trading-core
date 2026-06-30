"""Builder for v0.8.11 owner daily pack."""

from __future__ import annotations

import json

from trading_core.equity_owner_daily_pack.artifact_navigation import build_artifact_navigation, source_paths
from trading_core.equity_owner_daily_pack.boundary_digest import build_boundary_digest
from trading_core.equity_owner_daily_pack.candidate_digest import build_candidate_tracking_digest
from trading_core.equity_owner_daily_pack.daily_pack_boundary import build_boundary_check
from trading_core.equity_owner_daily_pack.daily_pack_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    BUILD_DECISION_PACK,
    DEFAULT_AS_OF_DATE,
    FILES,
    REPORTS,
    DailyPackConfig,
    artifact_paths,
    data_dir,
    validate_config,
)
from trading_core.equity_owner_daily_pack.daily_pack_manifest import build_manifest, build_summary
from trading_core.equity_owner_daily_pack.daily_pack_report import (
    render_decision_pack_report,
    render_next_step_report,
    render_research_digest_report,
    render_runbook_report,
    render_source_trace_report,
    render_status_brief_report,
)
from trading_core.equity_owner_daily_pack.daily_pack_source_trace import build_source_trace
from trading_core.equity_owner_daily_pack.daily_runbook import build_daily_runbook
from trading_core.equity_owner_daily_pack.date_alignment import build_date_alignment
from trading_core.equity_owner_daily_pack.decision_pack import build_decision_pack
from trading_core.equity_owner_daily_pack.input_availability import build_input_availability
from trading_core.equity_owner_daily_pack.next_step_checklist import build_next_step_checklist
from trading_core.equity_owner_daily_pack.ops_digest import build_monitoring_remediation_ops_digest
from trading_core.equity_owner_daily_pack.portfolio_digest import build_virtual_portfolio_digest
from trading_core.equity_owner_daily_pack.protected_path_digest import build_protected_path_digest
from trading_core.equity_owner_daily_pack.research_digest import build_research_output_digest
from trading_core.equity_owner_daily_pack.safe_action_digest import build_safe_action_digest
from trading_core.equity_owner_daily_pack.source_resolution import build_source_resolution
from trading_core.equity_owner_daily_pack.source_trace_digest import build_source_trace_digest
from trading_core.equity_owner_daily_pack.status_brief import build_status_brief
from trading_core.equity_owner_daily_pack.warning_issue_digest import build_warning_issue_digest
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_daily_pack_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict:
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-OWNER-DAILY-PACK-INPUT-VALIDATOR",
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": len(availability["warnings"]),
        "build_output_ops_refresh_audit_passed": availability["build_output_ops_refresh_audit_passed"],
        "build_output_dashboard_audit_passed": availability["build_output_dashboard_audit_passed"],
        "repeatability_audit_passed": availability["repeatability_audit_passed"],
        "gated_build_audit_passed": availability["gated_build_audit_passed"],
    }


def build_a_share_owner_daily_pack(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_DECISION_PACK,
    allow_date_mismatch: bool = False,
    paths: ProjectPaths | None = None,
) -> dict:
    paths = default_paths(paths)
    config = DailyPackConfig(as_of_date=as_of_date, mode=mode, allow_date_mismatch=allow_date_mismatch)
    issues = validate_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of {ALLOWED_MODES}")
    if mode == AUDIT_EXISTING:
        raise ValueError("use audit-a-share-owner-daily-pack for audit_existing mode")
    artifacts = artifact_paths(paths, as_of_date)
    data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, input_availability=availability, allow_date_mismatch=allow_date_mismatch)
    payloads = {
        "daily_pack_config": config.to_dict(),
        "daily_pack_input_availability": availability,
        "daily_pack_source_resolution": resolution,
        "daily_pack_date_alignment": alignment,
    }
    _write_json(payloads, artifacts)
    if mode in {"validate_daily_pack_inputs", "resolve_daily_pack_sources"}:
        return {
            "builder_id": "A-SHARE-OWNER-DAILY-PACK-BUILDER",
            "overall_passed": availability.get("overall_passed", False) and resolution.get("overall_passed", False) and alignment.get("overall_passed", False),
            "blocking_reasons": availability.get("blocking_reasons", []) + resolution.get("blocking_reasons", []) + alignment.get("blocking_reasons", []),
            "warnings": len(availability.get("warnings", []) + resolution.get("warnings", []) + alignment.get("warnings", [])),
            "source_workflow_mode": "build_from_existing_data",
            "recommended_next_version": "v0.8.12-a-share-build-output-daily-pack-history-and-owner-readiness-trends",
        }
    payloads.update(_build_pack_payloads(paths, as_of_date))
    payloads["daily_pack_artifact_navigation"] = build_artifact_navigation(paths=paths, as_of_date=as_of_date)
    payloads["owner_operations_decision_pack"] = build_decision_pack(as_of_date=as_of_date, payloads=payloads)
    _write_json(payloads, artifacts)
    source_artifacts = source_paths(paths, as_of_date)
    output_artifacts = {key: value for key, value in artifacts.items() if key in FILES}
    source_trace = build_source_trace(paths=paths, as_of_date=as_of_date, source_artifacts=source_artifacts, output_artifacts=output_artifacts, source_resolution=resolution)
    payloads["daily_pack_source_trace"] = source_trace
    boundary = build_boundary_check(paths=paths, as_of_date=as_of_date, payloads=payloads, source_resolution=resolution)
    payloads["daily_pack_boundary_check"] = boundary
    manifest = build_manifest(as_of_date=as_of_date, mode=mode, payloads=payloads, source_trace=source_trace, boundary=boundary, output_artifacts=output_artifacts, source_artifacts=source_artifacts, paths=paths)
    summary = build_summary(as_of_date=as_of_date, mode=mode, manifest=manifest, input_availability=availability, decision_pack=payloads["owner_operations_decision_pack"])
    payloads["daily_pack_manifest"] = manifest
    payloads["daily_pack_summary"] = summary
    _write_json(payloads, artifacts)
    _write_reports(artifacts, as_of_date, payloads, summary)
    return _builder_result(summary, artifacts)


def _build_pack_payloads(paths: ProjectPaths, as_of_date: str) -> dict:
    return {
        "owner_daily_status_brief": build_status_brief(paths=paths, as_of_date=as_of_date),
        "owner_daily_runbook": build_daily_runbook(as_of_date=as_of_date),
        "owner_next_step_checklist": build_next_step_checklist(paths=paths, as_of_date=as_of_date),
        "research_output_digest": build_research_output_digest(paths=paths, as_of_date=as_of_date),
        "candidate_tracking_digest": build_candidate_tracking_digest(paths=paths, as_of_date=as_of_date),
        "virtual_portfolio_digest": build_virtual_portfolio_digest(paths=paths, as_of_date=as_of_date),
        "warning_issue_digest": build_warning_issue_digest(paths=paths, as_of_date=as_of_date),
        "safe_action_digest": build_safe_action_digest(paths=paths, as_of_date=as_of_date),
        "monitoring_remediation_ops_digest": build_monitoring_remediation_ops_digest(paths=paths, as_of_date=as_of_date),
        "protected_path_digest": build_protected_path_digest(paths=paths, as_of_date=as_of_date),
        "source_trace_digest": build_source_trace_digest(paths=paths, as_of_date=as_of_date),
        "boundary_digest": build_boundary_digest(paths=paths, as_of_date=as_of_date),
    }


def _builder_result(summary: dict, artifacts: dict) -> dict:
    return {
        "builder_id": "A-SHARE-OWNER-DAILY-PACK-BUILDER",
        "overall_passed": summary.get("overall_passed", False),
        "blocking_reasons": summary.get("blocking_reasons", []),
        "warnings": len(summary.get("warnings", [])),
        "source_workflow_mode": summary.get("source_workflow_mode"),
        "not_investment_decision_pack": summary.get("not_investment_decision_pack", False),
        "build_output_ops_refresh_audit_passed": summary.get("build_output_ops_refresh_audit_passed", False),
        "build_output_dashboard_audit_passed": summary.get("build_output_dashboard_audit_passed", False),
        "repeatability_audit_passed": summary.get("repeatability_audit_passed", False),
        "gated_build_audit_passed": summary.get("gated_build_audit_passed", False),
        "business_output_drift_count": summary.get("business_output_drift_count"),
        "protected_path_modifications_detected": summary.get("protected_path_modifications_detected"),
        "automatic_action_count": summary.get("automatic_action_count"),
        "execute_remediation_actions": summary.get("execute_remediation_actions"),
        "external_notifications_sent": summary.get("external_notifications_sent"),
        "forbidden_decision_categories_detected": summary.get("forbidden_decision_categories_detected", []),
        "recommended_next_version": summary.get("recommended_next_version"),
        "daily_pack_report": str(artifacts["owner_daily_decision_pack_report"]),
    }


def _write_json(payloads: dict, artifacts: dict) -> None:
    for key, payload in payloads.items():
        path = artifacts.get(key)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_reports(artifacts: dict, as_of_date: str, payloads: dict, summary: dict) -> None:
    reports = {
        "owner_daily_decision_pack_report": render_decision_pack_report(as_of_date=as_of_date, payloads=payloads, summary=summary),
        "owner_daily_runbook_report": render_runbook_report(runbook=payloads["owner_daily_runbook"]),
        "owner_daily_status_brief_report": render_status_brief_report(status=payloads["owner_daily_status_brief"]),
        "owner_next_step_checklist_report": render_next_step_report(checklist=payloads["owner_next_step_checklist"]),
        "research_output_digest_report": render_research_digest_report(digest=payloads["research_output_digest"]),
        "owner_daily_pack_source_trace_report": render_source_trace_report(source_trace=payloads["daily_pack_source_trace"]),
    }
    for key, content in reports.items():
        path = artifacts[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

