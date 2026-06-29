"""Boundary checks for A-share current-day research runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import (
    CURRENT_DAY_BOUNDARY,
    FORBIDDEN_ARTIFACT_NAMES,
    FORBIDDEN_POSITIVE_WORDING,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_current_day_boundary_check(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    warnings: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    paths = default_paths(paths)
    forbidden_artifacts = _forbidden_artifacts(paths, as_of_date)
    positive_hits = _forbidden_wording_hits(paths, as_of_date)
    blocking = list(blocking_reasons)
    if forbidden_artifacts:
        blocking.append("forbidden_artifacts_present")
    if positive_hits:
        blocking.append("forbidden_positive_wording_present")
    return {
        "boundary_id": "A-SHARE-CURRENT-DAY-RESEARCH-RUN-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **CURRENT_DAY_BOUNDARY,
        "forbidden_artifacts_present": forbidden_artifacts,
        "forbidden_wording_positive_hits": positive_hits,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
    }


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> list[str]:
    roots = [
        paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date,
        paths.outputs_dir / "equity_current_day_runs" / "daily" / as_of_date,
    ]
    hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for item in root.rglob("*"):
            if item.name in FORBIDDEN_ARTIFACT_NAMES:
                hits.append(relative(item, paths.project_root))
    protected = [
        paths.data_dir / "orders" / f"orders-{as_of_date}.jsonl",
        paths.data_dir / "trades" / f"trades-{as_of_date}.jsonl",
        paths.data_dir / "accounts" / f"account-{as_of_date}.json",
        paths.outputs_dir / "orders" / f"ORDER_PREVIEW-{as_of_date}.md",
        paths.outputs_dir / "trades" / f"trades-{as_of_date}.md",
        paths.outputs_dir / "accounts" / f"account-{as_of_date}.md",
    ]
    hits.extend(relative(path, paths.project_root) for path in protected if path.exists())
    return sorted(set(hits))


def _forbidden_wording_hits(paths: ProjectPaths, as_of_date: str) -> list[str]:
    roots = [
        paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date,
        paths.outputs_dir / "equity_current_day_runs" / "daily" / as_of_date,
    ]
    hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json"}:
                hits.extend(_hits_in_file(path, paths.project_root))
    return sorted(set(hits))


def _hits_in_file(path: Path, root: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits = []
    for phrase in FORBIDDEN_POSITIVE_WORDING:
        index = text.find(phrase)
        if index >= 0 and not _negative_context(text, index):
            hits.append(f"{relative(path, root)}:{phrase}")
    return hits


def _negative_context(text: str, index: int) -> bool:
    prefix = text[max(0, index - 10) : index]
    return any(marker in prefix for marker in ["不", "无", "未", "不是", "不得"])
