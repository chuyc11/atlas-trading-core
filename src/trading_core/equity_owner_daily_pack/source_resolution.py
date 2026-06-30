"""Resolve sources for owner daily pack."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import REQUIRED_INPUTS
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_source_resolution(*, paths: ProjectPaths | None, as_of_date: str, input_availability: dict) -> dict:
    paths = default_paths(paths)
    primary_sources = {}
    supporting_sources = {}
    blocking = []
    for artifact_id, template in REQUIRED_INPUTS.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        role = "primary_build_output_ops_refresh" if artifact_id.startswith("build_output_ops") else "supporting_build_output_evidence"
        entry = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "source_role": role,
            "source_workflow_mode": "build_from_existing_data",
            "fallback_used": False,
        }
        if role == "primary_build_output_ops_refresh":
            primary_sources[artifact_id] = entry
        else:
            supporting_sources[artifact_id] = entry
        if not path.exists():
            blocking.append(f"missing_required_daily_pack_source:{artifact_id}")
    return {
        "resolution_id": "A-SHARE-OWNER-DAILY-PACK-SOURCE-RESOLUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "build_output_ops_refresh_available": input_availability.get("build_output_ops_refresh_audit_passed", False),
        "business_output_drift_count": input_availability.get("business_output_drift_count"),
        "protected_path_modifications_detected": input_availability.get("protected_path_modifications_detected"),
        "primary_sources": primary_sources,
        "supporting_sources": supporting_sources,
        "fallback_used": False,
        "fallback_reasons": [],
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
    }

