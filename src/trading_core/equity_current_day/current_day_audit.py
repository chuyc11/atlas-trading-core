"""Audit v0.8.1 A-share current-day research run artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import (
    CURRENT_DAY_BOUNDARY,
    CURRENT_DAY_FILES,
    DEFAULT_AS_OF_DATE,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
    current_day_artifact_paths,
)
from trading_core.equity_current_day.current_day_report import render_current_day_audit
from trading_core.equity_current_day.current_day_source_trace import forbidden_source_path_hits
from trading_core.equity_current_day.data_refresh_link import load_json
from trading_core.equity_data_quality.common import sha256_file, write_report
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_current_day_research_run(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = current_day_artifact_paths(paths, as_of_date)
    payloads = {key: load_json(artifacts[key]) for key in CURRENT_DAY_FILES}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads)
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    readiness = payloads["current_day_readiness"]
    execution = payloads["current_day_workflow_execution"]
    boundary = payloads["current_day_boundary_check"]
    manifest = payloads["current_day_run_manifest"]
    audit = {
        "audit_id": "A-SHARE-CURRENT-DAY-RESEARCH-RUN-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": manifest.get("resolved_as_of_date") or readiness.get("resolved_as_of_date"),
        "mode": manifest.get("mode"),
        "workflow_mode": manifest.get("workflow_mode"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": sorted(set(manifest.get("warnings", []) + readiness.get("warnings", []) + execution.get("warnings", []))),
        "readiness_checks": {
            "data_refresh_audit_passed": readiness.get("data_refresh_audit_passed") is True,
            "critical_datasets_passed": readiness.get("critical_datasets_passed") is True,
            "schema_validation_passed": readiness.get("schema_validation_passed") is True,
            "freshness_validation_passed": readiness.get("freshness_validation_passed") is True,
            "coverage_validation_passed": readiness.get("coverage_validation_passed") is True,
            "workflow_cli_available": readiness.get("workflow_cli_available") is True,
            "date_alignment_passed": readiness.get("checks", {}).get("resolved_as_of_date_matches_requested_date") is True,
        },
        "workflow_checks": {
            "workflow_execution_status": execution.get("status"),
            "workflow_audit_passed": execution.get("workflow_audit_overall_passed") is True,
            "old_run_daily_called": False,
        },
        "checks": checks,
        "boundary": {key: boundary.get(key) for key in CURRENT_DAY_BOUNDARY},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    return write_report(artifacts["current_day_audit_json"], audit, artifacts["current_day_audit_report"], render_current_day_audit(audit))


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    readiness = payloads["current_day_readiness"]
    link = payloads["current_day_data_refresh_link"]
    plan = payloads["current_day_workflow_plan"]
    execution = payloads["current_day_workflow_execution"]
    stage_manifest = payloads["current_day_stage_manifest"]
    artifact_index = payloads["current_day_artifact_index"]
    warning_summary = payloads["current_day_warning_summary"]
    source_trace = payloads["current_day_source_trace"]
    boundary = payloads["current_day_boundary_check"]
    manifest = payloads["current_day_run_manifest"]
    summary = payloads["current_day_summary"]
    stages = stage_manifest.get("stages", [])
    required_stage_ids = {
        "stage_00_current_day_config",
        "stage_01_data_refresh_readiness",
        "stage_02_date_alignment",
        "stage_03_workflow_plan",
        "stage_04_workflow_execution",
        "stage_05_workflow_audit_collection",
        "stage_06_artifact_index",
        "stage_07_warning_summary",
        "stage_08_source_trace",
        "stage_09_boundary_check",
        "stage_10_current_day_audit",
        "stage_11_owner_summary",
    }
    return {
        "current_day_run_config_exists": artifacts["current_day_run_config"].exists(),
        "current_day_readiness_exists": artifacts["current_day_readiness"].exists(),
        "current_day_data_refresh_link_exists": artifacts["current_day_data_refresh_link"].exists(),
        "current_day_workflow_plan_exists": artifacts["current_day_workflow_plan"].exists(),
        "current_day_workflow_execution_exists": artifacts["current_day_workflow_execution"].exists(),
        "current_day_stage_manifest_exists": artifacts["current_day_stage_manifest"].exists(),
        "current_day_artifact_index_exists": artifacts["current_day_artifact_index"].exists(),
        "current_day_warning_summary_exists": artifacts["current_day_warning_summary"].exists(),
        "current_day_source_trace_exists": artifacts["current_day_source_trace"].exists(),
        "current_day_boundary_check_exists": artifacts["current_day_boundary_check"].exists(),
        "current_day_run_manifest_exists": artifacts["current_day_run_manifest"].exists(),
        "current_day_summary_exists": artifacts["current_day_summary"].exists(),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload),
        "data_refresh_audit_passed": link.get("data_refresh_audit_passed") is True and readiness.get("data_refresh_audit_passed") is True,
        "data_refresh_blocking_reasons_empty": link.get("data_refresh_blocking_reasons") == [],
        "critical_datasets_passed": readiness.get("critical_datasets_passed") is True,
        "schema_validation_passed": readiness.get("schema_validation_passed") is True,
        "freshness_validation_passed": readiness.get("freshness_validation_passed") is True,
        "coverage_validation_passed": readiness.get("coverage_validation_passed") is True,
        "date_alignment_passed": readiness.get("checks", {}).get("resolved_as_of_date_matches_requested_date") is True,
        "workflow_command_does_not_call_old_run_daily": "run-daily" not in str(plan.get("workflow_command", "")) and "run_daily" not in str(plan.get("workflow_command", "")),
        "workflow_audit_passed": execution.get("workflow_audit_overall_passed") is True,
        "all_required_stages_present": {stage.get("stage_id") for stage in stages} == required_stage_ids,
        "artifact_index_generated": bool(artifact_index.get("artifacts")),
        "warning_summary_generated": "warnings" in warning_summary,
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, source_trace),
        "source_trace_has_no_forbidden_paths": not forbidden_source_path_hits(source_trace.get("source_artifacts", []) + source_trace.get("output_artifacts", [])),
        "known_warnings_carried_forward": set(link.get("data_refresh_warnings", [])).issubset(set(manifest.get("warnings", []))),
        "boundary_clean": boundary.get("overall_passed") is True and all(boundary.get(key) is expected for key, expected in CURRENT_DAY_BOUNDARY.items()),
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits"),
        "manifest_passed": manifest.get("overall_passed") is True,
        "summary_passed": summary.get("overall_passed") is True,
        "broker_not_connected": boundary.get("broker_connected") is False,
        "real_orders_not_placed": boundary.get("real_orders_placed") is False,
        "buy_sell_signals_not_generated": boundary.get("buy_sell_signals_generated") is False,
        "order_preview_not_generated": boundary.get("order_preview_generated") is False,
        "real_account_data_not_read": boundary.get("real_account_data_read") is False,
        "research_result_not_trade_instruction": boundary.get("research_result_used_as_trade_instruction") is False,
    }


def _source_hashes_match(paths: ProjectPaths, source_trace: dict[str, Any]) -> bool:
    for row in source_trace.get("source_artifacts", []):
        path = Path(str(row.get("path") or ""))
        if not path.is_absolute():
            path = paths.project_root / path
        if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
            return False
    return True

