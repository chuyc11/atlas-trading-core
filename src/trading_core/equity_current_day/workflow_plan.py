"""Workflow plan for the A-share current-day runner."""

from __future__ import annotations

from typing import Any

from trading_core.equity_current_day.current_day_config import CURRENT_DAY_BOUNDARY, TARGET_VERSION
from trading_core.equity_workflows.workflow_config import stage_definitions, workflow_artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_current_day_workflow_plan(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    resolved_as_of_date: str,
    workflow_mode: str,
    run_post_workflow_modules: bool = False,
) -> dict[str, Any]:
    paths = default_paths(paths)
    workflow_command = (
        "python -m trading_core.cli run-and-audit-a-share-daily-research-workflow "
        f"--as-of-date {resolved_as_of_date} --mode {workflow_mode}"
    )
    artifacts = workflow_artifact_paths(paths, resolved_as_of_date)
    return {
        "plan_id": "A-SHARE-CURRENT-DAY-WORKFLOW-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "workflow_command": workflow_command,
        "workflow_mode": workflow_mode,
        "stage_order": [
            {"stage_id": stage["stage_id"], "stage_name": stage["stage_name"], "stage_order": stage["stage_order"]}
            for stage in stage_definitions(paths, resolved_as_of_date)
        ],
        "expected_stage_artifacts": {
            key: relative(path, paths.project_root)
            for key, path in artifacts.items()
            if "audit" not in key and path.suffix in {".json", ".md"}
        },
        "expected_audit_artifacts": {
            "workflow_audit_json": relative(artifacts["workflow_audit_json"], paths.project_root),
            "workflow_audit_report": relative(artifacts["workflow_audit_report"], paths.project_root),
        },
        "post_workflow_modules_enabled": run_post_workflow_modules,
        "post_workflow_commands": _post_workflow_commands(resolved_as_of_date) if run_post_workflow_modules else [],
        "boundary_expectations": dict(CURRENT_DAY_BOUNDARY),
    }


def _post_workflow_commands(as_of_date: str) -> list[str]:
    return [
        f"python -m trading_core.cli build-and-audit-a-share-benchmark-comparison --as-of-date {as_of_date}",
        f"python -m trading_core.cli build-and-audit-a-share-multi-day-performance --as-of-date {as_of_date}",
        f"python -m trading_core.cli build-and-audit-a-share-performance-attribution --as-of-date {as_of_date}",
    ]

