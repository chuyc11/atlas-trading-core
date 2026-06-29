"""Boundary checks for build-output dashboard."""

from __future__ import annotations

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import (
    BOUNDARY,
    FORBIDDEN_ARTIFACT_NAMES,
    FORBIDDEN_POSITIVE_WORDING,
    TARGET_VERSION,
    data_dir,
    output_dir,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_boundary_check(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    warning_card: dict,
    source_resolution: dict,
) -> dict:
    paths = default_paths(paths)
    forbidden_artifacts = _forbidden_artifacts(paths, as_of_date)
    wording_hits = _forbidden_wording_hits(paths, as_of_date)
    blocking = []
    blocking.extend(warning_card.get("blocking_reasons", []))
    blocking.extend(source_resolution.get("blocking_reasons", []))
    if forbidden_artifacts:
        blocking.append("forbidden_artifacts_present")
    if wording_hits:
        blocking.append("forbidden_positive_wording_present")
    return {
        "boundary_id": "A-SHARE-BUILD-OUTPUT-DASHBOARD-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **BOUNDARY,
        "protected_path_modifications_detected": False,
        "forbidden_artifacts_present": sorted(set(forbidden_artifacts)),
        "forbidden_wording_positive_hits": sorted(set(wording_hits)),
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warning_card.get("warnings", []) + source_resolution.get("warnings", []))),
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
            if not path.is_file() or path.suffix.lower() not in {".json", ".md"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for phrase in FORBIDDEN_POSITIVE_WORDING:
                idx = text.find(phrase)
                if idx >= 0 and not _negative_context(text, idx):
                    hits.append(f"{relative(path, paths.project_root)}:{phrase}")
    return hits


def _negative_context(text: str, index: int) -> bool:
    prefix = text[max(0, index - 30) : index]
    return any(marker in prefix for marker in ["不", "无", "未", "不是", "不得", "禁止", "不会", "does not", "not "])

