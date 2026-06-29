"""Repeat build workflow result summary."""

from __future__ import annotations

import json

from trading_core.equity_build_repeatability.repeatability_config import TARGET_VERSION, WORKFLOW_MODE
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_repeat_build_workflow_result(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    execution_record: dict,
) -> dict:
    paths = default_paths(paths)
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json"
    execution_path = (
        paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date / "current_day_workflow_execution.json"
    )
    stage_path = (
        paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date / "current_day_stage_manifest.json"
    )
    audit = _load(audit_path)
    execution = _load(execution_path)
    stages = _load(stage_path).get("stages", [])
    stage_values = stages.values() if isinstance(stages, dict) else stages
    failed = [s for s in stage_values if isinstance(s, dict) and s.get("status") not in {"passed", "skipped"}]
    return {
        "result_id": "A-SHARE-REPEAT-BUILD-WORKFLOW-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "workflow_mode": WORKFLOW_MODE,
        "execution_status": execution_record.get("status"),
        "exit_code": execution_record.get("exit_code"),
        "workflow_audit_path": relative(audit_path, paths.project_root) if audit_path.exists() else "",
        "workflow_audit_overall_passed": audit.get("overall_passed", False) is True,
        "workflow_execution_path": relative(execution_path, paths.project_root) if execution_path.exists() else "",
        "stage_manifest_path": relative(stage_path, paths.project_root) if stage_path.exists() else "",
        "stage_count": len(list(stage_values)) if not isinstance(stages, dict) else len(stages),
        "failed_stage_count": len(failed),
        "blocking_reasons": sorted(set(execution_record.get("blocking_reasons", []) + audit.get("blocking_reasons", []))),
        "warnings": sorted(set(execution_record.get("warnings", []) + audit.get("warnings", []))),
    }


def _load(path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

