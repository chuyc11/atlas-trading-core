"""Manifest and summary builders for current-day research runs."""

from __future__ import annotations

from typing import Any

from trading_core.equity_current_day.current_day_config import CURRENT_DAY_FLAGS, RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_current_day_run_manifest(
    *,
    as_of_date: str,
    resolved_as_of_date: str,
    generated_at: str,
    mode: str,
    workflow_mode: str,
    readiness: dict[str, Any],
    workflow_execution: dict[str, Any],
    warning_summary: dict[str, Any],
    source_trace: dict[str, Any],
    boundary: dict[str, Any],
    output_artifacts: dict[str, str],
    source_artifacts: dict[str, str],
) -> dict[str, Any]:
    blocking = sorted(
        set(
            readiness.get("blocking_reasons", [])
            + workflow_execution.get("blocking_reasons", [])
            + warning_summary.get("blocking_reasons", [])
            + source_trace.get("forbidden_path_hits", [])
            + boundary.get("blocking_reasons", [])
        )
    )
    warnings = sorted(
        set(
            readiness.get("warnings", [])
            + workflow_execution.get("warnings", [])
            + [row["warning"] for row in warning_summary.get("warnings", [])]
            + boundary.get("warnings", [])
        )
    )
    workflow_required = mode != "validate_current_day_readiness"
    workflow_passed = workflow_execution.get("workflow_audit_overall_passed") is True if workflow_required else True
    return {
        "manifest_id": "A-SHARE-CURRENT-DAY-RESEARCH-RUN-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "generated_at": generated_at,
        "mode": mode,
        "workflow_mode": workflow_mode,
        "data_refresh_audit_passed": readiness.get("data_refresh_audit_passed") is True,
        "workflow_audit_passed": workflow_passed,
        "overall_passed": not blocking and readiness.get("overall_passed") is True and workflow_passed and boundary.get("overall_passed") is True,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "output_artifacts": output_artifacts,
        "source_artifacts": source_artifacts,
        "boundary": dict(boundary),
        **CURRENT_DAY_FLAGS,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_current_day_summary(
    *,
    as_of_date: str,
    resolved_as_of_date: str,
    mode: str,
    workflow_mode: str,
    readiness: dict[str, Any],
    workflow_execution: dict[str, Any],
    stage_manifest: dict[str, Any],
    artifact_index: dict[str, Any],
    warning_summary: dict[str, Any],
    boundary: dict[str, Any],
    run_manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-CURRENT-DAY-RESEARCH-RUN-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "mode": mode,
        "workflow_mode": workflow_mode,
        "overall_passed": run_manifest.get("overall_passed") is True,
        "blocking_reasons": list(run_manifest.get("blocking_reasons", [])),
        "warnings": list(run_manifest.get("warnings", [])),
        "data_refresh_audit_passed": readiness.get("data_refresh_audit_passed") is True,
        "workflow_audit_passed": workflow_execution.get("workflow_audit_overall_passed") is True,
        "stage_status": {row["stage_id"]: row["status"] for row in stage_manifest.get("stages", [])},
        "key_artifacts": _key_artifacts(artifact_index),
        "warning_summary": warning_summary,
        "boundary": boundary,
        "disclaimer": "本产物仅用于研究工作流状态汇总，不是交易指令，不连接券商，不下真实订单。",
        **CURRENT_DAY_FLAGS,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _key_artifacts(index: dict[str, Any]) -> dict[str, str]:
    result = {}
    for row in index.get("artifacts", []):
        artifact_id = str(row.get("artifact_id"))
        if artifact_id in {
            "workflow_summary",
            "workflow_audit_json",
            "data_refresh_audit_json",
            "current_day_run_manifest",
            "current_day_summary_report",
        }:
            result[artifact_id] = str(row.get("path"))
    return result

