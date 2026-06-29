"""Boundary checks for v0.8.6 ops history baselines."""

from __future__ import annotations

from trading_core.equity_ops_history.ops_history_config import (
    FORBIDDEN_ARTIFACT_NAMES,
    FORBIDDEN_POSITIVE_WORDING,
    OPS_HISTORY_BOUNDARY,
    TARGET_VERSION,
    ops_history_data_dir,
    ops_history_output_dir,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_ops_history_boundary_check(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    warnings: list[str],
    blocking_reasons: list[str],
    commands_executed: list[str] | None = None,
    synthetic_history_used: bool = False,
    future_dates_used: bool = False,
) -> dict:
    paths = default_paths(paths)
    commands = list(commands_executed or [])
    forbidden_artifacts = _forbidden_artifacts(paths, as_of_date)
    wording_hits = _forbidden_wording_hits(paths, as_of_date)
    blocking = list(blocking_reasons)
    if commands:
        blocking.append("commands_executed_not_empty")
    if synthetic_history_used:
        blocking.append("synthetic_history_used")
    if future_dates_used:
        blocking.append("future_dates_used")
    if forbidden_artifacts:
        blocking.append("forbidden_artifacts_present")
    if wording_hits:
        blocking.append("forbidden_positive_wording_present")
    boundary = {
        **OPS_HISTORY_BOUNDARY,
        "commands_executed": commands,
        "synthetic_history_used": synthetic_history_used,
        "future_dates_used": future_dates_used,
    }
    return {
        "boundary_id": "A-SHARE-OPS-HISTORY-BASELINE-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **boundary,
        "forbidden_artifacts_present": sorted(set(forbidden_artifacts)),
        "forbidden_wording_positive_hits": sorted(set(wording_hits)),
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
    }


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> list[str]:
    hits: list[str] = []
    for root in [ops_history_data_dir(paths, as_of_date), ops_history_output_dir(paths, as_of_date)]:
        if root.exists():
            for item in root.rglob("*"):
                if item.name in FORBIDDEN_ARTIFACT_NAMES:
                    hits.append(relative(item, paths.project_root))
    protected = [
        paths.data_dir / "orders" / f"orders-{as_of_date}.jsonl",
        paths.data_dir / "trades" / f"trades-{as_of_date}.jsonl",
        paths.data_dir / "accounts" / f"account-{as_of_date}.json",
        paths.outputs_dir / "orders" / f"ORDER_PREVIEW-{as_of_date}.md",
        paths.outputs_dir / "trades" / f"TRADES-{as_of_date}.md",
        paths.outputs_dir / "accounts" / f"ACCOUNT-{as_of_date}.md",
    ]
    hits.extend(relative(path, paths.project_root) for path in protected if path.exists())
    return hits


def _forbidden_wording_hits(paths: ProjectPaths, as_of_date: str) -> list[str]:
    hits: list[str] = []
    for root in [ops_history_data_dir(paths, as_of_date), ops_history_output_dir(paths, as_of_date)]:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".json", ".md"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                for phrase in FORBIDDEN_POSITIVE_WORDING:
                    index = text.find(phrase)
                    if index >= 0 and not _negative_context(text, index):
                        hits.append(f"{relative(path, paths.project_root)}:{phrase}")
    return hits


def _negative_context(text: str, index: int) -> bool:
    prefix = text[max(0, index - 20) : index]
    return any(marker in prefix for marker in ["不", "无", "未", "不是", "不得", "禁止", "不会", "does not", "not "])

