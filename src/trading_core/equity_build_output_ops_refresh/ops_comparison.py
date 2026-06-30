"""Compare original ops layer with build-output ops refresh."""

from __future__ import annotations

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import TARGET_VERSION
from trading_core.equity_build_output_ops_refresh.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_ops_comparison(*, paths: ProjectPaths, as_of_date: str, refresh_payloads: dict) -> dict:
    health = load_json(paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_health_score_card.json")
    action = load_json(paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_action_summary.json")
    issue = load_json(paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_issue_summary.json")
    boundary = load_json(paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_boundary_check.json")
    refreshed_health = refresh_payloads["build_output_health_score_refresh"]
    refreshed_action = refresh_payloads["build_output_action_summary_refresh"]
    refreshed_issue = refresh_payloads["build_output_issue_summary_refresh"]
    refreshed_boundary = refresh_payloads.get("build_output_ops_boundary_check", {})
    expected = ["source_workflow_mode:original_validate_to_build_output"]
    unexpected = []
    if health.get("score") != refreshed_health.get("score"):
        unexpected.append("health_score_changed")
    if action.get("automatic_action_count", 0) != refreshed_action.get("automatic_action_count", 0):
        unexpected.append("automatic_action_count_changed")
    if len(issue.get("blocking_issues", [])) != refreshed_issue.get("blocking_issue_count", 0):
        unexpected.append("blocking_issue_count_changed")
    if boundary.get("broker_connected") is True or refreshed_boundary.get("broker_connected") is True:
        unexpected.append("broker_boundary_changed")
    return {
        "comparison_id": "A-SHARE-ORIGINAL-OPS-VS-BUILD-OUTPUT-OPS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "comparison_completed": True,
        "original_source_workflow_mode": "validate_existing_artifacts",
        "build_output_source_workflow_mode": "build_from_existing_data",
        "original_health_score": health.get("score"),
        "build_output_health_score": refreshed_health.get("score"),
        "original_warning_issue_count": len(issue.get("warning_issues", [])),
        "build_output_warning_issue_count": refreshed_issue.get("warning_issue_count", 0),
        "original_automatic_action_count": action.get("automatic_action_count", 0),
        "build_output_automatic_action_count": refreshed_action.get("automatic_action_count", 0),
        "expected_source_mode_differences": expected,
        "unexpected_business_output_or_boundary_differences": unexpected,
        "overall_passed": not unexpected,
        "blocking_reasons": unexpected,
    }

