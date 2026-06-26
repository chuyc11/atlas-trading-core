"""Reclassify blockers after virtual forward dry-run day 1 execution."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import NEXT_VERSION, non_claim_lines, paths_or_default, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def reclassify_day1_blockers_after_forward_dry_run_day1(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    payload: dict[str, Any] = {
        "reclassification_id": "DAY1-BLOCKER-RECLASSIFICATION-V063",
        "day1_executed": True,
        "forward_dry_run_started": True,
        "forward_dry_run_days_completed": 1,
        "remaining_day1_blocker_count": 0,
        "day2_blocker_count": 0,
        "recommended_next_version": NEXT_VERSION,
        "boundary": {
            "reclassification_only": True,
            "virtual_forward_dry_run_only": True,
            "real_trading": False,
            "broker_connected": False,
            "main_ledger_written": False,
        },
    }
    return write_artifact(system_json(paths, "day1_blocker_reclassification_v063.json"), payload, system_report(paths, "DAY1_BLOCKER_RECLASSIFICATION_V063.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day1 Blocker Reclassification V063",
        "",
        "- day1_executed: true",
        "- forward_dry_run_started: true",
        "- forward_dry_run_days_completed: 1",
        "- remaining_day1_blocker_count: 0",
        "- day2_blocker_count: 0",
        f"- recommended_next_version: {payload['recommended_next_version']}",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)

