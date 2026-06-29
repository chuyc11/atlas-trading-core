"""Source trace for v0.8.7 gated build."""

from __future__ import annotations

import hashlib
from pathlib import Path

from trading_core.equity_current_day_builds.gated_build_config import (
    FORBIDDEN_PATH_TOKENS,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None


def _check_forbidden_paths(path_strs: list[str]) -> list[str]:
    hits: list[str] = []
    for path_str in path_strs:
        norm = path_str.replace("\\", "/").lower()
        for token in FORBIDDEN_PATH_TOKENS:
            if token.lower() in norm:
                hits.append(f"{path_str}:{token}")
    return hits


def build_gated_build_source_trace(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    source_artifacts: dict[str, Path],
    output_artifacts: dict[str, Path],
    workflow_command: str = "",
) -> dict:
    paths = default_paths(paths)

    all_artifacts = {**source_artifacts, **output_artifacts}
    trace_entries = []
    path_strs = []

    for key, path in all_artifacts.items():
        path_str = relative(path, paths.project_root)
        path_strs.append(path_str)
        trace_entries.append({
            "artifact_id": key,
            "required": key in source_artifacts,
            "path": path_str,
            "exists": path.exists(),
            "sha256": _sha256(path),
        })

    forbidden_hits = _check_forbidden_paths(path_strs)

    boundary_assumptions = [
        "gated_build_from_existing_data_only=True",
        "research_only=True",
        "virtual_only=True",
        "no broker connection",
        "no real orders",
        "no buy/sell signals",
        "no order preview",
        "no old run-daily call",
        "no official forward dry-run day2",
        "workflow command uses build_from_existing_data",
    ]

    complete = not forbidden_hits and all(e["exists"] for e in trace_entries if e["required"])

    return {
        "trace_id": "A-SHARE-GATED-BUILD-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "entries": trace_entries,
        "workflow_command": workflow_command,
        "forbidden_path_hits": sorted(set(forbidden_hits)),
        "boundary_assumptions": boundary_assumptions,
        "source_trace_complete": complete,
    }
