"""Repeatability dashboard card."""

from __future__ import annotations

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import TARGET_VERSION


def build_repeatability_card(*, as_of_date: str, repeatability_audit: dict, comparison: dict) -> dict:
    return {
        "card_id": "BUILD_OUTPUT_REPEATABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "repeatability_audit_passed": repeatability_audit.get("overall_passed", False),
        "business_output_drift_count": comparison.get("business_output_drift_count", 0),
        "timestamp_only_drift_count": comparison.get("timestamp_only_drift_count", 0),
        "metadata_hash_drift_count": comparison.get("metadata_hash_drift_count", 0),
        "missing_required_artifact_count": comparison.get("missing_required_artifact_count", 0),
        "boundary_drift": comparison.get("boundary_drift", False),
        "protected_path_drift": comparison.get("protected_path_drift", False),
        "source_trace_missing": repeatability_audit.get("comparison_checks", {}).get("source_trace_missing", False),
    }

