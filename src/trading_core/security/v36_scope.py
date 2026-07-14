"""Stable source/config scope used by the V36 security evidence contract."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


SCOPE_ROOTS = ("src", "scripts", "tests", "config", ".github")
SCOPE_ROOT_FILES = ("pyproject.toml", "VERSION")
IGNORED_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_v36_scope_records(project_root: Path) -> list[dict[str, Any]]:
    root = project_root.resolve()
    candidates: set[Path] = set()
    for name in SCOPE_ROOTS:
        base = root / name
        if base.is_dir():
            candidates.update(path for path in base.rglob("*") if path.is_file())
    for name in SCOPE_ROOT_FILES:
        path = root / name
        if path.is_file():
            candidates.add(path)
    candidates.update(path for path in root.glob("requirements*.txt") if path.is_file())

    records: list[dict[str, Any]] = []
    for path in sorted(candidates, key=lambda value: value.as_posix().lower()):
        relative = path.resolve().relative_to(root)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        records.append(
            {
                "path": relative.as_posix(),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return records
