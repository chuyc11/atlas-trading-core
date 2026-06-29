"""Boundary checks for repeatability."""

from __future__ import annotations

from trading_core.equity_build_repeatability.repeatability_config import (
    FORBIDDEN_ARTIFACT_NAMES,
    FORBIDDEN_POSITIVE_WORDING,
    REPEATABILITY_BOUNDARY,
    TARGET_VERSION,
    repeatability_data_dir,
    repeatability_output_dir,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_repeatability_boundary_check(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    execution_record: dict,
    protected_check: dict,
    comparison: dict,
    drift_summary: dict,
) -> dict:
    paths = default_paths(paths)
    forbidden_artifacts = _forbidden_artifacts(paths, as_of_date)
    wording_hits = _forbidden_wording_hits(paths, as_of_date)
    blocking = []
    blocking.extend(execution_record.get("blocking_reasons", []))
    blocking.extend(protected_check.get("blocking_reasons", []))
    blocking.extend(comparison.get("blocking_reasons", []))
    blocking.extend(drift_summary.get("blocking_reasons", []))
    if forbidden_artifacts:
        blocking.append("forbidden_artifacts_present")
    if wording_hits:
        blocking.append("forbidden_positive_wording_present")
    for key, reason in [
        ("old_run_daily_called", "old_run_daily_called"),
        ("run_daily_called", "run_daily_called"),
        ("broker_connected", "broker_connected"),
        ("real_orders_placed", "real_orders_placed"),
        ("buy_sell_signals_generated", "buy_sell_signals_generated"),
        ("order_preview_generated", "order_preview_generated"),
        ("real_account_data_read", "real_account_data_read"),
        ("public_network_refresh_run", "public_network_refresh_run"),
        ("full_research_run", "full_research_run"),
    ]:
        if execution_record.get(key, False):
            blocking.append(reason)
    return {
        "boundary_id": "A-SHARE-BUILD-REPEATABILITY-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **REPEATABILITY_BOUNDARY,
        "workflow_mode": "build_from_existing_data",
        "repeat_build_execution_performed": execution_record.get("command_executed", False),
        "repeat_build_audit_passed": execution_record.get("workflow_audit_overall_passed", False),
        "comparison_completed": comparison.get("comparison_completed", False),
        "protected_path_modifications_detected": protected_check.get("protected_path_modifications_detected", False),
        "forbidden_artifacts_present": sorted(set(forbidden_artifacts)),
        "forbidden_wording_positive_hits": sorted(set(wording_hits)),
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(protected_check.get("warnings", []) + execution_record.get("warnings", []))),
    }


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> list[str]:
    hits = []
    for root in [repeatability_data_dir(paths, as_of_date), repeatability_output_dir(paths, as_of_date)]:
        if not root.exists():
            continue
        for item in root.rglob("*"):
            if item.name in FORBIDDEN_ARTIFACT_NAMES:
                hits.append(relative(item, paths.project_root))
    return hits


def _forbidden_wording_hits(paths: ProjectPaths, as_of_date: str) -> list[str]:
    hits = []
    for root in [repeatability_data_dir(paths, as_of_date), repeatability_output_dir(paths, as_of_date)]:
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

