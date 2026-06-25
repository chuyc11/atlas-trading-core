"""Scope plan for v0.6.1 daily workflow binding."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id

from .common import BASELINE_FROM, NOTICE, RELEASE_CANDIDATE, WORKFLOW_COMPONENTS, boundary_markdown, paths_or_default, read_json_file, rel, workflow_boundary, write_artifact


def build_daily_workflow_scope_plan(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    plan_id, created_at = timestamp_id("DAILY-WORKFLOW-SCOPE-PLAN")
    audit_path = paths.data_dir / "system" / "baseline_strategy_pack_audit.json"
    v060_path = paths.data_dir / "system" / "day1_blocker_reclassification_v060.json"
    summary_path = paths.data_dir / "strategies" / "baseline_strategy_pack_summary.json"
    baseline_audit = read_json_file(audit_path)
    baseline_summary = read_json_file(summary_path)
    payload: dict[str, Any] = {
        "plan_id": plan_id,
        "created_at": created_at,
        "target_version": RELEASE_CANDIDATE,
        "baseline_from": BASELINE_FROM,
        "input_artifacts": {
            "baseline_strategy_pack_audit": rel(audit_path, paths),
            "day1_blocker_reclassification_v060": rel(v060_path, paths),
            "baseline_strategy_pack_summary": rel(summary_path, paths),
            "ashare_execution_rules_audit": "data/system/ashare_execution_rules_audit.json",
            "plan_alignment_audit": "data/system/plan_alignment_audit.json",
        },
        "baseline_strategy_pack_complete": baseline_audit.get("overall_passed") is True and baseline_summary.get("all_strategies_complete") is True,
        "daily_workflow_binding_required": True,
        "forward_dry_run_day1_allowed": False,
        "workflow_components": list(WORKFLOW_COMPONENTS),
        "run_daily_command_preview": run_daily_preview_placeholder(),
        "boundary": workflow_boundary("planning_only"),
    }
    json_path = paths.data_dir / "system" / "daily_workflow_scope_plan.json"
    md_path = paths.outputs_dir / "system" / "DAILY_WORKFLOW_SCOPE_PLAN.md"
    return write_artifact(json_path, payload, md_path, build_markdown(payload))


def run_daily_preview_placeholder() -> dict[str, Any]:
    return {"preview_only": True, "executed": False, "run_daily_called": False}


def build_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Daily Workflow Scope Plan", "", NOTICE, "", "## Components"]
    lines.extend(f"- {item}" for item in payload["workflow_components"])
    lines.extend(["", "## Boundary"])
    lines.extend(boundary_markdown("planning only"))
    lines.append("")
    return "\n".join(lines)

