"""Scan existing repo artifacts for MVP evidence coverage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.planning.common import paths_or_default, rel, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


SCAN_ROOTS = [
    ("module", "src/trading_core"),
    ("test", "tests"),
    ("artifact", "data/system"),
    ("report", "outputs/system"),
    ("audit", "outputs/audit"),
    ("doc", "docs"),
]
TOP_LEVEL_FILES = ["README.md", "RELEASE_NOTES.md", "VERSION"]
MAX_RECORDS = 5000


def build_artifact_coverage_scan(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    scan_id, created_at = timestamp_id("ARTIFACT-COVERAGE-SCAN")
    artifacts = []
    counts = {"modules": 0, "tests": 0, "system_artifacts": 0, "system_reports": 0, "audit_reports": 0, "docs": 0}
    for artifact_type, raw_root in SCAN_ROOTS:
        root = paths.project_root / raw_root
        if not root.exists():
            continue
        for file in sorted(item for item in root.rglob("*") if item.is_file()):
            if len(artifacts) >= MAX_RECORDS:
                break
            record = _file_record(file, artifact_type, paths)
            artifacts.append(record)
            _increment_count(counts, artifact_type, raw_root)
    for name in TOP_LEVEL_FILES:
        file = paths.project_root / name
        if file.exists():
            artifacts.append(_file_record(file, "doc", paths))
            counts["docs"] += 1
    payload: dict[str, Any] = {
        "scan_id": scan_id,
        "created_at": created_at,
        "counts": counts,
        "artifacts": artifacts,
        "read_policy": {"large_file_content_read": False, "metadata_only": True, "max_records": MAX_RECORDS},
        "boundary": standard_boundary("scanner_only"),
    }
    json_path = paths.data_dir / "system" / "artifact_coverage_scan.json"
    md_path = paths.outputs_dir / "system" / "ARTIFACT_COVERAGE_SCAN.md"
    write_json_markdown(json_path, payload, md_path, build_artifact_coverage_scan_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _file_record(file: Path, artifact_type: str, paths: ProjectPaths) -> dict[str, Any]:
    stat = file.stat()
    return {"type": artifact_type, "path": rel(file, paths), "size_bytes": stat.st_size, "mtime": stat.st_mtime}


def _increment_count(counts: dict[str, int], artifact_type: str, raw_root: str) -> None:
    if artifact_type == "module":
        counts["modules"] += 1
    elif artifact_type == "test":
        counts["tests"] += 1
    elif raw_root == "data/system":
        counts["system_artifacts"] += 1
    elif raw_root == "outputs/system":
        counts["system_reports"] += 1
    elif raw_root == "outputs/audit":
        counts["audit_reports"] += 1
    elif artifact_type == "doc":
        counts["docs"] += 1


def build_artifact_coverage_scan_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Artifact Coverage Scan",
        "",
        "## Scope",
        "This scanner records current modules, tests, CLI artifacts, reports, audits, and docs as MVP evidence candidates.",
        "It does not read large data files in full and does not start forward dry-run.",
        "",
        "## Counts",
    ]
    lines.extend(f"- {key}: {value}" for key, value in payload["counts"].items())
    lines.extend(["", "## Boundary", "- scanner only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

