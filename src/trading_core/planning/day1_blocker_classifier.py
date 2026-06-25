"""Extract day-1 blockers from MVP gap classification."""

from __future__ import annotations

from typing import Any

from trading_core.planning.common import paths_or_default, read_dict, rel, resolve_path, standard_boundary
from trading_core.planning.mvp_gap_classifier import classify_mvp_gaps
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


BLOCKER_IDS = {
    "R001": "missing_trading_calendar",
    "R003": "missing_price_data",
    "R004": "missing_adjusted_price_contract",
    "R005": "missing_pit_contract",
    "R006": "missing_t_plus_1_semantics",
    "R007": "missing_suspension_handling",
    "R008": "missing_limit_up_down_handling",
    "R010": "missing_execution_model",
    "R011": "missing_cost_model",
    "R012": "missing_ledger_accounting",
    "R013": "missing_ledger_accounting",
    "R014": "missing_equity_curve",
    "R015": "missing_benchmark_comparison",
    "R017": "missing_daily_report",
    "R019": "boundary_violation",
    "R020": "boundary_violation",
    "R021": "boundary_violation",
    "R024": "missing_30_day_forward_dry_run_plan",
}


def classify_day1_blockers(*, mvp_gap_classification_path: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    classifier_id, created_at = timestamp_id("DAY1-BLOCKER-CLASSIFICATION")
    classification_file = resolve_path(mvp_gap_classification_path, paths.data_dir / "system" / "mvp_gap_classification.json", paths)
    classification = read_dict(classification_file) or classify_mvp_gaps(paths=paths)
    blockers = []
    manual_acceptance = []
    deferred = []
    non_blocking = []
    for item in classification.get("requirements", []):
        record = _classify_item(item)
        if record["severity"] == "blocking":
            blockers.append(record)
        elif record["severity"] == "requires_manual_acceptance":
            manual_acceptance.append(record)
        elif record["severity"] == "deferred_non_blocking":
            deferred.append(record)
        else:
            non_blocking.append(record)
    payload: dict[str, Any] = {
        "classifier_id": classifier_id,
        "created_at": created_at,
        "mvp_gap_classification_path": rel(classification_file, paths),
        "day1_allowed": False,
        "blocking_count": len(blockers),
        "requires_manual_acceptance_count": len(manual_acceptance),
        "blockers": blockers,
        "requires_manual_acceptance": manual_acceptance,
        "deferred_non_blocking": deferred,
        "not_blocking": non_blocking,
        "manual_confirmation_complete": False,
        "boundary": standard_boundary("classifier_only"),
    }
    json_path = paths.data_dir / "system" / "day1_blocker_classification.json"
    md_path = paths.outputs_dir / "system" / "DAY1_BLOCKER_CLASSIFICATION.md"
    write_json_markdown(json_path, payload, md_path, build_day1_blocker_classification_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _classify_item(item: dict[str, Any]) -> dict[str, Any]:
    if item.get("day1_blocker"):
        severity = "blocking"
    elif item.get("status") == "partial" and item.get("accepted_partial"):
        severity = "requires_manual_acceptance"
    elif item.get("status") in {"deferred", "not_applicable"} or item.get("requirement_id") in {"R022", "R023"}:
        severity = "deferred_non_blocking"
    else:
        severity = "not_blocking"
    return {
        "requirement_id": item["requirement_id"],
        "blocker_id": BLOCKER_IDS.get(item["requirement_id"], f"{item['name']}_gap"),
        "severity": severity,
        "reason": item.get("rationale", ""),
        "status": item.get("status"),
    }


def build_day1_blocker_classification_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day-1 Blocker Classification",
        "",
        "## Decision",
        f"day1_allowed: {str(payload['day1_allowed']).lower()} unless blocking_count=0 and manual confirmations complete.",
        f"- blocking_count: {payload['blocking_count']}",
        f"- requires_manual_acceptance_count: {payload['requires_manual_acceptance_count']}",
        "",
        "## Blocking Items",
    ]
    if payload["blockers"]:
        lines.extend(f"- {item['requirement_id']} {item['blocker_id']}: {item['reason']}" for item in payload["blockers"])
    else:
        lines.append("- none")
    lines.extend(["", "## Requires Manual Acceptance"])
    if payload["requires_manual_acceptance"]:
        lines.extend(f"- {item['requirement_id']} {item['blocker_id']}: {item['reason']}" for item in payload["requires_manual_acceptance"])
    else:
        lines.append("- none")
    lines.extend(["", "## Deferred Non-Blocking"])
    if payload["deferred_non_blocking"]:
        lines.extend(f"- {item['requirement_id']} {item['blocker_id']}" for item in payload["deferred_non_blocking"])
    else:
        lines.append("- none")
    lines.extend(["", "## Boundary", "- classifier only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)
