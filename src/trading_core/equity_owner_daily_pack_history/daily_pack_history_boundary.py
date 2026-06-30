"""Boundary check for daily pack history."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import (
    BOUNDARY,
    FORBIDDEN_ARTIFACT_NAMES,
    FORBIDDEN_POSITIVE_WORDING,
    TARGET_VERSION,
    data_dir,
    output_dir,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_boundary_check(*, paths: ProjectPaths | None, as_of_date: str, blocking_reasons: list[str], warnings: list[str], synthetic_history_used: bool = False, future_dates_used: bool = False) -> dict:
    paths = default_paths(paths)
    forbidden_artifacts = _forbidden_artifacts(paths, as_of_date)
    wording = _forbidden_wording_hits(paths, as_of_date)
    blocking = list(blocking_reasons)
    if synthetic_history_used:
        blocking.append("synthetic_history_used")
    if future_dates_used:
        blocking.append("future_dates_used")
    if forbidden_artifacts:
        blocking.append("forbidden_artifacts_present")
    if wording:
        blocking.append("forbidden_positive_wording_present")
    return {
        "boundary_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **BOUNDARY,
        "append_only_history": True,
        "allow_synthetic_history": False,
        "synthetic_history_used": synthetic_history_used,
        "future_dates_used": future_dates_used,
        "forbidden_artifacts_present": sorted(set(forbidden_artifacts)),
        "forbidden_wording_positive_hits": sorted(set(wording)),
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
    }


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> list[str]:
    hits = []
    for root in [data_dir(paths, as_of_date), output_dir(paths, as_of_date)]:
        if root.exists():
            for path in root.rglob("*"):
                if path.name in FORBIDDEN_ARTIFACT_NAMES:
                    hits.append(relative(path, paths.project_root))
    return hits


def _forbidden_wording_hits(paths: ProjectPaths, as_of_date: str) -> list[str]:
    hits = []
    for root in [data_dir(paths, as_of_date), output_dir(paths, as_of_date)]:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".json", ".md"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                for phrase in FORBIDDEN_POSITIVE_WORDING:
                    idx = text.find(phrase)
                    if idx >= 0 and not _negative_context(text, idx):
                        hits.append(f"{relative(path, paths.project_root)}:{phrase}")
    return hits


def _negative_context(text: str, index: int) -> bool:
    prefix = text[max(0, index - 45) : index]
    return any(marker in prefix for marker in ["不", "无", "未", "不是", "不得", "禁止", "不会", "does not", "not "])
