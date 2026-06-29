"""Artifact index for current-day research runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import TARGET_VERSION, current_day_artifact_paths
from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.equity_workflows.workflow_config import workflow_artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_current_day_artifact_index(*, paths: ProjectPaths | None, as_of_date: str, resolved_as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    entries: list[dict[str, Any]] = []
    groups = [
        ("data_refresh", data_refresh_artifact_paths(paths, resolved_as_of_date), "v0.8.0", False),
        ("workflow", workflow_artifact_paths(paths, resolved_as_of_date), "v0.7.9", False),
        ("current_day", current_day_artifact_paths(paths, as_of_date), TARGET_VERSION, True),
    ]
    for stage, artifacts, source_version, created in groups:
        for key, path in sorted(artifacts.items()):
            entries.append(_entry(paths, key, stage, path, source_version, created))
    for stage, root, source_version in _optional_roots(paths, resolved_as_of_date):
        if root.exists():
            for path in sorted(item for item in root.rglob("*") if item.is_file()):
                entries.append(_entry(paths, path.stem, stage, path, source_version, False))
    return {
        "index_id": "A-SHARE-CURRENT-DAY-ARTIFACT-INDEX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "artifacts": entries,
        "artifact_count": len(entries),
    }


def _optional_roots(paths: ProjectPaths, as_of_date: str) -> list[tuple[str, Path, str]]:
    return [
        ("briefing", paths.data_dir / "equity_briefings" / "daily" / as_of_date, "v0.7.7"),
        ("tracking", paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date, "v0.7.8"),
        ("benchmark", paths.data_dir / "equity_benchmarks" / "daily" / as_of_date, "v0.7.10"),
        ("performance", paths.data_dir / "equity_performance" / "daily" / as_of_date, "v0.7.11"),
        ("attribution", paths.data_dir / "equity_attribution" / "daily" / as_of_date, "v0.7.12"),
    ]


def _entry(paths: ProjectPaths, artifact_id: str, stage: str, path: Path, source_version: str, created: bool) -> dict[str, Any]:
    suffix = path.suffix.lstrip(".") or "directory"
    return {
        "artifact_id": artifact_id,
        "artifact_type": suffix,
        "stage": stage,
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
        "source_version": source_version,
        "created_by_current_day_run": created,
    }

