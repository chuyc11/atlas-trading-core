"""Scope plan for the v0.6.0 baseline strategy pack."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown

from .common import (
    BASELINE_FROM,
    RELEASE_CANDIDATE,
    RESEARCH_NOTICE,
    STRATEGY_IDS,
    markdown_boundary,
    paths_or_default,
    read_dict,
    rel,
    research_boundary,
)


def build_baseline_strategy_scope_plan(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    plan_id, created_at = timestamp_id("BASELINE-STRATEGY-SCOPE-PLAN")
    reclassification_path = paths.data_dir / "system" / "day1_blocker_reclassification_v059.json"
    execution_audit_path = paths.data_dir / "system" / "ashare_execution_rules_audit.json"
    next_work_path = paths.data_dir / "system" / "next_work_register.json"
    plan_alignment_path = paths.data_dir / "system" / "plan_alignment_audit.json"
    reclassification = read_dict(reclassification_path)
    execution_audit = read_dict(execution_audit_path)
    execution_closed = (
        reclassification.get("updated_day1_blocker_count") == 0
        and execution_audit.get("overall_passed") is True
        and not execution_audit.get("blocking_reasons")
    )
    payload: dict[str, Any] = {
        "plan_id": plan_id,
        "created_at": created_at,
        "target_version": RELEASE_CANDIDATE,
        "baseline_from": BASELINE_FROM,
        "input_artifacts": {
            "day1_blocker_reclassification_v059": rel(reclassification_path, paths),
            "ashare_execution_rules_audit": rel(execution_audit_path, paths),
            "next_work_register": rel(next_work_path, paths) if next_work_path.exists() else None,
            "plan_alignment_audit": rel(plan_alignment_path, paths) if plan_alignment_path.exists() else None,
        },
        "execution_day1_blockers_closed": execution_closed,
        "baseline_strategy_pack_required": True,
        "forward_dry_run_day1_allowed": False,
        "strategies": list(STRATEGY_IDS),
        "boundary": research_boundary("planning_only"),
    }
    json_path = paths.data_dir / "system" / "baseline_strategy_scope_plan.json"
    md_path = paths.outputs_dir / "system" / "BASELINE_STRATEGY_SCOPE_PLAN.md"
    write_json_markdown(json_path, payload, md_path, build_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Baseline Strategy Scope Plan",
        "",
        "## Scope",
        "This plan defines the v0.6.0 baseline strategy pack.",
        "",
        "It does not start forward dry-run.",
        RESEARCH_NOTICE,
        "",
        "## Strategies",
    ]
    lines.extend(f"- {strategy_id}" for strategy_id in payload["strategies"])
    lines.extend(["", "## Boundary"])
    lines.extend(markdown_boundary("planning only"))
    lines.append("")
    return "\n".join(lines)

