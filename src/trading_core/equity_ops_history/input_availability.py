"""Input availability for ops history baselines."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_ops_center.ops_config import ops_artifact_paths
from trading_core.equity_ops_history.ops_history_config import BASELINE_OPS_VERSION, TARGET_VERSION
from trading_core.equity_owner_monitoring.monitoring_config import monitoring_artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def ops_history_input_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ops = ops_artifact_paths(paths, as_of_date)
    monitoring = monitoring_artifact_paths(paths, as_of_date)
    return {
        "ops_center_audit": ops["ops_audit_json"],
        "ops_center_config": ops["ops_center_config"],
        "ops_input_availability": ops["ops_input_availability"],
        "ops_date_alignment": ops["ops_date_alignment"],
        "ops_execution_record": ops["ops_execution_record"],
        "ops_health_score_card": ops["ops_health_score_card"],
        "ops_module_status_matrix": ops["ops_module_status_matrix"],
        "ops_issue_summary": ops["ops_issue_summary"],
        "ops_action_summary": ops["ops_action_summary"],
        "ops_artifact_navigation": ops["ops_artifact_navigation"],
        "ops_source_trace": ops["ops_source_trace"],
        "ops_boundary_check": ops["ops_boundary_check"],
        "ops_manifest": ops["ops_manifest"],
        "ops_summary": ops["ops_summary"],
        "monitoring_run_history_index": monitoring["run_history_index"],
        "monitoring_warning_history_index": monitoring["warning_history_index"],
        "monitoring_blocking_history_index": monitoring["blocking_history_index"],
        "monitoring_alert_history_index": monitoring["alert_history_index"],
    }


def build_ops_history_input_availability(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    input_paths = ops_history_input_paths(paths, as_of_date)
    records = [_record(paths, key, path, required=not key.startswith("monitoring_")) for key, path in input_paths.items()]
    missing = [row["artifact_id"] for row in records if row["required"] and not row["exists"]]
    audit = load_json(input_paths["ops_center_audit"])
    boundary = load_json(input_paths["ops_boundary_check"])
    source_trace = load_json(input_paths["ops_source_trace"])
    audit_passed = audit.get("overall_passed") is True
    blocking = [f"{item}_missing" for item in missing]
    if not audit_passed:
        blocking.append("ops_center_audit_passed=false")
    if audit.get("target_version") != BASELINE_OPS_VERSION:
        blocking.append("ops_center_target_version_unexpected")
    if audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("ops_center_recommended_next_version_unexpected")
    if boundary.get("overall_passed") is not True:
        blocking.append("ops_center_boundary_clean=false")
    if source_trace.get("source_trace_complete") is not True:
        blocking.append("ops_center_source_trace_complete=false")
    return {
        "availability_id": "A-SHARE-OPS-HISTORY-BASELINE-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "input_artifacts": records,
        "input_audit_checks": {"ops_center_audit_passed": audit_passed},
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "boundary_clean": boundary.get("overall_passed") is True,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
    }


def _record(paths: ProjectPaths, artifact_id: str, path: Path, *, required: bool) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "required": required,
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }
