"""Build artifact index for v0.8.7 gated build."""

from __future__ import annotations

import hashlib
from pathlib import Path

from trading_core.equity_current_day_builds.gated_build_config import (
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


def build_gated_build_artifact_index(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    workflow_result: dict,
) -> dict:
    paths = default_paths(paths)

    current_day_dir = (
        paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date
    )

    artifacts = []
    if current_day_dir.exists():
        for item in sorted(current_day_dir.rglob("*.json")):
            artifacts.append({
                "artifact_id": item.stem,
                "artifact_type": "json",
                "path": relative(item, paths.project_root),
                "exists": True,
                "sha256": _sha256(item),
                "source_stage": "current_day_build",
            })

    # Also index the current-day output markdown files
    current_day_output_dir = (
        paths.outputs_dir / "equity_current_day_runs" / "daily" / as_of_date
    )
    if current_day_output_dir.exists():
        for item in sorted(current_day_output_dir.rglob("*.md")):
            artifacts.append({
                "artifact_id": item.stem,
                "artifact_type": "md",
                "path": relative(item, paths.project_root),
                "exists": True,
                "sha256": _sha256(item),
                "source_stage": "current_day_build",
            })

    return {
        "index_id": "A-SHARE-GATED-BUILD-ARTIFACT-INDEX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "workflow_status": workflow_result.get("status", "unknown"),
        "workflow_audit_passed": workflow_result.get("workflow_audit_overall_passed", False),
    }
