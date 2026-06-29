"""Manifest and summary for repeatability."""

from __future__ import annotations

from datetime import UTC, datetime

from trading_core.equity_build_repeatability.repeatability_config import (
    RECOMMENDED_NEXT_VERSION,
    REPEATABILITY_FLAGS,
    TARGET_VERSION,
)
from trading_core.system.common import relative


def build_repeatability_manifest(
    *,
    as_of_date: str,
    mode: str,
    execution_record: dict,
    workflow_result: dict,
    comparison: dict,
    drift_summary: dict,
    protected_check: dict,
    source_trace: dict,
    boundary: dict,
    output_artifacts: dict,
    source_artifacts: dict,
    paths,
) -> dict:
    blocking = sorted(set(boundary.get("blocking_reasons", [])))
    return {
        "manifest_id": "A-SHARE-BUILD-REPEATABILITY-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "mode": mode,
        "workflow_mode": "build_from_existing_data",
        "repeat_build_execution_performed": execution_record.get("command_executed", False),
        "first_build_audit_passed": True,
        "second_build_audit_passed": workflow_result.get("workflow_audit_overall_passed", False),
        "comparison_completed": comparison.get("comparison_completed", False),
        "overall_repeatability_status": "passed" if not blocking else "failed",
        "business_output_drift_count": comparison.get("business_output_drift_count", 0),
        "timestamp_only_drift_count": comparison.get("timestamp_only_drift_count", 0),
        "metadata_hash_drift_count": comparison.get("metadata_hash_drift_count", 0),
        "missing_required_artifact_count": comparison.get("missing_required_artifact_count", 0),
        "boundary_drift": comparison.get("boundary_drift", False),
        "protected_path_drift": protected_check.get("protected_path_modifications_detected", False),
        "source_trace_missing": not source_trace.get("source_trace_complete", False),
        "blocking_reasons": blocking,
        "warnings": sorted(set(boundary.get("warnings", []))),
        "output_artifacts": {k: relative(v, paths.project_root) for k, v in output_artifacts.items()},
        "source_artifacts": {k: relative(v, paths.project_root) for k, v in source_artifacts.items()},
        "boundary": {k: boundary.get(k) for k in [
            "repeatability_only",
            "research_only",
            "virtual_only",
            "old_run_daily_called",
            "broker_connected",
            "real_orders_placed",
            "buy_sell_signals_generated",
            "order_preview_generated",
        ]},
        **REPEATABILITY_FLAGS,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_repeatability_summary(
    *,
    as_of_date: str,
    mode: str,
    manifest: dict,
    execution_record: dict,
    workflow_result: dict,
    comparison: dict,
    drift_summary: dict,
    protected_check: dict,
    boundary: dict,
) -> dict:
    return {
        "summary_id": "A-SHARE-BUILD-REPEATABILITY-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "workflow_mode": "build_from_existing_data",
        "overall_passed": boundary.get("overall_passed", False),
        "blocking_reasons": sorted(set(boundary.get("blocking_reasons", []))),
        "warnings": sorted(set(boundary.get("warnings", []))),
        "repeat_build_execution_performed": execution_record.get("command_executed", False),
        "repeat_build_audit_passed": workflow_result.get("workflow_audit_overall_passed", False),
        "comparison_completed": comparison.get("comparison_completed", False),
        "drift_status": drift_summary.get("overall_status", "unknown"),
        "protected_path_modifications_detected": protected_check.get("protected_path_modifications_detected", False),
        "business_output_drift_count": comparison.get("business_output_drift_count", 0),
        "timestamp_only_drift_count": comparison.get("timestamp_only_drift_count", 0),
        "metadata_hash_drift_count": comparison.get("metadata_hash_drift_count", 0),
        "missing_required_artifact_count": comparison.get("missing_required_artifact_count", 0),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

