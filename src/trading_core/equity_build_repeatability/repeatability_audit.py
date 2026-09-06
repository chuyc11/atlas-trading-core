"""Audit for v0.8.8 build repeatability."""

from __future__ import annotations
from typing import Any

import hashlib
import json

from trading_core.equity_build_repeatability.repeatability_config import (
    RECOMMENDED_NEXT_VERSION,
    REPEATABILITY_BOUNDARY,
    REPEATABILITY_FILES,
    REPEATABILITY_REPORTS,
    TARGET_VERSION,
    repeatability_artifact_paths,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


def audit_a_share_build_repeatability(
    *,
    as_of_date: str,
    paths: ProjectPaths | None = None,
) -> dict:
    paths = default_paths(paths)
    artifact_paths = repeatability_artifact_paths(paths, as_of_date)
    payloads = {}
    for key, path in artifact_paths.items():
        if key.endswith("_json") or key.endswith("_report"):
            continue
        if path.exists() and path.suffix == ".json":
            try:
                payloads[key] = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                payloads[key] = {}
    checks = _checks(paths, as_of_date, artifact_paths, payloads)
    blocking = sorted(name for name, ok in checks.items() if not ok)
    protected = payloads.get("protected_path_modification_check", {})
    comparison = payloads.get("build_vs_build_comparison", {})
    execution = payloads.get("repeat_build_execution_record", {})
    boundary_payload = payloads.get("repeatability_boundary_check", {})
    audit: dict[str, Any] = {
        "audit_id": "A-SHARE-BUILD-REPEATABILITY-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": "run_repeat_build_from_existing_data",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "gated_build_audit_passed": checks.get("gated_build_audit_passed", False),
        },
        "execution_checks": {
            "workflow_mode": "build_from_existing_data",
            "repeat_build_execution_performed": execution.get("command_executed", False),
            "repeat_build_audit_passed": execution.get("workflow_audit_overall_passed", False),
            "old_run_daily_called": execution.get("old_run_daily_called", True),
        },
        "comparison_checks": {
            "comparison_completed": comparison.get("comparison_completed", False),
            "business_output_drift_count": comparison.get("business_output_drift_count", 0),
            "timestamp_only_drift_count": comparison.get("timestamp_only_drift_count", 0),
            "metadata_hash_drift_count": comparison.get("metadata_hash_drift_count", 0),
            "missing_required_artifact_count": comparison.get("missing_required_artifact_count", 0),
            "boundary_drift": comparison.get("boundary_drift", True),
            "protected_path_drift": protected.get("protected_path_modifications_detected", True),
            "source_trace_missing": not payloads.get("repeatability_source_trace", {}).get("source_trace_complete", False),
        },
        "protected_path_checks": {
            "preexisting_protected_paths_allowed": True,
            "protected_path_modifications_detected": protected.get("protected_path_modifications_detected", True),
            "new_protected_paths_created": protected.get("new_protected_paths_created", []),
            "protected_files_modified": protected.get("protected_files_modified", []),
            "protected_files_created": protected.get("protected_files_created", []),
            "protected_files_deleted": protected.get("protected_files_deleted", []),
        },
        "boundary": {**REPEATABILITY_BOUNDARY, **{k: boundary_payload.get(k, v) for k, v in REPEATABILITY_BOUNDARY.items()}},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json_markdown(
        artifact_paths["repeatability_audit_json"],
        audit,
        artifact_paths["repeatability_audit_report"],
        _render_audit(audit),
    )
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "execution_checks": audit["execution_checks"],
        "comparison_checks": audit["comparison_checks"],
        "protected_path_checks": audit["protected_path_checks"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifact_paths["repeatability_audit_json"]),
        "report_path": str(artifact_paths["repeatability_audit_report"]),
    }


