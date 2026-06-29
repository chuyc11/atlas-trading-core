"""Resolve build-output dashboard sources."""

from __future__ import annotations

from trading_core.equity_build_output_dashboard.input_availability import OPTIONAL_INPUTS, REQUIRED_INPUTS
from trading_core.equity_build_output_dashboard.build_output_dashboard_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_source_resolution(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    input_availability: dict,
    allow_required_validate_fallback: bool = False,
) -> dict:
    paths = default_paths(paths)
    required_map = {}
    optional_map = {}
    blocking = []
    warnings = []
    fallback_reasons = []
    required_validate_fallback_used = False
    optional_validate_fallback_used = False

    for artifact_id, template in REQUIRED_INPUTS.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        source_type = "build_output" if _is_build_output(artifact_id) else "supporting_input"
        if not path.exists():
            if allow_required_validate_fallback:
                required_validate_fallback_used = True
                fallback_reasons.append(f"required_fallback:{artifact_id}")
                warnings.append(f"required_validate_fallback_used:{artifact_id}")
            else:
                blocking.append(f"missing_required_build_output_artifact:{artifact_id}")
        required_map[artifact_id] = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "source_type": source_type,
            "source_workflow_mode": "build_from_existing_data" if source_type == "build_output" else "supporting",
            "fallback_used": False,
        }

    for artifact_id, template in OPTIONAL_INPUTS.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        fallback = not path.exists()
        if fallback:
            optional_validate_fallback_used = True
            fallback_reasons.append(f"optional_missing:{artifact_id}")
            warnings.append(f"optional_validate_fallback_recorded:{artifact_id}")
        optional_map[artifact_id] = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "source_type": "optional_build_output" if path.exists() else "optional_unavailable",
            "source_workflow_mode": "build_from_existing_data" if path.exists() else "unavailable",
            "fallback_used": fallback,
        }

    return {
        "resolution_id": "A-SHARE-BUILD-OUTPUT-SOURCE-RESOLUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "build_output_available": input_availability.get("overall_passed", False),
        "repeatability_audit_passed": input_availability.get("repeatability_audit_passed", False),
        "business_output_drift_count": input_availability.get("business_output_drift_count"),
        "protected_path_modifications_detected": input_availability.get("protected_path_modifications_detected"),
        "required_artifact_source_map": required_map,
        "optional_artifact_source_map": optional_map,
        "fallback_used": required_validate_fallback_used or optional_validate_fallback_used,
        "required_validate_fallback_used": required_validate_fallback_used,
        "optional_validate_fallback_used": optional_validate_fallback_used,
        "fallback_reasons": fallback_reasons,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
    }


def _is_build_output(artifact_id: str) -> bool:
    return artifact_id.startswith("repeat") or artifact_id in {
        "build_vs_build_comparison",
        "protected_path_modification_check",
        "gated_build_summary",
        "gated_build_execution_record",
        "build_from_existing_data_workflow_result",
        "build_artifact_index",
    }

