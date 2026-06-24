"""Shared helpers for system integrity commands."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.reports.research_common import snapshot_diff, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths, project_paths


PROTECTED_BUCKETS = ["orders", "trades", "portfolio", "portfolios", "accounts"]


def default_paths(paths: ProjectPaths | None = None) -> ProjectPaths:
    return paths or project_paths()


def timestamp_id(prefix: str) -> tuple[str, str]:
    now = datetime.now(UTC)
    return f"{prefix}-{now:%Y%m%d}-001", now.isoformat().replace("+00:00", "Z")


def write_json_markdown(json_path: Path, payload: dict[str, Any], report_path: Path, markdown: str) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(markdown, encoding="utf-8")


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def protected_diff(paths: ProjectPaths, before: dict[str, Any]) -> list[str]:
    return snapshot_diff(before, snapshot_protected(paths))
