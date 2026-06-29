"""Issue aggregation for the daily ops center."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_center.ops_config import TARGET_VERSION


def build_ops_issue_summary(*, as_of_date: str, payloads: dict[str, Any]) -> dict[str, Any]:
    remediation_manifest = payloads.get("remediation_manifest", {})
    issue_catalog = payloads.get("issue_catalog", {})
    non_actionable = payloads.get("non_actionable_issue_list", {})
    blocking_issues = [issue for issue in issue_catalog.get("issues", []) if issue.get("blocking")]
    warning_issues = [issue for issue in issue_catalog.get("issues", []) if issue.get("severity") == "warning"]
    known_issues = [issue for issue in issue_catalog.get("issues", []) if issue.get("known_non_blocking")]
    informational = [issue for issue in issue_catalog.get("issues", []) if issue.get("severity") == "informational"]
    return {
        "summary_id": "A-SHARE-DAILY-OPS-CENTER-ISSUE-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "blocking_issues": blocking_issues,
        "warning_issues": warning_issues,
        "known_non_blocking_issues": known_issues,
        "informational_issues": informational,
        "remediation_issues": issue_catalog.get("issues", []),
        "non_actionable_issues": non_actionable.get("items", []),
        "issue_count": int(remediation_manifest.get("issue_count", issue_catalog.get("issue_count", 0))),
        "blocking_issue_count": int(remediation_manifest.get("blocking_issue_count", len(blocking_issues))),
        "warning_issue_count": int(remediation_manifest.get("warning_issue_count", len(warning_issues))),
        "known_non_blocking_issue_count": int(remediation_manifest.get("known_non_blocking_issue_count", len(known_issues))),
    }
