"""Reclassify day-1 blockers after v0.6.1 daily workflow binding."""

from __future__ import annotations

from typing import Any

from trading_core.execution.common import read_dict, rel
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown
from trading_core.daily_workflow.common import NEXT_VERSION, NOTICE, paths_or_default, workflow_boundary


def reclassify_day1_blockers_after_daily_workflow(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    reclassification_id, created_at = timestamp_id("DAY1-BLOCKER-RECLASSIFICATION-V061")
    v060_path = paths.data_dir / "system" / "day1_blocker_reclassification_v060.json"
    audit_path = paths.data_dir / "system" / "daily_workflow_audit.json"
    v060 = read_dict(v060_path)
    audit = read_dict(audit_path)
    closed = audit.get("overall_passed") is True and not audit.get("blocking_reasons")
    previous_count = int(v060.get("updated_day1_blocker_count", 0) or 0)
    updated_count = 0 if closed and previous_count == 0 else max(previous_count, 1)
    payload: dict[str, Any] = {
        "reclassification_id": reclassification_id,
        "created_at": created_at,
        "input_artifacts": {
            "day1_blocker_reclassification_v060": rel(v060_path, paths) if v060_path.exists() else None,
            "daily_workflow_audit": rel(audit_path, paths) if audit_path.exists() else None,
        },
        "daily_workflow_blocker_closed": closed,
        "updated_day1_blocker_count": updated_count,
        "recommended_next_version": NEXT_VERSION,
        "day1_start_allowed": False,
        "manual_confirmation_complete": False,
        "forward_dry_run_start_authorized": False,
        "run_daily_called": False,
        "forward_dry_run_started": False,
        "main_ledger_written": False,
        "boundary": workflow_boundary("reclassification_only"),
    }
    json_path = paths.data_dir / "system" / "day1_blocker_reclassification_v061.json"
    md_path = paths.outputs_dir / "system" / "DAY1_BLOCKER_RECLASSIFICATION_V061.md"
    write_json_markdown(json_path, payload, md_path, build_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day-1 Blocker Reclassification V061",
        "",
        NOTICE,
        "",
        "## Summary",
        f"- daily_workflow_blocker_closed: {str(payload['daily_workflow_blocker_closed']).lower()}",
        f"- updated_day1_blocker_count: {payload['updated_day1_blocker_count']}",
        f"- recommended_next_version: {payload['recommended_next_version']}",
        "- day1_start_allowed=false",
        "- manual_confirmation_complete=false",
        "- forward_dry_run_start_authorized=false",
        "",
        "## Boundary",
        "- reclassification only",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "",
    ]
    return "\n".join(lines)

