"""Source trace for A-share current-day research runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import FORBIDDEN_PATH_TOKENS, TARGET_VERSION
from trading_core.equity_data_quality.common import sha256_file
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_current_day_source_trace(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    resolved_as_of_date: str,
    generated_at: str,
    workflow_command: str,
    data_refresh_link: dict[str, Any],
    artifact_index: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    paths = default_paths(paths)
    source_artifacts = [
        _record(paths, paths.project_root / row["path"])
        for row in artifact_index.get("artifacts", [])
        if row.get("exists") and row.get("created_by_current_day_run") is False
    ]
    output_artifacts = [
        _record(paths, paths.project_root / row["path"])
        for row in artifact_index.get("artifacts", [])
        if row.get("created_by_current_day_run") is True
    ]
    forbidden_hits = forbidden_source_path_hits(source_artifacts + output_artifacts)
    return {
        "trace_id": "A-SHARE-CURRENT-DAY-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "generated_at": generated_at,
        "workflow_command": workflow_command,
        "data_refresh_audit_path": data_refresh_link.get("data_refresh_audit_path"),
        "source_artifacts": source_artifacts,
        "output_artifacts": output_artifacts,
        "warnings_carried_forward": list(warnings),
        "boundary_assumptions": [
            "current_day_research_run_only",
            "research_only",
            "virtual_only",
            "no_legacy_daily_runner",
            "no_broker_connection",
            "no_real_account_access",
            "no_real_order",
        ],
        "forbidden_path_hits": forbidden_hits,
        "source_trace_complete": not forbidden_hits and bool(source_artifacts),
    }


def forbidden_source_path_hits(records: list[dict[str, Any]]) -> list[str]:
    hits = []
    for record in records:
        path = str(record.get("path") or "").lower().replace("\\", "/")
        for token in FORBIDDEN_PATH_TOKENS:
            if token in path:
                hits.append(f"{record.get('path')}:{token}")
    return sorted(set(hits))


def _record(paths: ProjectPaths, path: Path) -> dict[str, Any]:
    return {
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }

