"""Issue and action summary refresh for build-output ops."""

from __future__ import annotations

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import TARGET_VERSION
from trading_core.equity_build_output_ops_refresh.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_issue_summary_refresh(*, paths: ProjectPaths, as_of_date: str) -> dict:
    original = load_json(paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_issue_summary.json")
    return {
        "summary_id": "A-SHARE-BUILD-OUTPUT-ISSUE-SUMMARY-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "issue_summary_refresh_performed": True,
        "blocking_issues": original.get("blocking_issues", []),
        "warning_issues": original.get("warning_issues", []),
        "known_non_blocking_issues": original.get("known_non_blocking_issues", []),
        "blocking_issue_count": len(original.get("blocking_issues", [])),
        "warning_issue_count": len(original.get("warning_issues", [])),
    }


def build_action_summary_refresh(*, paths: ProjectPaths, as_of_date: str, safe_action_refresh: dict) -> dict:
    original = load_json(paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_action_summary.json")
    return {
        "summary_id": "A-SHARE-BUILD-OUTPUT-ACTION-SUMMARY-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "action_summary_refresh_performed": True,
        "safe_action_count": safe_action_refresh.get("safe_action_count", original.get("safe_action_count", 0)),
        "automatic_action_count": 0,
        "manual_review_count": safe_action_refresh.get("manual_review_count", original.get("manual_review_count", 0)),
        "top_owner_actions": original.get("top_owner_actions", []),
        "forbidden_action_hits": safe_action_refresh.get("forbidden_safe_action_type_hits", []),
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
    }

