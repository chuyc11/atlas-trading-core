"""Manifest for v0.8.7 gated build."""

from __future__ import annotations

from datetime import UTC, datetime

from trading_core.equity_current_day_builds.gated_build_config import (
    GATED_BUILD_FLAGS,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
)
from trading_core.system.common import relative


def build_gated_build_manifest(
    *,
    as_of_date: str,
    mode: str,
    preflight_gate: dict,
    execution_record: dict,
    workflow_result: dict,
    comparison: dict,
    drift_summary: dict,
    boundary: dict,
    output_artifacts: dict,
    source_artifacts: dict,
    paths,
) -> dict:
    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    return {
        "manifest_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "mode": mode,
        "workflow_mode": "build_from_existing_data",
        "preflight_gate_passed": preflight_gate.get("overall_passed", False),
        "gated_build_execution_performed": execution_record.get("command_executed", False),
        "workflow_audit_passed": workflow_result.get("workflow_audit_overall_passed", False),
        "comparison_completed": comparison.get("comparison_completed", False),
        "blocking_reasons": sorted(set(boundary.get("blocking_reasons", []))),
        "warnings": sorted(set(boundary.get("warnings", []))),
        "output_artifacts": {
            key: relative(path, paths.project_root) for key, path in output_artifacts.items()
        },
        "source_artifacts": {
            key: relative(path, paths.project_root) for key, path in source_artifacts.items()
        },
        "boundary": {
            "overall_passed": boundary.get("overall_passed", False),
            "gated_build_from_existing_data_only": True,
            "research_only": True,
            "virtual_only": True,
            "old_run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
        },
        **GATED_BUILD_FLAGS,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_gated_build_summary(
    *,
    as_of_date: str,
    mode: str,
    manifest: dict,
    preflight_gate: dict,
    execution_record: dict,
    workflow_result: dict,
    comparison: dict,
    drift_summary: dict,
    boundary: dict,
) -> dict:
    return {
        "summary_id": "A-SHARE-GATED-BUILD-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "workflow_mode": "build_from_existing_data",
        "overall_passed": boundary.get("overall_passed", False),
        "blocking_reasons": sorted(set(boundary.get("blocking_reasons", []))),
        "warnings": sorted(set(boundary.get("warnings", []))),
        "preflight_gate_passed": preflight_gate.get("overall_passed", False),
        "gated_build_execution_performed": execution_record.get("command_executed", False),
        "workflow_status": execution_record.get("status", "unknown"),
        "workflow_audit_passed": workflow_result.get("workflow_audit_overall_passed", False),
        "comparison_completed": comparison.get("comparison_completed", False),
        "drift_status": drift_summary.get("overall_status", "unknown"),
        "exit_code": execution_record.get("exit_code"),
        "duration_seconds": execution_record.get("duration_seconds"),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
