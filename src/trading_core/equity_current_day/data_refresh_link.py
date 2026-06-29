"""Link current-day runs to v0.8.0 data refresh artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import TARGET_VERSION
from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_data_refresh_link(*, paths: ProjectPaths | None, as_of_date: str, resolved_as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = data_refresh_artifact_paths(paths, resolved_as_of_date)
    audit = load_json(artifacts["data_refresh_audit_json"])
    dataset_checks = audit.get("dataset_checks", {})
    link_keys = [
        "data_refresh_config",
        "date_resolution",
        "dataset_refresh_result",
        "dataset_schema_validation",
        "dataset_freshness_validation",
        "dataset_coverage_summary",
        "data_refresh_audit_json",
    ]
    return {
        "link_id": "A-SHARE-CURRENT-DAY-DATA-REFRESH-LINK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "data_refresh_artifacts": {key: _record(paths, artifacts[key]) for key in link_keys},
        "data_refresh_audit_path": relative(artifacts["data_refresh_audit_json"], paths.project_root),
        "data_refresh_audit_hash": sha256_file(artifacts["data_refresh_audit_json"]),
        "data_refresh_audit_passed": audit.get("overall_passed") is True,
        "data_refresh_blocking_reasons": list(audit.get("blocking_reasons", [])),
        "data_refresh_warnings": list(audit.get("warnings", [])),
        "datasets_passed": [key for key, value in dataset_checks.items() if value in {"passed", "warning"}],
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _record(paths: ProjectPaths, path: Path) -> dict[str, Any]:
    return {
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }

