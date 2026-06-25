"""Protected path residue scanner for local ignored runtime files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

from .common import NOTICE, PROTECTED_PATHS, boundary_markdown, git_lines, paths_or_default, workflow_boundary, write_artifact


def scan_protected_path_residue(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    tracked = set(git_lines(paths, ["ls-files", "--", *PROTECTED_PATHS]))
    modified = {line[3:].replace("\\", "/") for line in git_lines(paths, ["status", "--short", "--", *PROTECTED_PATHS]) if line[:2].strip()}
    records = []
    warnings = []
    blockers = []
    for raw in PROTECTED_PATHS:
        root = paths.project_root / raw
        if not root.exists():
            records.append({"path": raw, "classification": "no_residue", "file_count": 0, "blocking": False})
            continue
        files = [file for file in root.rglob("*") if file.is_file()]
        tracked_files = [rel for rel in tracked if rel == raw or rel.startswith(f"{raw}/")]
        modified_files = [rel for rel in modified if rel == raw or rel.startswith(f"{raw}/")]
        if modified_files:
            classification = "modified_protected_artifact"
            blockers.append({"path": raw, "classification": classification, "files": modified_files})
        elif tracked_files:
            classification = "tracked_protected_artifact"
            blockers.append({"path": raw, "classification": classification, "files": tracked_files})
        elif files:
            classification = "ignored_runtime_residue"
            warnings.append({"path": raw, "classification": classification, "file_count": len(files), "severity": "nit"})
        else:
            classification = "no_residue"
        records.append({"path": raw, "classification": classification, "file_count": len(files), "blocking": classification in {"tracked_protected_artifact", "modified_protected_artifact"}})
    payload: dict[str, Any] = {
        "scan_id": "PROTECTED-PATH-RESIDUE-SCAN",
        "records": records,
        "warnings": warnings,
        "blocking_reasons": blockers,
        "warning_count": len(warnings),
        "blocker_count": len(blockers),
        "overall_passed": len(blockers) == 0,
        "scanner_actions": {
            "deleted_files": False,
            "moved_files": False,
            "cleaned_directories": False,
            "modified_gitignore": False,
            "auto_fixed_residue": False,
        },
        "boundary": workflow_boundary("protected_path_residue_scan_only"),
    }
    json_path = paths.data_dir / "system" / "protected_path_residue_scan.json"
    md_path = paths.outputs_dir / "audit" / "PROTECTED_PATH_RESIDUE_SCAN.md"
    return write_artifact(json_path, payload, md_path, build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Protected Path Residue Scan",
        "",
        NOTICE,
        "",
        "## Summary",
        f"- blocker_count: {payload['blocker_count']}",
        f"- warning_count: {payload['warning_count']}",
        "",
        "## Records",
    ]
    lines.extend(f"- {item['path']}: {item['classification']} files={item['file_count']}" for item in payload["records"])
    lines.extend(["", "## Boundary"])
    lines.extend(boundary_markdown("protected path residue scan only"))
    lines.append("")
    return "\n".join(lines)

