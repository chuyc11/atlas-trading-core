"""Builder for v0.8.10 build-output ops refresh."""

from __future__ import annotations

import json

from trading_core.equity_build_output_ops_refresh.artifact_navigation import build_artifact_navigation, source_paths
from trading_core.equity_build_output_ops_refresh.build_output_ops_boundary import build_boundary_check
from trading_core.equity_build_output_ops_refresh.build_output_ops_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    BUILD_REFRESH,
    DEFAULT_AS_OF_DATE,
    FILES,
    BuildOutputOpsRefreshConfig,
    artifact_paths,
    data_dir,
    validate_config,
)
from trading_core.equity_build_output_ops_refresh.build_output_ops_manifest import build_manifest, build_summary
from trading_core.equity_build_output_ops_refresh.build_output_ops_report import (
    render_comparison_report,
    render_monitoring_report,
    render_ops_center_report,
    render_ops_refresh_report,
    render_remediation_report,
    render_source_trace_report,
)
from trading_core.equity_build_output_ops_refresh.build_output_ops_source_trace import build_source_trace
from trading_core.equity_build_output_ops_refresh.date_alignment import build_date_alignment
from trading_core.equity_build_output_ops_refresh.health_score_refresh import build_health_score_refresh
from trading_core.equity_build_output_ops_refresh.input_availability import build_input_availability
from trading_core.equity_build_output_ops_refresh.issue_action_summary import build_action_summary_refresh, build_issue_summary_refresh
from trading_core.equity_build_output_ops_refresh.module_status_refresh import build_module_status_matrix_refresh
from trading_core.equity_build_output_ops_refresh.monitoring_refresh import build_alert_summary_refresh, build_monitoring_refresh
from trading_core.equity_build_output_ops_refresh.ops_center_refresh import build_ops_center_refresh
from trading_core.equity_build_output_ops_refresh.ops_comparison import build_ops_comparison
from trading_core.equity_build_output_ops_refresh.ops_history_refresh import build_ops_history_refresh
from trading_core.equity_build_output_ops_refresh.owner_next_steps import build_owner_next_steps_refresh
from trading_core.equity_build_output_ops_refresh.remediation_refresh import build_remediation_refresh, build_safe_action_refresh
from trading_core.equity_build_output_ops_refresh.source_resolution import build_source_resolution
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_build_output_ops_refresh_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict:
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-BUILD-OUTPUT-OPS-INPUT-VALIDATOR",
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": len(availability["warnings"]),
        "build_output_dashboard_audit_passed": availability["build_output_dashboard_audit_passed"],
        "repeatability_audit_passed": availability["repeatability_audit_passed"],
        "gated_build_audit_passed": availability["gated_build_audit_passed"],
        "original_monitoring_audit_passed": availability["original_monitoring_audit_passed"],
        "original_remediation_audit_passed": availability["original_remediation_audit_passed"],
        "original_ops_center_audit_passed": availability["original_ops_center_audit_passed"],
    }


