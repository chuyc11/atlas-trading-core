"""Manifest and summary for build-output dashboard."""

from __future__ import annotations

from datetime import UTC, datetime

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import (
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
)
from trading_core.system.common import relative


def build_manifest(
    *,
    as_of_date: str,
    mode: str,
    cards: dict,
    source_resolution: dict,
    source_trace: dict,
    boundary: dict,
    output_artifacts: dict,
    source_artifacts: dict,
    paths,
) -> dict:
    required_cards_present = all(cards.get(key) for key in [
        "build_output_executive_status_card",
        "build_output_data_freshness_card",
        "build_output_workflow_status_card",
        "build_output_research_output_card",
        "build_output_warning_and_blocker_card",
        "build_output_artifact_navigation",
    ])
    optional_cards_present = all(cards.get(key) for key in [
        "build_output_candidate_summary_card",
        "build_output_portfolio_summary_card",
        "build_output_benchmark_summary_card",
        "build_output_performance_summary_card",
        "build_output_attribution_summary_card",
        "build_output_repeatability_card",
        "build_output_protected_path_card",
    ])
    repeat = cards.get("build_output_repeatability_card", {})
    protected = cards.get("build_output_protected_path_card", {})
    return {
        "manifest_id": "A-SHARE-BUILD-OUTPUT-OWNER-DASHBOARD-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "mode": mode,
        "source_workflow_mode": "build_from_existing_data",
        "dashboard_refresh_performed": True,
        "gated_build_audit_passed": cards.get("build_output_executive_status_card", {}).get("gated_build_audit_passed", False),
        "repeatability_audit_passed": repeat.get("repeatability_audit_passed", False),
        "business_output_drift_count": repeat.get("business_output_drift_count", 0),
        "protected_path_modifications_detected": protected.get("protected_path_modifications_detected", True),
        "required_cards_present": required_cards_present,
        "optional_cards_present": optional_cards_present,
        "overall_status": cards.get("build_output_executive_status_card", {}).get("overall_status", "unknown"),
        "blocking_reasons": boundary.get("blocking_reasons", []),
        "warnings": boundary.get("warnings", []),
        "output_artifacts": {k: relative(v, paths.project_root) for k, v in output_artifacts.items()},
        "source_artifacts": {k: relative(v, paths.project_root) for k, v in source_artifacts.items()},
        "boundary": boundary,
        "source_trace_complete": source_trace.get("source_trace_complete", False),
        "required_validate_fallback_used": source_resolution.get("required_validate_fallback_used", False),
        "optional_validate_fallback_used": source_resolution.get("optional_validate_fallback_used", False),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_summary(*, as_of_date: str, mode: str, manifest: dict, cards: dict, comparison: dict) -> dict:
    repeat = cards.get("build_output_repeatability_card", {})
    protected = cards.get("build_output_protected_path_card", {})
    return {
        "summary_id": "A-SHARE-BUILD-OUTPUT-OWNER-DASHBOARD-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "source_workflow_mode": "build_from_existing_data",
        "overall_passed": not manifest.get("blocking_reasons", []),
        "overall_status": manifest.get("overall_status"),
        "blocking_reasons": manifest.get("blocking_reasons", []),
        "warnings": manifest.get("warnings", []),
        "gated_build_audit_passed": manifest.get("gated_build_audit_passed", False),
        "repeatability_audit_passed": manifest.get("repeatability_audit_passed", False),
        "business_output_drift_count": repeat.get("business_output_drift_count", 0),
        "protected_path_modifications_detected": protected.get("protected_path_modifications_detected", True),
        "required_cards_present": manifest.get("required_cards_present", False),
        "optional_cards_present": manifest.get("optional_cards_present", False),
        "required_validate_fallback_used": manifest.get("required_validate_fallback_used", False),
        "optional_validate_fallback_used": manifest.get("optional_validate_fallback_used", False),
        "comparison_completed": comparison.get("comparison_completed", False),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

