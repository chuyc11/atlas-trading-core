"""Manifest and summary for the daily ops center."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_ops_center.ops_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_ops_manifest(
    *,
    as_of_date: str,
    generated_at: str,
    mode: str,
    health_score: dict[str, Any],
    issue_summary: dict[str, Any],
    action_summary: dict[str, Any],
    execution_record: dict[str, Any],
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-DAILY-OPS-CENTER-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "mode": mode,
        "overall_status": health_score.get("overall_status"),
        "ops_health_score": health_score.get("score"),
        "required_modules_passed": health_score.get("required_modules_passed"),
        "blocking_issue_count": issue_summary.get("blocking_issue_count", 0),
        "warning_issue_count": issue_summary.get("warning_issue_count", 0),
        "known_non_blocking_issue_count": issue_summary.get("known_non_blocking_issue_count", 0),
        "safe_action_count": action_summary.get("safe_action_count", 0),
        "automatic_action_count": action_summary.get("automatic_action_count", 0),
        "commands_executed": execution_record.get("commands_executed", []),
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_ops_summary(*, as_of_date: str, mode: str, manifest: dict[str, Any], health_score: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-DAILY-OPS-CENTER-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "overall_status": manifest.get("overall_status"),
        "ops_health_score": health_score.get("score"),
        "ops_health_grade": health_score.get("grade"),
        "required_modules_passed": manifest.get("required_modules_passed"),
        "blocking_issue_count": manifest.get("blocking_issue_count"),
        "warning_issue_count": manifest.get("warning_issue_count"),
        "known_non_blocking_issue_count": manifest.get("known_non_blocking_issue_count"),
        "safe_action_count": manifest.get("safe_action_count"),
        "automatic_action_count": manifest.get("automatic_action_count"),
        "commands_executed": manifest.get("commands_executed", []),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