def build_a_share_build_output_ops_refresh(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_REFRESH,
    allow_date_mismatch: bool = False,
    allow_business_output_drift: bool = False,
    paths: ProjectPaths | None = None,
) -> dict:
    paths = default_paths(paths)
    config = BuildOutputOpsRefreshConfig(
        as_of_date=as_of_date,
        mode=mode,
        allow_date_mismatch=allow_date_mismatch,
        allow_business_output_drift=allow_business_output_drift,
    )
    issues = validate_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of {ALLOWED_MODES}")
    if mode == AUDIT_EXISTING:
        raise ValueError("use audit-a-share-build-output-ops-refresh for audit_existing mode")

    artifacts = artifact_paths(paths, as_of_date)
    data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(
        as_of_date=as_of_date,
        input_availability=availability,
        allow_date_mismatch=allow_date_mismatch,
    )
    payloads = {
        "build_output_ops_refresh_config": config.to_dict(),
        "build_output_ops_input_availability": availability,
        "build_output_ops_source_resolution": resolution,
        "build_output_ops_date_alignment": alignment,
    }
    _write_json(payloads, artifacts)
    if mode in {"validate_build_output_ops_refresh_inputs", "resolve_build_output_ops_sources"}:
        return {
            "builder_id": "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-BUILDER",
            "overall_passed": availability.get("overall_passed", False) and resolution.get("overall_passed", False) and alignment.get("overall_passed", False),
            "blocking_reasons": availability.get("blocking_reasons", []) + resolution.get("blocking_reasons", []) + alignment.get("blocking_reasons", []),
            "warnings": len(availability.get("warnings", []) + resolution.get("warnings", []) + alignment.get("warnings", [])),
            "source_workflow_mode": "build_from_existing_data",
            "recommended_next_version": "v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack",
        }

    payloads.update(_build_refresh_payloads(paths, as_of_date))
    comparison = build_ops_comparison(paths=paths, as_of_date=as_of_date, refresh_payloads=payloads)
    payloads["original_ops_vs_build_output_ops_comparison"] = comparison
    payloads["build_output_ops_artifact_navigation"] = build_artifact_navigation(paths=paths, as_of_date=as_of_date)
    _write_json(payloads, artifacts)

    source_artifacts = source_paths(paths, as_of_date)
    output_artifacts = {key: value for key, value in artifacts.items() if key in FILES}
    source_trace = build_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        source_artifacts=source_artifacts,
        output_artifacts=output_artifacts,
        source_resolution=resolution,
    )
    payloads["build_output_ops_source_trace"] = source_trace
    boundary = build_boundary_check(paths=paths, as_of_date=as_of_date, payloads=payloads, source_resolution=resolution)
    payloads["build_output_ops_boundary_check"] = boundary
    manifest = build_manifest(
        as_of_date=as_of_date,
        mode=mode,
        payloads=payloads,
        source_trace=source_trace,
        boundary=boundary,
        output_artifacts=output_artifacts,
        source_artifacts=source_artifacts,
        paths=paths,
    )
    summary = build_summary(
        as_of_date=as_of_date,
        mode=mode,
        manifest=manifest,
        input_availability=availability,
        source_resolution=resolution,
        comparison=comparison,
    )
    payloads["build_output_ops_manifest"] = manifest
    payloads["build_output_ops_summary"] = summary
    _write_json(payloads, artifacts)
    _write_reports(artifacts, as_of_date, payloads, summary)
    return _builder_result(summary, artifacts)


def _build_refresh_payloads(paths: ProjectPaths, as_of_date: str) -> dict:
    monitoring = build_monitoring_refresh(paths=paths, as_of_date=as_of_date)
    alert = build_alert_summary_refresh(paths=paths, as_of_date=as_of_date, monitoring_refresh=monitoring)
    remediation = build_remediation_refresh(paths=paths, as_of_date=as_of_date)
    safe_action = build_safe_action_refresh(paths=paths, as_of_date=as_of_date)
    health = build_health_score_refresh(paths=paths, as_of_date=as_of_date)
    module = build_module_status_matrix_refresh(paths=paths, as_of_date=as_of_date)
    issue = build_issue_summary_refresh(paths=paths, as_of_date=as_of_date)
    action = build_action_summary_refresh(paths=paths, as_of_date=as_of_date, safe_action_refresh=safe_action)
    next_steps = build_owner_next_steps_refresh(paths=paths, as_of_date=as_of_date)
    ops_center = build_ops_center_refresh(
        paths=paths,
        as_of_date=as_of_date,
        health=health,
        module_matrix=module,
        issue_summary=issue,
        action_summary=action,
        owner_next_steps=next_steps,
    )
    ops_history = build_ops_history_refresh(paths=paths, as_of_date=as_of_date, ops_center_refresh=ops_center)
    return {
        "build_output_monitoring_refresh": monitoring,
        "build_output_alert_summary_refresh": alert,
        "build_output_remediation_refresh": remediation,
        "build_output_safe_action_refresh": safe_action,
        "build_output_ops_center_refresh": ops_center,
        "build_output_ops_history_refresh": ops_history,
        "build_output_health_score_refresh": health,
        "build_output_module_status_matrix_refresh": module,
        "build_output_issue_summary_refresh": issue,
        "build_output_action_summary_refresh": action,
        "build_output_owner_next_steps_refresh": next_steps,
    }


