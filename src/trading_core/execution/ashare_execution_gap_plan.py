"""Build the v0.5.9 A-share execution gap plan from v0.5.8.1 artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.execution.common import HARDENING_NOTICE, RELEASE_CANDIDATE, paths_or_default, read_dict, rel, resolve_path, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_ashare_execution_gap_plan(*, mvp_gaps_path: str | None = None, day1_blockers_path: str | None = None, next_work_path: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    plan_id, created_at = timestamp_id("ASHARE-EXECUTION-GAP-PLAN")
    mvp_path = resolve_path(mvp_gaps_path, paths.data_dir / "system" / "mvp_gap_classification.json", paths)
    day1_path = resolve_path(day1_blockers_path, paths.data_dir / "system" / "day1_blocker_classification.json", paths)
    next_path = resolve_path(next_work_path, paths.data_dir / "system" / "next_work_register.json", paths)
    mvp = read_dict(mvp_path)
    day1 = read_dict(day1_path)
    next_work = read_dict(next_path)
    warnings = []
    blocking = []
    for label, payload in [("mvp_gap_classification", mvp), ("day1_blocker_classification", day1), ("next_work_register", next_work)]:
        if not payload:
            warnings.append(f"{label} missing")
            blocking.append(f"{label} missing")
    baseline = int(day1.get("blocking_count", 0) or 0)
    work_items = [
        {"work_id": item.get("blocker_id", item.get("requirement_id")), "requirement_id": item.get("requirement_id"), "required_before_day1": True, "status": "targeted", "source_reason": item.get("reason")}
        for item in day1.get("blockers", [])
    ]
    if not work_items and next_work.get("work_items"):
        work_items = [{**item, "status": "targeted"} for item in next_work["work_items"]]
    payload: dict[str, Any] = {
        "plan_id": plan_id,
        "created_at": created_at,
        "source_artifacts": {"mvp_gap_classification": rel(mvp_path, paths), "day1_blocker_classification": rel(day1_path, paths), "next_work_register": rel(next_path, paths)},
        "baseline_day1_blocker_count": baseline,
        "target_day1_blocker_count": 0,
        "target_version": RELEASE_CANDIDATE,
        "work_items": work_items,
        "warnings": warnings,
        "blocking_reasons": blocking,
        "overall_passed": not blocking and bool(work_items),
        "boundary": standard_boundary("planning_only"),
    }
    json_path = paths.data_dir / "system" / "ashare_execution_gap_plan.json"
    md_path = paths.outputs_dir / "system" / "ASHARE_EXECUTION_GAP_PLAN.md"
    write_json_markdown(json_path, payload, md_path, build_gap_plan_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_gap_plan_markdown(payload: dict[str, Any]) -> str:
    lines = ["# A-Share Execution Gap Plan", "", "## Scope", "This plan targets execution-rule blockers identified by v0.5.8.1.", "It does not start forward dry-run.", HARDENING_NOTICE, "", "## Baseline Day-1 Blockers", f"- baseline_day1_blocker_count: {payload['baseline_day1_blocker_count']}", "", "## Work Items"]
    lines.extend(f"- {item.get('work_id')}: {item.get('status')}" for item in payload["work_items"])
    lines.extend(["", "## Boundary", "- planning only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

