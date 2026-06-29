"""Source trace for owner dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_dashboard.dashboard_config import FORBIDDEN_PATH_TOKENS, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_dashboard_source_trace(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    resolved_as_of_date: str,
    generated_at: str,
    source_paths: list[Path],
    output_paths: list[Path],
    warnings: list[str],
) -> dict[str, Any]:
    paths = default_paths(paths)
    source_records = [_record(paths, path) for path in source_paths]
    output_records = [_record(paths, path) for path in output_paths]
    hits = forbidden_source_path_hits(source_records + output_records)
    return {
        "trace_id": "A-SHARE-OWNER-DASHBOARD-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "generated_at": generated_at,
        "source_artifacts": source_records,
        "output_artifacts": output_records,
        "warning_carry_forward_decisions": list(warnings),
        "boundary_assumptions": ["owner_dashboard_only", "research_only", "virtual_only", "no_refresh", "no_workflow_rerun", "no_broker", "no_order"],
        "forbidden_path_hits": hits,
        "source_trace_complete": not hits and all(row["exists"] for row in source_records if _required_source(row["path"])),
    }


def forbidden_source_path_hits(records: list[dict[str, Any]]) -> list[str]:
    hits = []
    for row in records:
        path = str(row.get("path") or "").lower().replace("\\", "/")
        for token in FORBIDDEN_PATH_TOKENS:
            if token in path:
                hits.append(f"{row.get('path')}:{token}")
    return sorted(set(hits))


def _required_source(path: str) -> bool:
    return any(key in path for key in ["current_day", "data_refresh", "workflow", "briefing", "portfolio_tracking"])


def _record(paths: ProjectPaths, path: Path) -> dict[str, Any]:
    return {
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }

