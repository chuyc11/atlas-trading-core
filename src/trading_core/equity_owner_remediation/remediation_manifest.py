"""Manifest and summary for owner remediation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_remediation.remediation_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_remediation_manifest(
    *,
    as_of_date: str,
    generated_at: str,
    mode: str,
    issue_catalog: dict[str, Any],
    priority_summary: dict[str, Any],
    checklist: dict[str, Any],
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-REMEDIATION-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "mode": mode,
        "issue_count": int(issue_catalog.get("issue_count", 0)),
        "blocking_issue_count": int(priority_summary.get("blocking_issue_count", 0)),
        "warning_issue_count": int(priority_summary.get("warning_issue_count", 0)),
        "known_non_blocking_issue_count": int(priority_summary.get("known_non_blocking_issue_count", 0)),
        "safe_action_count": int(checklist.get("safe_action_count", 0)),
        "automatic_action_count": int(checklist.get("automatic_action_count", 0)),
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_remediation_summary(*, as_of_date: str, mode: str, manifest: dict[str, Any], priority_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-REMEDIATION-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "issue_count": manifest.get("issue_count", 0),
        "blocking_issue_count": manifest.get("blocking_issue_count", 0),
        "warning_issue_count": manifest.get("warning_issue_count", 0),
        "known_non_blocking_issue_count": manifest.get("known_non_blocking_issue_count", 0),
        "safe_action_count": manifest.get("safe_action_count", 0),
        "automatic_action_count": manifest.get("automatic_action_count", 0),
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
        "priority_status": priority_summary.get("status"),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
