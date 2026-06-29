"""Repeatability drift summary."""

from __future__ import annotations

from trading_core.equity_build_repeatability.repeatability_config import TARGET_VERSION


def build_repeatability_drift_summary(
    *,
    as_of_date: str,
    comparison: dict,
    protected_check: dict,
    allow_business_output_drift: bool = False,
) -> dict:
    blocking = list(comparison.get("blocking_reasons", []))
    if protected_check.get("protected_path_modifications_detected", False):
        blocking.append("protected_path_drift")
    if comparison.get("business_output_drift_count", 0) and not allow_business_output_drift:
        blocking.append("business_output_drift")
    return {
        "drift_summary_id": "A-SHARE-REPEATABILITY-DRIFT-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_status": "passed" if not blocking else "failed",
        "drift_categories_found": comparison.get("drift_categories_found", []),
        "timestamp_only_drift_count": comparison.get("timestamp_only_drift_count", 0),
        "metadata_hash_drift_count": comparison.get("metadata_hash_drift_count", 0),
        "business_output_drift_count": comparison.get("business_output_drift_count", 0),
        "missing_required_artifact_count": comparison.get("missing_required_artifact_count", 0),
        "boundary_drift": comparison.get("boundary_drift", False),
        "protected_path_drift": protected_check.get("protected_path_modifications_detected", False),
        "source_trace_drift": comparison.get("source_trace_drift", False),
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
    }

