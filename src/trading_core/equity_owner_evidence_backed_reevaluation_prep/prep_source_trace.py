"""Source trace for evidence-backed reevaluation prep."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_prep_source_trace(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE, source_paths: dict[str, Path], output_paths: dict[str, Path], boundary: dict[str, Any]) -> dict[str, Any]:
    paths = default_paths(paths)
    source_rows = [_row(paths, key, path, required=True) for key, path in source_paths.items()]
    output_rows = [_row(paths, key, path, required=True) for key, path in output_paths.items()]
    missing = [row["artifact_key"] for row in source_rows if row["required"] and not row["exists"]]
    return {
        "trace_id": "A-SHARE-EVIDENCE-BACKED-PREP-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_trace_complete": not missing,
        "missing_required_sources": missing,
        "source_artifacts": source_rows,
        "output_artifacts": output_rows,
        "boundary_assumptions": boundary,
        "source_resolution_decisions": [
            "Prefer v0.8.18 recovery evidence artifacts.",
            "Use v0.8.17 controlled reevaluation artifacts as skipped-not-ready context.",
            "Use v0.8.13 owner readiness gate artifacts as source gate truth.",
        ],
    }


def _row(paths: ProjectPaths, key: str, path: Path, *, required: bool) -> dict[str, Any]:
    exists = path.exists()
    return {
        "artifact_key": key,
        "path": str(path),
        "relative_path": str(path.relative_to(paths.project_root)) if path.is_relative_to(paths.project_root) else str(path),
        "required": required,
        "exists": exists,
        "sha256": sha256_file(path) if exists and path.is_file() else "",
    }