def _builder_result(summary: dict, artifacts: dict) -> dict:
    return {
        "builder_id": "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-BUILDER",
        "overall_passed": summary.get("overall_passed", False),
        "blocking_reasons": summary.get("blocking_reasons", []),
        "warnings": len(summary.get("warnings", [])),
        "source_workflow_mode": summary.get("source_workflow_mode"),
        "build_output_dashboard_audit_passed": summary.get("build_output_dashboard_audit_passed", False),
        "repeatability_audit_passed": summary.get("repeatability_audit_passed", False),
        "gated_build_audit_passed": summary.get("gated_build_audit_passed", False),
        "original_monitoring_audit_passed": summary.get("original_monitoring_audit_passed", False),
        "original_remediation_audit_passed": summary.get("original_remediation_audit_passed", False),
        "original_ops_center_audit_passed": summary.get("original_ops_center_audit_passed", False),
        "monitoring_refresh_performed": summary.get("monitoring_refresh_performed", False),
        "remediation_refresh_performed": summary.get("remediation_refresh_performed", False),
        "ops_center_refresh_performed": summary.get("ops_center_refresh_performed", False),
        "ops_history_refresh_performed": summary.get("ops_history_refresh_performed", False),
        "build_from_existing_data_rerun": summary.get("build_from_existing_data_rerun", True),
        "business_output_drift_count": summary.get("business_output_drift_count"),
        "protected_path_modifications_detected": summary.get("protected_path_modifications_detected"),
        "execute_remediation_actions": summary.get("execute_remediation_actions", True),
        "external_notifications_sent": summary.get("external_notifications_sent", True),
        "automatic_action_count": summary.get("automatic_action_count", 1),
        "comparison_completed": summary.get("comparison_completed", False),
        "ops_health_score": summary.get("ops_health_score"),
        "ops_health_grade": summary.get("ops_health_grade"),
        "overall_status": summary.get("overall_status"),
        "recommended_next_version": summary.get("recommended_next_version"),
        "ops_refresh_report": str(artifacts["build_output_ops_refresh_report"]),
    }


def _write_json(payloads: dict, artifacts: dict) -> None:
    for key, payload in payloads.items():
        path = artifacts.get(key)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_reports(artifacts: dict, as_of_date: str, payloads: dict, summary: dict) -> None:
    reports = {
        "build_output_ops_refresh_report": render_ops_refresh_report(as_of_date=as_of_date, payloads=payloads, summary=summary),
        "build_output_monitoring_refresh_report": render_monitoring_report(
            monitoring=payloads["build_output_monitoring_refresh"],
            alert=payloads["build_output_alert_summary_refresh"],
        ),
        "build_output_remediation_refresh_report": render_remediation_report(
            remediation=payloads["build_output_remediation_refresh"],
            safe_action=payloads["build_output_safe_action_refresh"],
        ),
        "build_output_ops_center_refresh_report": render_ops_center_report(
            ops_center=payloads["build_output_ops_center_refresh"],
            module_matrix=payloads["build_output_module_status_matrix_refresh"],
            issue=payloads["build_output_issue_summary_refresh"],
            action=payloads["build_output_action_summary_refresh"],
            next_steps=payloads["build_output_owner_next_steps_refresh"],
        ),
        "original_ops_vs_build_output_ops_report": render_comparison_report(
            comparison=payloads["original_ops_vs_build_output_ops_comparison"],
        ),
        "build_output_ops_source_trace_report": render_source_trace_report(
            source_trace=payloads["build_output_ops_source_trace"],
        ),
    }
    for key, content in reports.items():
        path = artifacts[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

