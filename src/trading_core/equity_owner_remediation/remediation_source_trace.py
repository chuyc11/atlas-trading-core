"""Source trace for owner remediation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_remediation.remediation_config import FORBIDDEN_PATH_TOKENS, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_remediation_source_trace(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    generated_at: str,
    source_paths: list[Path],
    output_paths: list[Path],
    issue_catalog: dict[str, Any],
) -> dict[str, Any]:
    paths = default_paths(paths)
    source_records = [_record(paths, path) for path in source_paths]
    output_records = [_record(paths, path) for path in output_paths]
    hits = forbidden_source_path_hits(source_records + output_records)
    return {
        "trace_id": "A-SHARE-OWNER-REMEDIATION-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "source_artifacts": source_records,
        "output_artifacts": output_records,
        "issue_catalog_sources": sorted({issue.get("source_artifact") for issue in issue_catalog.get("issues", []) if issue.get("source_artifact")}),
        "boundary_assumptions": [
            "owner_remediation_only",
            "runbook_only",
            "checklist_only",
            "research_only",
            "virtual_only",
            "no_refresh_execution",
            "no_workflow_execution",
            "no_broker",
        ],
        "forbidden_path_hits": hits,
        "source_trace_complete": not hits and all(row["exists"] for row in source_records),
    }


def forbidden_source_path_hits(records: list[dict[str, Any]]) -> list[str]:
    hits: list[str] = []
    for row in records:
        path = str(row.get("path") or "").lower().replace("\\", "/")
        for token in FORBIDDEN_PATH_TOKENS:
            if token in path:
                hits.append(f"{row.get('path')}:{token}")
    return sorted(set(hits))


def _record(paths: ProjectPaths, path: Path) -> dict[str, Any]:
    return {
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }
