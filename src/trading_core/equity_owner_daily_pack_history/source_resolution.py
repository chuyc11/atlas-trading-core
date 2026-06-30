"""Source resolution for owner daily pack history."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack_history.input_availability import REQUIRED_INPUTS, SUPPORTING_INPUTS
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_source_resolution(*, paths: ProjectPaths | None, as_of_date: str, input_availability: dict[str, Any]) -> dict[str, Any]:
    paths = default_paths(paths)
    primary = {}
    supporting = {}
    blocking = []
    for artifact_id, template in REQUIRED_INPUTS.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        primary[artifact_id] = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "source_role": "primary_owner_daily_pack",
            "fallback_used": False,
        }
        if not path.exists():
            blocking.append(f"missing_required_history_source:{artifact_id}")
    for artifact_id, template in SUPPORTING_INPUTS.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        supporting[artifact_id] = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "source_role": "supporting_build_output_evidence",
            "fallback_used": False,
        }
    return {
        "resolution_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-SOURCE-RESOLUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "owner_daily_pack_available": input_availability.get("owner_daily_pack_audit_passed", False),
        "primary_sources": primary,
        "supporting_sources": supporting,
        "fallback_used": False,
        "fallback_reasons": [],
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
    }
