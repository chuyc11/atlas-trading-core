"""Ops run record creation."""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_ops_history.ops_history_config import BASELINE_OPS_VERSION, TARGET_VERSION
from trading_core.system.common import relative
from trading_core.storage.file_paths import ProjectPaths


def build_ops_run_record(*, paths: ProjectPaths, as_of_date: str, payloads: dict[str, Any], input_paths: dict[str, Path]) -> dict[str, Any]:
    audit = payloads["ops_center_audit"]
    manifest = payloads["ops_manifest"]
    summary = payloads["ops_summary"]
    boundary = payloads["ops_boundary_check"]
    source_trace_path = input_paths["ops_source_trace"]
    manifest_path = input_paths["ops_manifest"]
    audit_path = input_paths["ops_center_audit"]
    return {
        "run_record_id": f"A-SHARE-OPS-RUN-{as_of_date}",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_version": BASELINE_OPS_VERSION,
        "ops_audit_passed": audit.get("overall_passed") is True,
        "ops_audit_path": relative(audit_path, paths.project_root),
        "ops_manifest_path": relative(manifest_path, paths.project_root),
        "ops_health_score": int(summary.get("ops_health_score", manifest.get("ops_health_score", 0))),
        "ops_health_grade": summary.get("ops_health_grade") or audit.get("manifest", {}).get("ops_health_grade"),
        "overall_status": summary.get("overall_status") or manifest.get("overall_status"),
        "blocking_issue_count": int(manifest.get("blocking_issue_count", 0)),
        "warning_issue_count": int(manifest.get("warning_issue_count", 0)),
        "known_non_blocking_issue_count": int(manifest.get("known_non_blocking_issue_count", 0)),
        "safe_action_count": int(manifest.get("safe_action_count", 0)),
        "automatic_action_count": int(manifest.get("automatic_action_count", 0)),
        "commands_executed": list(manifest.get("commands_executed", [])),
        "external_notifications_sent": audit.get("ops_checks", {}).get("external_notifications_sent") is True,
        "boundary_clean": boundary.get("overall_passed") is True,
        "source_trace_path": relative(source_trace_path, paths.project_root),
        "source_trace_sha256": sha256_file(source_trace_path),
        "manifest_sha256": sha256_file(manifest_path),
        "created_at": datetime.now(UTC).isoformat(),
    }
