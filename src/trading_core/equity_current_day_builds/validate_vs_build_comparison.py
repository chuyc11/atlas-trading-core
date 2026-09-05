"""Validate vs build comparison for v0.8.7 gated build."""

from __future__ import annotations

import json

from trading_core.equity_current_day_builds.gated_build_config import (
    TARGET_VERSION,
    FROM_WORKFLOW_MODE,
    TO_WORKFLOW_MODE,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths
import contextlib


def build_validate_vs_build_comparison(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    validate_snapshot: dict | None = None,
) -> dict:
    paths = default_paths(paths)
    validate_snapshot = validate_snapshot or {}

    # Load validate_existing_artifacts manifest (the v0.8.1 baseline run)
    validate_manifest_path = (
        paths.data_dir
        / "equity_current_day_runs"
        / "daily"
        / as_of_date
        / "current_day_run_manifest.json"
    )

    # Load build_from_existing_data workflow execution
    build_execution_path = (
        paths.data_dir
        / "equity_current_day_runs"
        / "daily"
        / as_of_date
        / "current_day_workflow_execution.json"
    )

    # Load boundary checks
    validate_boundary_path = (
        paths.data_dir
        / "equity_current_day_runs"
        / "daily"
        / as_of_date
        / "current_day_boundary_check.json"
    )

    # Load artifact indexes
    validate_artifact_index_path = (
        paths.data_dir
        / "equity_current_day_runs"
        / "daily"
        / as_of_date
        / "current_day_artifact_index.json"
    )

    validate_manifest = dict(validate_snapshot.get("current_day_run_manifest", {}))
    build_execution = {}
    validate_boundary = dict(validate_snapshot.get("current_day_boundary_check", {}))
    build_boundary = {}
    validate_artifact_index = dict(validate_snapshot.get("current_day_artifact_index", {}))
    build_artifact_index = {}

    if not validate_manifest and validate_manifest_path.exists():
        with contextlib.suppress(Exception):
            validate_manifest = json.loads(validate_manifest_path.read_text(encoding="utf-8"))

    if build_execution_path.exists():
        with contextlib.suppress(Exception):
            build_execution = json.loads(build_execution_path.read_text(encoding="utf-8"))

    if not validate_boundary and validate_boundary_path.exists():
        with contextlib.suppress(Exception):
            validate_boundary = json.loads(validate_boundary_path.read_text(encoding="utf-8"))

    if validate_boundary_path.exists():
        with contextlib.suppress(Exception):
            build_boundary = json.loads(validate_boundary_path.read_text(encoding="utf-8"))

    if validate_artifact_index_path.exists():
        with contextlib.suppress(Exception):
            build_artifact_index = json.loads(validate_artifact_index_path.read_text(encoding="utf-8"))

    # Compare key fields
    comparisons = {
        "workflow_mode_difference": {
            "validate_mode": FROM_WORKFLOW_MODE,
            "build_mode": TO_WORKFLOW_MODE,
            "expected_different": True,
        },
        "audit_status_comparison": {
            "validate_audit_passed": validate_manifest.get("overall_passed", False),
            "build_exit_code": build_execution.get("exit_code", None),
            "build_status": build_execution.get("status", None),
        },
        "boundary_comparison": {
            "validate_boundary_passed": validate_boundary.get("overall_passed", False),
            "build_boundary_passed": build_boundary.get("overall_passed", False),
        },
        "artifact_count_comparison": {
            "validate_artifact_count": validate_artifact_index.get("artifact_count", 0),
            "build_artifact_count": build_artifact_index.get("artifact_count", 0),
        },
    }

    # Check for drift
    blocking = []
    warnings = []

    if build_boundary.get("overall_passed") is False:
        blocking.append("build_boundary_failed")

    if build_execution.get("exit_code", -1) != 0:
        warnings.append("build_exit_code_nonzero")

    missing_required_artifacts = []
    for artifact_id in ["current_day_run_manifest", "current_day_boundary_check", "current_day_artifact_index"]:
        path = paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date / f"{artifact_id}.json"
        if not path.exists():
            missing_required_artifacts.append(artifact_id)
            blocking.append(f"missing_required_artifact:{artifact_id}")

    business_output_drift = []
    if validate_manifest.get("overall_passed") is True and build_execution.get("status") not in {"passed", None}:
        business_output_drift.append(
            {
                "field": "workflow_status",
                "validate": "overall_passed",
                "build": build_execution.get("status"),
            }
        )

    return {
        "comparison_id": "A-SHARE-VALIDATE-VS-BUILD-COMPARISON",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "from_workflow_mode": FROM_WORKFLOW_MODE,
        "to_workflow_mode": TO_WORKFLOW_MODE,
        "comparisons": comparisons,
        "blocking_reasons": sorted(blocking),
        "warnings": sorted(warnings),
        "comparison_completed": True,
        "business_output_drift": business_output_drift,
        "timestamp_only_drift": [],
        "hash_only_drift": [],
        "missing_required_artifacts": missing_required_artifacts,
        "new_artifacts": [],
    }
