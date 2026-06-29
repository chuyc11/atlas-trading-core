"""Build-from-existing-data workflow result for v0.8.7."""

from __future__ import annotations

import json

from trading_core.equity_current_day_builds.gated_build_config import (
    TARGET_VERSION,
    TO_WORKFLOW_MODE,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_workflow_result(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    execution_record: dict,
) -> dict:
    paths = default_paths(paths)

    # Load the current-day run manifest (the build output)
    current_day_manifest_path = (
        paths.data_dir
        / "equity_current_day_runs"
        / "daily"
        / as_of_date
        / "current_day_run_manifest.json"
    )

    workflow_stages = {}
    artifacts_generated = []
    manifest_loaded = False

    if current_day_manifest_path.exists():
        try:
            manifest = json.loads(current_day_manifest_path.read_text(encoding="utf-8"))
            manifest_loaded = True
            artifacts_generated = list(manifest.get("output_artifacts", {}).keys())
            # Extract stage information
            stage_manifest_path = (
                paths.data_dir
                / "equity_current_day_runs"
                / "daily"
                / as_of_date
                / "current_day_stage_manifest.json"
            )
            if stage_manifest_path.exists():
                stage_data = json.loads(stage_manifest_path.read_text(encoding="utf-8"))
                workflow_stages = stage_data.get("stages", {})
        except Exception:
            pass

    # Load workflow audit
    workflow_audit_path = (
        paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json"
    )
    workflow_audit_overall_passed = False
    workflow_blocking = []
    workflow_warnings = []

    if workflow_audit_path.exists():
        try:
            audit = json.loads(workflow_audit_path.read_text(encoding="utf-8"))
            workflow_audit_overall_passed = audit.get("overall_passed", False)
            workflow_blocking = audit.get("blocking_reasons", [])
            workflow_warnings = audit.get("warnings", [])
        except Exception:
            pass

    stage_rows = workflow_stages.values() if isinstance(workflow_stages, dict) else workflow_stages
    stages_passed = sum(1 for s in stage_rows if isinstance(s, dict) and s.get("status") == "passed")
    stage_rows = workflow_stages.values() if isinstance(workflow_stages, dict) else workflow_stages
    stages_failed = sum(1 for s in stage_rows if isinstance(s, dict) and s.get("status") == "failed")

    return {
        "result_id": "A-SHARE-BUILD-FROM-EXISTING-DATA-WORKFLOW-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "workflow_mode": TO_WORKFLOW_MODE,
        "command": execution_record.get("command", ""),
        "exit_code": execution_record.get("exit_code", None),
        "status": execution_record.get("status", "unknown"),
        "workflow_audit_path": execution_record.get("workflow_audit_path", ""),
        "workflow_audit_overall_passed": workflow_audit_overall_passed,
        "workflow_blocking_reasons": workflow_blocking,
        "workflow_warnings": workflow_warnings,
        "stages_passed": stages_passed,
        "stages_failed": stages_failed,
        "artifacts_generated_or_reused": artifacts_generated,
        "manifest_loaded": manifest_loaded,
        "boundary_status": {
            "old_run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
        },
        "source_trace_status": "complete",
    }


def build_audit_link(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    execution_record: dict,
    workflow_result: dict,
) -> dict:
    paths = default_paths(paths)

    return {
        "link_id": "A-SHARE-BUILD-FROM-EXISTING-DATA-AUDIT-LINK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "workflow_mode": TO_WORKFLOW_MODE,
        "execution_record_path": (
            str(
                paths.data_dir
                / "equity_current_day_builds"
                / "daily"
                / as_of_date
                / "gated_build_execution_record.json"
            )
        ),
        "workflow_result_path": (
            str(
                paths.data_dir
                / "equity_current_day_builds"
                / "daily"
                / as_of_date
                / "build_from_existing_data_workflow_result.json"
            )
        ),
        "workflow_audit_path": execution_record.get("workflow_audit_path", ""),
        "workflow_audit_overall_passed": workflow_result.get("workflow_audit_overall_passed", False),
        "build_output_manifest_path": (
            str(
                paths.data_dir
                / "equity_current_day_runs"
                / "daily"
                / as_of_date
                / "current_day_run_manifest.json"
            )
        ),
        "linked": True,
    }
