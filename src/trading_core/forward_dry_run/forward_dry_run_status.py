"""Forward dry-run status after virtual day 1."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import non_claim_lines, paths_or_default, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_forward_dry_run_status(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    payload: dict[str, Any] = {
        "status_id": "FORWARD-DRY-RUN-STATUS",
        "forward_dry_run_started": True,
        "forward_dry_run_days_planned": 30,
        "forward_dry_run_days_completed": 1,
        "current_day_index": 1,
        "next_day_index": 2,
        "latest_completed_day_artifacts": ["data/forward_dry_run/day_001/day1_post_execution_audit.json"],
        "next_allowed_action": "forward_dry_run_day2_continuation_after_operator_review",
        "boundary": {
            "virtual_forward_dry_run_only": True,
            "real_trading": False,
            "broker_connected": False,
            "main_ledger_written": False,
        },
    }
    return write_artifact(system_json(paths, "forward_dry_run_status.json"), payload, system_report(paths, "FORWARD_DRY_RUN_STATUS.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Status",
        "",
        "- forward_dry_run_started: true",
        "- forward_dry_run_days_planned: 30",
        "- forward_dry_run_days_completed: 1",
        "- current_day_index: 1",
        "- next_day_index: 2",
        "- next_allowed_action: forward_dry_run_day2_continuation_after_operator_review",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)

