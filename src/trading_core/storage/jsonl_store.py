"""Small JSON/JSONL helpers used by the file-backed pipeline."""

from __future__ import annotations

import json
from uuid import uuid4
from pathlib import Path
from typing import Any
from collections.abc import Iterable


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at {path}") from exc


def _atomic_write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    tmp_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(path)


def write_json(path: Path, payload: Any) -> Path:
    _atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return path


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row must be an object at {path}:{line_number}")
        rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> Path:
    text = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    _atomic_write_text(path, text)
    return path


def append_jsonl(path: Path, row: dict[str, Any]) -> Path:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return path
