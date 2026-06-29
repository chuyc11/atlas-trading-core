"""Artifact navigation for the daily ops center."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_ops_center.ops_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_ops_artifact_navigation(*, paths: ProjectPaths | None, as_of_date: str, input_paths: dict[str, Path], output_paths: dict[str, Path]) -> dict[str, Any]:
    paths = default_paths(paths)
    entries = []
    for artifact_id, path in {**input_paths, **output_paths}.items():
        entries.append(
            {
                "artifact_id": artifact_id,
                "module_id": _module_id(artifact_id),
                "label_zh": _label(artifact_id),
                "category": _category(artifact_id),
                "path": relative(path, paths.project_root),
                "exists": path.exists(),
                "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
                "owner_priority": _priority(artifact_id),
            }
        )
    return {
        "navigation_id": "A-SHARE-DAILY-OPS-CENTER-ARTIFACT-NAVIGATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "entries": entries,
    }


def _module_id(artifact_id: str) -> str:
    for prefix, module in [
        ("data_refresh", "data_refresh"),
        ("current_day", "current_day_research_run"),
        ("owner_dashboard", "owner_dashboard"),
        ("dashboard", "owner_dashboard"),
        ("owner_monitoring", "owner_monitoring"),
        ("monitoring", "owner_monitoring"),
        ("owner_remediation", "owner_remediation"),
        ("remediation", "owner_remediation"),
        ("ops", "ops_center"),
    ]:
        if artifact_id.startswith(prefix):
            return module
    return "audits" if artifact_id.endswith("audit") else "ops_center"


def _category(artifact_id: str) -> str:
    if "source_trace" in artifact_id:
        return "source traces"
    if "boundary" in artifact_id:
        return "boundary checks"
    if artifact_id.endswith("audit"):
        return "audits"
    if "report" in artifact_id:
        return "owner reports"
    return "artifacts"


def _priority(artifact_id: str) -> str:
    if artifact_id.endswith("audit") or "health_score" in artifact_id or "command_center" in artifact_id:
        return "high"
    if "boundary" in artifact_id or "source_trace" in artifact_id:
        return "diagnostic"
    if "summary" in artifact_id or "manifest" in artifact_id:
        return "medium"
    return "low"


def _label(artifact_id: str) -> str:
    return artifact_id.replace("_", " ")