def _checks(paths: ProjectPaths, as_of_date: str, artifact_paths: dict, payloads: dict) -> dict[str, bool]:
    checks = {}
    for key in REPEATABILITY_FILES:
        checks[f"{key}_present"] = artifact_paths[key].exists()
    for key in REPEATABILITY_REPORTS:
        checks[f"{key}_present"] = artifact_paths[key].exists()
    gated_audit = paths.data_dir / "equity_data_quality" / "a_share_gated_build_from_existing_data_audit.json"
    checks["gated_build_audit_passed"] = _load(gated_audit).get("overall_passed", False) is True

    execution = payloads.get("repeat_build_execution_record", {})
    checks["repeat_build_command_used_build_from_existing_data"] = execution.get("workflow_mode") == "build_from_existing_data"
    checks["repeat_build_execution_performed"] = execution.get("command_executed", False) is True
    checks["repeat_build_audit_passed"] = execution.get("workflow_audit_overall_passed", False) is True
    checks["no_old_run_daily_called"] = execution.get("old_run_daily_called", True) is False

    comparison = payloads.get("build_vs_build_comparison", {})
    checks["comparison_completed"] = comparison.get("comparison_completed", False) is True
    checks["missing_required_artifacts_absent"] = comparison.get("missing_required_artifact_count", 1) == 0
    checks["business_output_drift_absent"] = comparison.get("business_output_drift_count", 1) == 0
    checks["boundary_drift_absent"] = comparison.get("boundary_drift", True) is False
    checks["source_trace_drift_absent"] = comparison.get("source_trace_drift", True) is False

    protected = payloads.get("protected_path_modification_check", {})
    checks["protected_path_modification_absent"] = protected.get("protected_path_modifications_detected", True) is False
    checks["new_protected_paths_absent"] = not protected.get("new_protected_paths_created", [])
    checks["protected_files_modified_absent"] = not protected.get("protected_files_modified", [])
    checks["protected_files_created_absent"] = not protected.get("protected_files_created", [])
    checks["protected_files_deleted_absent"] = not protected.get("protected_files_deleted", [])

    source_trace = payloads.get("repeatability_source_trace", {})
    checks["source_trace_complete"] = source_trace.get("source_trace_complete", False) is True
    checks["source_trace_hashes_match"] = _source_trace_hashes_match(paths, source_trace)

    boundary = payloads.get("repeatability_boundary_check", {})
    checks["boundary_overall_passed"] = boundary.get("overall_passed", False) is True
    for key, expected in REPEATABILITY_BOUNDARY.items():
        checks[f"boundary_{key}"] = boundary.get(key) is expected
    checks["forbidden_artifacts_absent"] = not boundary.get("forbidden_artifacts_present", [])
    checks["forbidden_positive_wording_absent"] = not boundary.get("forbidden_wording_positive_hits", [])
    return checks


def _source_trace_hashes_match(paths: ProjectPaths, source_trace: dict) -> bool:
    entries = [e for e in source_trace.get("entries", []) if e.get("required") is True]
    if not entries:
        return False
    for entry in entries:
        recorded = entry.get("sha256")
        if not recorded:
            return False
        path = paths.project_root / entry.get("path", "")
        if not path.exists():
            return False
        if hashlib.sha256(path.read_bytes()).hexdigest() != recorded:
            return False
    return True


def _load(path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _render_audit(audit: dict) -> str:
    lines = [
        "# A 股 Build Repeatability Audit",
        "",
        f"- Audit ID: {audit['audit_id']}",
        f"- Target Version: {audit['target_version']}",
        f"- As-of Date: {audit['as_of_date']}",
        f"- Overall Passed: {audit['overall_passed']}",
        f"- Blocking Reasons: {audit['blocking_reasons']}",
        "",
        "## Input Checks",
        "",
    ]
    for key, value in audit["input_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Execution Checks", ""])
    for key, value in audit["execution_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Comparison Checks", ""])
    for key, value in audit["comparison_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Protected Path Checks", ""])
    for key, value in audit["protected_path_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Disclaimer", "", "本审计只验证研究产物重复性，不构成交易动作或投资建议。", ""])
    return "\n".join(lines)

