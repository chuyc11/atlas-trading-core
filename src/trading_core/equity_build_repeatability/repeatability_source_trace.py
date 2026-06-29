"""Source trace for repeatability artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path

from trading_core.equity_build_repeatability.repeatability_config import FORBIDDEN_ARTIFACT_NAMES, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_repeatability_source_trace(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    source_artifacts: dict[str, Path],
    output_artifacts: dict[str, Path],
) -> dict:
    paths = default_paths(paths)
    entries = []
    forbidden = []
    for required, artifacts in [(True, source_artifacts), (False, output_artifacts)]:
        for artifact_id, path in artifacts.items():
            rel = relative(path, paths.project_root)
            if path.name in FORBIDDEN_ARTIFACT_NAMES:
                forbidden.append(rel)
            entries.append({
                "artifact_id": artifact_id,
                "required": required,
                "path": rel,
                "exists": path.exists(),
                "sha256": _sha(path),
            })
    complete = all(e["exists"] for e in entries if e["required"]) and not forbidden
    return {
        "trace_id": "A-SHARE-BUILD-REPEATABILITY-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "entries": entries,
        "source_trace_complete": complete,
        "forbidden_generated_sources": forbidden,
        "boundary_assumptions": [
            "repeatability_only=True",
            "research_only=True",
            "virtual_only=True",
            "preexisting protected paths are allowed only if unchanged",
            "no broker connection",
            "no real orders",
            "no order preview",
            "no buy/sell signals",
            "no old run-daily call",
            "no official forward dry-run day2",
        ],
    }


def _sha(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None

