"""Shared helpers for v0.5 research reporting."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, UTC
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths


PROTECTED_PATHS = [
    "data/orders",
    "data/trades",
    "data/portfolio",
    "data/portfolios",
    "data/accounts",
    "outputs/orders",
    "outputs/trades",
    "outputs/portfolio",
    "outputs/portfolios",
]


def utc_now_id(prefix: str) -> tuple[str, str]:
    now = datetime.now(UTC)
    return f"{prefix}-{now:%Y%m%d}", now.isoformat().replace("+00:00", "Z")


def dates_between(start_date: str, end_date: str) -> list[str]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        return []
    output = []
    current = start
    while current <= end:
        output.append(current.isoformat())
        current += timedelta(days=1)
    return output


def read_json(path: Path, default: Any | None = None, warnings: list[str] | None = None) -> Any:
    if not path.exists():
        if warnings is not None:
            warnings.append(f"missing artifact: {path}")
        return default
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text) if text.strip() else default
    except json.JSONDecodeError as exc:
        if warnings is not None:
            warnings.append(f"malformed JSON skipped: {path.name} ({exc.msg})")
        return default


def read_jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len([line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])


def write_json_and_markdown(json_path: Path, payload: dict[str, Any], md_path: Path, markdown: str) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")


def latest_json(directory: Path, pattern: str) -> dict[str, Any] | None:
    files = sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime) if directory.exists() else []
    if not files:
        return None
    return read_json(files[-1], default=None)


def file_exists(directory: Path, pattern: str) -> bool:
    return bool(list(directory.glob(pattern))) if directory.exists() else False


def snapshot_protected(paths: ProjectPaths) -> dict[str, tuple[tuple[str, int, int], ...]]:
    snapshot: dict[str, tuple[tuple[str, int, int], ...]] = {}
    for raw in PROTECTED_PATHS:
        root = paths.project_root / raw
        if not root.exists():
            snapshot[str(root)] = ()
            continue
        rows = []
        for file in sorted(root.rglob("*")):
            if file.is_file():
                stat = file.stat()
                rows.append((str(file), stat.st_size, stat.st_mtime_ns))
        snapshot[str(root)] = tuple(rows)
    return snapshot


def snapshot_diff(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    changed = []
    for key in sorted(set(before) | set(after)):
        if before.get(key, ()) != after.get(key, ()):
            changed.append(key)
    return changed


def default_paths(paths: ProjectPaths | None = None) -> ProjectPaths:
    return paths or project_paths()
