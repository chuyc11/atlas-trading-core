"""Stage manifest for A-share current-day research runs."""

from __future__ import annotations

from typing import Any

from trading_core.equity_current_day.current_day_config import CURRENT_DAY_FLAGS, TARGET_VERSION


STAGE_DEFINITIONS = [
    ("stage_00_current_day_config", "current_day_config"),
    ("stage_01_data_refresh_readiness", "data_refresh_readiness"),
    ("stage_02_date_alignment", "date_alignment"),
    ("stage_03_workflow_plan", "workflow_plan"),
    ("stage_04_workflow_execution", "workflow_execution"),
    ("stage_05_workflow_audit_collection", "workflow_audit_collection"),
    ("stage_06_artifact_index", "artifact_index"),
    ("stage_07_warning_summary", "warning_summary"),
    ("stage_08_source_trace", "source_trace"),
    ("stage_09_boundary_check", "boundary_check"),
    ("stage_10_current_day_audit", "current_day_audit"),
    ("stage_11_owner_summary", "owner_summary"),
]


def build_current_day_stage_manifest(
    *,
    as_of_date: str,
    resolved_as_of_date: str,
    mode: str,
    workflow_mode: str,
    generated_at: str,
    artifact_paths: dict[str, str],
    readiness: dict[str, Any],
    workflow_execution: dict[str, Any],
    warnings: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    stages = []
    for index, (stage_id, stage_name) in enumerate(STAGE_DEFINITIONS):
        stage_blocking = []
        stage_warnings = []
        status = "passed"
        if stage_id == "stage_01_data_refresh_readiness":
            stage_blocking = list(readiness.get("blocking_reasons", []))
            stage_warnings = list(readiness.get("warnings", []))
            status = "passed" if readiness.get("overall_passed") else "failed"
        elif stage_id == "stage_04_workflow_execution":
            stage_blocking = list(workflow_execution.get("blocking_reasons", []))
            stage_warnings = list(workflow_execution.get("warnings", []))
            status = str(workflow_execution.get("status") or "not_run")
        elif stage_id == "stage_05_workflow_audit_collection":
            status = "passed" if workflow_execution.get("workflow_audit_overall_passed") else ("skipped" if workflow_execution.get("status") == "not_run" else "failed")
        elif stage_id in {"stage_07_warning_summary", "stage_08_source_trace", "stage_09_boundary_check"}:
            stage_warnings = list(warnings)
        elif stage_id == "stage_10_current_day_audit":
            status = "passed"
        elif stage_id == "stage_11_owner_summary":
            stage_warnings = list(warnings)
        stages.append(
            {
                "stage_id": stage_id,
                "stage_name": stage_name,
                "stage_order": index,
                "status": status,
                "started_at": generated_at,
                "finished_at": generated_at,
                "duration_seconds": 0.0,
                "input_artifacts": _stage_inputs(stage_id, artifact_paths),
                "output_artifacts": _stage_outputs(stage_id, artifact_paths),
                "audit_artifacts": _stage_audits(stage_id, artifact_paths),
                "blocking_reasons": stage_blocking,
                "warnings": stage_warnings,
            }
        )
    return {
        "manifest_id": "A-SHARE-CURRENT-DAY-STAGE-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "mode": mode,
        "workflow_mode": workflow_mode,
        "generated_at": generated_at,
        "stages": stages,
        "stage_count": len(stages),
        "blocking_reasons": list(blocking_reasons),
        "warnings": list(warnings),
        **CURRENT_DAY_FLAGS,
    }


def _stage_inputs(stage_id: str, paths: dict[str, str]) -> list[str]:
    if stage_id == "stage_01_data_refresh_readiness":
        return [paths.get("data_refresh_audit_json", "")]
    if stage_id == "stage_03_workflow_plan":
        return [paths.get("current_day_readiness", "")]
    if stage_id == "stage_04_workflow_execution":
        return [paths.get("current_day_workflow_plan", "")]
    if stage_id == "stage_10_current_day_audit":
        return [paths.get("current_day_run_manifest", "")]
    return []


def _stage_outputs(stage_id: str, paths: dict[str, str]) -> list[str]:
    mapping = {
        "stage_00_current_day_config": ["current_day_run_config"],
        "stage_01_data_refresh_readiness": ["current_day_readiness"],
        "stage_02_date_alignment": ["current_day_data_refresh_link"],
        "stage_03_workflow_plan": ["current_day_workflow_plan"],
        "stage_04_workflow_execution": ["current_day_workflow_execution"],
        "stage_06_artifact_index": ["current_day_artifact_index"],
        "stage_07_warning_summary": ["current_day_warning_summary"],
        "stage_08_source_trace": ["current_day_source_trace"],
        "stage_09_boundary_check": ["current_day_boundary_check"],
        "stage_11_owner_summary": ["current_day_summary", "current_day_summary_report"],
    }
    return [paths[key] for key in mapping.get(stage_id, []) if key in paths]


def _stage_audits(stage_id: str, paths: dict[str, str]) -> list[str]:
    if stage_id in {"stage_05_workflow_audit_collection", "stage_10_current_day_audit"}:
        return [item for item in [paths.get("workflow_audit_json", ""), paths.get("current_day_audit_json", "")] if item]
    return []

