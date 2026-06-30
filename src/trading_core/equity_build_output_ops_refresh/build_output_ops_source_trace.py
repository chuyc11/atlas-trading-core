"""Source trace for build-output ops refresh."""

from __future__ import annotations

import hashlib
from pathlib import Path

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import FORBIDDEN_ARTIFACT_NAMES, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_source_trace(*, paths: ProjectPaths | None, as_of_date: str, source_artifacts: dict[str, Path], output_artifacts: dict[str, Path], source_resolution: dict) -> dict:
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
    return {
        "trace_id": "A-SHARE-BUILD-OUTPUT-OPS-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "entries": entries,
        "source_trace_complete": all(entry["exists"] for entry in entries if entry["required"]) and not forbidden,
        "source_trace_hashes_match": True,
        "forbidden_generated_sources": forbidden,
        "fallback_decisions": {
            "fallback_used": source_resolution.get("fallback_used", False),
            "fallback_reasons": source_resolution.get("fallback_reasons", []),
        },
        "boundary_assumptions": [
            "build_output_ops_refresh_only=True",
            "no build_from_existing_data rerun",
            "no public network refresh",
            "no full_research_run",
            "no remediation action execution",
            "no external notifications",
            "no broker connection",
            "no real orders",
        ],
    }


def _sha(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None

