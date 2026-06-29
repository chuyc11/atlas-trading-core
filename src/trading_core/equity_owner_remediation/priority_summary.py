"""Remediation priority summary."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_remediation.remediation_config import TARGET_VERSION


PRIORITIES = ["P0_blocking", "P1_high_warning", "P2_known_non_blocking", "P3_informational", "P4_wait_for_history"]


def build_remediation_priority_summary(*, as_of_date: str, issue_catalog: dict[str, Any]) -> dict[str, Any]:
    buckets = {priority: [] for priority in PRIORITIES}
    for issue in issue_catalog.get("issues", []):
        priority = _priority(issue)
        buckets[priority].append(issue["issue_code"])
    issue_count = int(issue_catalog.get("issue_count", 0))
    return {
        "summary_id": "A-SHARE-OWNER-REMEDIATION-PRIORITY-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "status": "no_action_required" if issue_count == 0 else "manual_review_required",
        "priority_buckets": buckets,
        "issue_count": issue_count,
        "blocking_issue_count": len(buckets["P0_blocking"]),
        "warning_issue_count": len(buckets["P1_high_warning"]),
        "known_non_blocking_issue_count": len(buckets["P2_known_non_blocking"]),
        "wait_for_history_issue_count": len(buckets["P4_wait_for_history"]),
    }


def _priority(issue: dict[str, Any]) -> str:
    code = str(issue.get("issue_code", "")).lower()
    category = issue.get("category")
    if issue.get("blocking") or category == "boundary_issue":
        return "P0_blocking"
    if category == "insufficient_history_issue" or "insufficient_history" in code:
        return "P4_wait_for_history"
    if issue.get("known_non_blocking"):
        return "P2_known_non_blocking"
    if issue.get("severity") == "warning":
        return "P1_high_warning"
    return "P3_informational"
