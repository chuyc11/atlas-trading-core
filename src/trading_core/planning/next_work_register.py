"""Recommend the next work package from MVP and day-1 blocker classifications."""

from __future__ import annotations

from typing import Any

from trading_core.planning.common import paths_or_default, read_dict, rel, resolve_path, standard_boundary
from trading_core.planning.day1_blocker_classifier import classify_day1_blockers
from trading_core.planning.mvp_gap_classifier import classify_mvp_gaps
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


EXECUTION_BLOCKER_IDS = {"R006", "R007", "R008", "R009", "R010", "R011"}


def build_next_work_register(
    *,
    mvp_gap_classification_path: str | None = None,
    day1_blocker_classification_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    register_id, created_at = timestamp_id("NEXT-WORK-REGISTER")
    gap_file = resolve_path(mvp_gap_classification_path, paths.data_dir / "system" / "mvp_gap_classification.json", paths)
    blocker_file = resolve_path(day1_blocker_classification_path, paths.data_dir / "system" / "day1_blocker_classification.json", paths)
    gap = read_dict(gap_file) or classify_mvp_gaps(paths=paths)
    day1 = read_dict(blocker_file) or classify_day1_blockers(paths=paths)
    recommendation = _recommend(gap, day1)
    payload: dict[str, Any] = {
        "register_id": register_id,
        "created_at": created_at,
        "mvp_gap_classification_path": rel(gap_file, paths),
        "day1_blocker_classification_path": rel(blocker_file, paths),
        "recommended_next_version": recommendation["version"],
        "reason": recommendation["reason"],
        "work_items": recommendation["work_items"],
        "boundary": standard_boundary("register_only"),
    }
    json_path = paths.data_dir / "system" / "next_work_register.json"
    md_path = paths.outputs_dir / "system" / "NEXT_WORK_REGISTER.md"
    write_json_markdown(json_path, payload, md_path, build_next_work_register_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _recommend(gap: dict[str, Any], day1: dict[str, Any]) -> dict[str, Any]:
    blockers = day1.get("blockers", [])
    blocked_ids = {item.get("requirement_id") for item in blockers}
    if blocked_ids & EXECUTION_BLOCKER_IDS:
        return {
            "version": "v0.5.9-ashare-execution-rules-hardening",
            "reason": "A-share execution rule blockers remain before day 1.",
            "work_items": _work_items(gap, blocked_ids & EXECUTION_BLOCKER_IDS, "v0.5.9", True),
        }
    by_id = {item["requirement_id"]: item for item in gap.get("requirements", [])}
    if by_id.get("R016", {}).get("status") != "passed":
        return {
            "version": "v0.6.0-baseline-strategy-pack",
            "reason": "Baseline strategy pack remains incomplete after execution blockers are cleared.",
            "work_items": _work_items(gap, {"R016"}, "v0.6.0", False),
        }
    if by_id.get("R017", {}).get("status") != "passed":
        return {
            "version": "v0.6.1-daily-workflow-binding",
            "reason": "Daily workflow binding remains incomplete after baseline strategy readiness.",
            "work_items": _work_items(gap, {"R017"}, "v0.6.1", True),
        }
    return {
        "version": "v0.6.2-forward-dry-run-start-authorization-pack",
        "reason": "No blockers remain, but manual confirmation is still incomplete.",
        "work_items": [{"work_id": "manual_forward_dry_run_start_authorization", "recommended_version": "v0.6.2", "required_before_day1": True}],
    }


def _work_items(gap: dict[str, Any], ids: set[str], version: str, required: bool) -> list[dict[str, Any]]:
    by_id = {item["requirement_id"]: item for item in gap.get("requirements", [])}
    return [
        {
            "work_id": by_id.get(requirement_id, {}).get("name", requirement_id),
            "requirement_id": requirement_id,
            "recommended_version": version,
            "required_before_day1": required,
            "status": by_id.get(requirement_id, {}).get("status"),
        }
        for requirement_id in sorted(ids)
    ]


def build_next_work_register_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Next Work Register",
        "",
        "## Recommended Next Version",
        payload["recommended_next_version"],
        "",
        "## Rationale",
        payload["reason"],
        "",
        "## Work Items",
    ]
    lines.extend(f"- {item['recommended_version']} {item['work_id']}: required_before_day1={str(item['required_before_day1']).lower()}" for item in payload["work_items"])
    lines.extend(["", "## Boundary", "- register only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

