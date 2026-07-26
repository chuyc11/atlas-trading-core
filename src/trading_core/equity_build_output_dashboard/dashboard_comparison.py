"""Compare validate-source dashboard with build-output dashboard."""

from __future__ import annotations

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import TARGET_VERSION
from trading_core.equity_build_output_dashboard.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_dashboard_comparison(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    build_cards: dict,
    source_resolution: dict,
) -> dict:
    paths = default_paths(paths)
    validate_summary = load_json(paths.data_dir / "equity_owner_dashboard" / "daily" / as_of_date / "dashboard_summary.json")
    validate_boundary = load_json(paths.data_dir / "equity_owner_dashboard" / "daily" / as_of_date / "dashboard_boundary_check.json")
    build_warning = build_cards.get("build_output_warning_and_blocker_card", {})
    _build_boundary = build_cards.get("build_output_dashboard_boundary_check", {})
    unexpected = []
    if build_warning.get("blocking_count", 0):
        unexpected.append("build_dashboard_has_blocking_reasons")
    return {
        "comparison_id": "A-SHARE-VALIDATE-DASHBOARD-VS-BUILD-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "comparison_completed": True,
        "expected_source_mode_difference": {
            "validate_dashboard_source_workflow_mode": validate_summary.get("source_workflow_mode", "validate_existing_artifacts"),
            "build_dashboard_source_workflow_mode": "build_from_existing_data",
            "expected_different": True,
        },
        "overall_status_comparison": {
            "validate_overall_passed": validate_summary.get("overall_passed", validate_boundary.get("overall_passed")),
            "build_overall_passed": build_warning.get("overall_passed", False),
        },
        "warning_count_comparison": {
            "validate_warning_count": len(validate_summary.get("warnings", [])),
            "build_warning_count": build_warning.get("warning_count", 0),
        },
        "artifact_navigation_comparison": {
            "build_navigation_available": bool(build_cards.get("build_output_artifact_navigation")),
            "required_validate_fallback_used": source_resolution.get("required_validate_fallback_used", False),
            "optional_validate_fallback_used": source_resolution.get("optional_validate_fallback_used", False),
        },
        "availability_comparison": {
            "candidate_available": build_cards.get("build_output_candidate_summary_card", {}).get("available", False),
            "portfolio_available": build_cards.get("build_output_portfolio_summary_card", {}).get("available", False),
            "benchmark_available": build_cards.get("build_output_benchmark_summary_card", {}).get("available", False),
            "performance_available": build_cards.get("build_output_performance_summary_card", {}).get("available", False),
            "attribution_available": build_cards.get("build_output_attribution_summary_card", {}).get("available", False),
        },
        "unexpected_business_output_differences": unexpected,
        "blocking_reasons": unexpected,
        "warnings": ["source_mode_changed_to_build_from_existing_data"],
    }
