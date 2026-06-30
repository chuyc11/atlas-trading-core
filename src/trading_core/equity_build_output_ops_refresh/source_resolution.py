"""Resolve build-output sources for ops refresh."""

from __future__ import annotations

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import TARGET_VERSION
from trading_core.equity_build_output_ops_refresh.input_availability import OPTIONAL_INPUTS, REQUIRED_INPUTS
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_source_resolution(*, paths: ProjectPaths | None, as_of_date: str, input_availability: dict) -> dict:
    paths = default_paths(paths)
    primary_sources = {}
    comparison_sources = {}
    fallback_sources = {}
    blocking = []
    warnings = []

    for artifact_id, template in REQUIRED_INPUTS.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        role = _source_role(artifact_id)
        entry = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "source_role": role,
            "source_workflow_mode": "build_from_existing_data" if role == "primary_build_output" else "comparison_only",
        }
        if role == "comparison_only":
            comparison_sources[artifact_id] = entry
        else:
            primary_sources[artifact_id] = entry
            if not path.exists():
                blocking.append(f"missing_required_build_output_source:{artifact_id}")

    for artifact_id, template in OPTIONAL_INPUTS.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        if not path.exists():
            warnings.append(f"optional_source_missing:{artifact_id}")
        fallback_sources[artifact_id] = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "source_role": "optional_context",
            "fallback_used": not path.exists(),
        }

    fallback_used = any(entry["fallback_used"] for entry in fallback_sources.values())
    return {
        "resolution_id": "A-SHARE-BUILD-OUTPUT-OPS-SOURCE-RESOLUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "build_output_dashboard_available": input_availability.get("build_output_dashboard_audit_passed", False),
        "repeatability_audit_passed": input_availability.get("repeatability_audit_passed", False),
        "gated_build_audit_passed": input_availability.get("gated_build_audit_passed", False),
        "build_output_dashboard_audit_passed": input_availability.get("build_output_dashboard_audit_passed", False),
        "business_output_drift_count": input_availability.get("business_output_drift_count"),
        "protected_path_modifications_detected": input_availability.get("protected_path_modifications_detected"),
        "primary_sources": primary_sources,
        "comparison_sources": comparison_sources,
        "fallback_sources": fallback_sources,
        "fallback_used": fallback_used,
        "fallback_reasons": [f"optional_missing:{key}" for key, value in fallback_sources.items() if value["fallback_used"]],
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings + (["fallback_used_for_optional_context"] if fallback_used else []))),
    }


def _source_role(artifact_id: str) -> str:
    if artifact_id.startswith(("build_output_", "repeatability", "protected_path", "gated_build", "build_from_existing")):
        return "primary_build_output"
    return "comparison_only"

