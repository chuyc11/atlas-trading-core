"""Warning recurrence baseline."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_history.ops_history_config import TARGET_VERSION


def build_ops_warning_recurrence_baseline(*, as_of_date: str, issue_summary: dict[str, Any], records: list[dict[str, Any]], minimum_required_observations: int) -> dict[str, Any]:
    enough = len(records) >= minimum_required_observations
    items = []
    for issue in issue_summary.get("warning_issues", []) + issue_summary.get("known_non_blocking_issues", []):
        code = issue.get("issue_code")
        items.append(
            {
                "warning_code": code,
                "first_seen_date": as_of_date,
                "last_seen_date": as_of_date,
                "seen_count": 1,
                "severity": issue.get("severity"),
                "source_module": issue.get("source_stage", "owner_remediation"),
                "known_non_blocking": issue.get("known_non_blocking") is True,
                "recurrence_status": "known_non_blocking" if issue.get("known_non_blocking") else ("new" if not enough else "insufficient_history"),
                "owner_action_status": "document_and_monitor",
            }
        )
    return {"baseline_id": "A-SHARE-OPS-WARNING-RECURRENCE-BASELINE", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "items": items}
