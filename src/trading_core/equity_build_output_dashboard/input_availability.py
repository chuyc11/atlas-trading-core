"""Input availability for build-output dashboard."""

from __future__ import annotations

import json
from pathlib import Path

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import (
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


REQUIRED_INPUTS = {
    "repeatability_audit": "data/equity_data_quality/a_share_build_repeatability_audit.json",
    "repeatability_summary": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_summary.json",
    "repeat_build_execution_record": "data/equity_build_repeatability/daily/{as_of_date}/repeat_build_execution_record.json",
    "build_vs_build_comparison": "data/equity_build_repeatability/daily/{as_of_date}/build_vs_build_comparison.json",
    "protected_path_modification_check": "data/equity_build_repeatability/daily/{as_of_date}/protected_path_modification_check.json",
    "repeatability_boundary_check": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_boundary_check.json",
    "gated_build_audit": "data/equity_data_quality/a_share_gated_build_from_existing_data_audit.json",
    "gated_build_summary": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_summary.json",
    "gated_build_execution_record": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_execution_record.json",
    "build_from_existing_data_workflow_result": "data/equity_current_day_builds/daily/{as_of_date}/build_from_existing_data_workflow_result.json",
    "build_artifact_index": "data/equity_current_day_builds/daily/{as_of_date}/build_artifact_index.json",
    "owner_dashboard_audit": "data/equity_data_quality/a_share_owner_dashboard_audit.json",
    "data_refresh_audit": "data/equity_data_quality/a_share_daily_data_refresh_audit.json",
    "data_refresh_summary": "data/equity_data_refresh/daily/{as_of_date}/data_refresh_summary.json",
}

OPTIONAL_INPUTS = {
    "validate_dashboard_manifest": "data/equity_owner_dashboard/daily/{as_of_date}/dashboard_manifest.json",
    "validate_dashboard_summary": "data/equity_owner_dashboard/daily/{as_of_date}/dashboard_summary.json",
    "validate_artifact_navigation": "data/equity_owner_dashboard/daily/{as_of_date}/artifact_navigation_index.json",
    "candidate_summary": "data/equity_selection/daily/{as_of_date}/candidate_generation_summary.json",
    "portfolio_manifest": "data/equity_portfolios/daily/{as_of_date}/portfolio_manifest.json",
    "benchmark_summary": "data/equity_benchmarks/daily/{as_of_date}/benchmark_summary.json",
    "performance_summary": "data/equity_performance/daily/{as_of_date}/performance_summary.json",
    "attribution_summary": "data/equity_attribution/daily/{as_of_date}/attribution_summary.json",
}


def build_input_availability(*, paths: ProjectPaths | None, as_of_date: str) -> dict:
    paths = default_paths(paths)
    entries = []
    payloads = {}
    blocking = []
    warnings = []
    for required, mapping in [(True, REQUIRED_INPUTS), (False, OPTIONAL_INPUTS)]:
        for artifact_id, template in mapping.items():
            path = paths.project_root / template.format(as_of_date=as_of_date)
            payload = _load(path)
            if payload:
                payloads[artifact_id] = payload
            if required and not path.exists():
                blocking.append(f"missing_required_input:{artifact_id}")
            if not required and not path.exists():
                warnings.append(f"optional_input_missing:{artifact_id}")
            entries.append({
                "artifact_id": artifact_id,
                "path": relative(path, paths.project_root),
                "exists": path.exists(),
                "required": required,
                "overall_passed": payload.get("overall_passed"),
                "workflow_mode": payload.get("workflow_mode"),
            })

    repeat_audit = payloads.get("repeatability_audit", {})
    gated_audit = payloads.get("gated_build_audit", {})
    owner_audit = payloads.get("owner_dashboard_audit", {})
    refresh_audit = payloads.get("data_refresh_audit", {})
    comparison = payloads.get("build_vs_build_comparison", {})
    protected = payloads.get("protected_path_modification_check", {})
    execution = payloads.get("repeat_build_execution_record", {})

    if repeat_audit.get("overall_passed") is not True:
        blocking.append("repeatability_audit_not_passed")
    if repeat_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("repeatability_recommended_next_version_mismatch")
    if gated_audit.get("overall_passed") is not True:
        blocking.append("gated_build_audit_not_passed")
    if owner_audit.get("overall_passed") is not True:
        blocking.append("validate_source_dashboard_audit_not_passed")
    if refresh_audit.get("overall_passed") is not True:
        blocking.append("data_refresh_audit_not_passed")
    if execution.get("workflow_mode") != "build_from_existing_data":
        blocking.append("repeat_build_workflow_mode_not_build_from_existing_data")
    if comparison.get("business_output_drift_count", 1) != 0:
        blocking.append("business_output_drift_count_nonzero")
    if protected.get("protected_path_modifications_detected", True) is not False:
        blocking.append("protected_path_modifications_detected")

    return {
        "availability_id": "A-SHARE-BUILD-OUTPUT-DASHBOARD-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
        "entries": entries,
        "repeatability_audit_passed": repeat_audit.get("overall_passed") is True,
        "gated_build_audit_passed": gated_audit.get("overall_passed") is True,
        "validate_source_dashboard_audit_passed": owner_audit.get("overall_passed") is True,
        "data_refresh_audit_passed": refresh_audit.get("overall_passed") is True,
        "business_output_drift_count": comparison.get("business_output_drift_count"),
        "protected_path_modifications_detected": protected.get("protected_path_modifications_detected"),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def load_json(path: Path) -> dict:
    return _load(path)


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}

