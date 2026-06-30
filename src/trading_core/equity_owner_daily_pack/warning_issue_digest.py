"""Warning and issue digest."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_warning_issue_digest(*, paths: ProjectPaths, as_of_date: str) -> dict:
    issue = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_issue_summary_refresh.json")
    warning = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_warning_and_blocker_card.json")
    return {
        "digest_id": "A-SHARE-WARNING-ISSUE-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "blocking_issues": issue.get("blocking_issues", []),
        "warning_issues": issue.get("warning_issues", []),
        "known_non_blocking_issues": issue.get("known_non_blocking_issues", []),
        "blocking_count": issue.get("blocking_issue_count", len(issue.get("blocking_issues", []))),
        "warning_count": issue.get("warning_issue_count", len(issue.get("warning_issues", []))),
        "build_output_warning_count": warning.get("warning_count", 0),
        "not_trade_instruction": True,
    }

