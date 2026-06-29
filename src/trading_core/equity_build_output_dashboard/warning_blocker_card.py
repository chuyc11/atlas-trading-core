"""Warning and blocker card for build-output dashboard."""

from __future__ import annotations

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import TARGET_VERSION


def build_warning_and_blocker_card(*, as_of_date: str, cards: dict, availability: dict, resolution: dict) -> dict:
    blocking = []
    warnings = []
    blocking.extend(availability.get("blocking_reasons", []))
    blocking.extend(resolution.get("blocking_reasons", []))
    warnings.extend(availability.get("warnings", []))
    warnings.extend(resolution.get("warnings", []))
    repeat = cards.get("build_output_repeatability_card", {})
    if repeat.get("business_output_drift_count", 0):
        blocking.append("business_output_drift_count_nonzero")
    if repeat.get("timestamp_only_drift_count", 0):
        warnings.append("timestamp_only_drift_non_blocking")
    if repeat.get("metadata_hash_drift_count", 0):
        warnings.append("metadata_hash_drift_non_blocking")
    protected = cards.get("build_output_protected_path_card", {})
    if protected.get("protected_path_modifications_detected", False):
        blocking.append("protected_path_modifications_detected")
    return {
        "card_id": "BUILD_OUTPUT_WARNING_AND_BLOCKER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "overall_passed": not blocking,
        "blocking_count": len(set(blocking)),
        "warning_count": len(set(warnings)),
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
        "timestamp_and_metadata_drift_non_blocking": True,
    }

