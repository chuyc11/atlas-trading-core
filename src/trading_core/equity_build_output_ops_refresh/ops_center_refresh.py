"""Ops center refresh sourced from build-output dashboard."""

from __future__ import annotations

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths


def build_ops_center_refresh(*, paths: ProjectPaths, as_of_date: str, health: dict, module_matrix: dict, issue_summary: dict, action_summary: dict, owner_next_steps: dict) -> dict:
    return {
        "refresh_id": "A-SHARE-BUILD-OUTPUT-OPS-CENTER-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "ops_center_refresh_performed": True,
        "health_score": health.get("score"),
        "health_grade": health.get("grade"),
        "overall_status": health.get("overall_status"),
        "module_count": len(module_matrix.get("rows", [])),
        "blocking_issue_count": len(issue_summary.get("blocking_issues", [])),
        "warning_issue_count": len(issue_summary.get("warning_issues", [])),
        "safe_action_count": action_summary.get("safe_action_count", 0),
        "automatic_action_count": action_summary.get("automatic_action_count", 0),
        "owner_next_steps_count": sum(len(owner_next_steps.get(key, [])) for key in ["do_now", "review_today", "wait_for_more_history", "developer_follow_up", "no_action_required"]),
        "aggregate_existing_artifacts_only": True,
        "build_from_existing_data_rerun": False,
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
    }

