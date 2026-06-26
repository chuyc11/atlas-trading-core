"""Reclassify continuation artifact blockers after v0.6.3.1."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import non_claim_lines, paths_or_default, system_json, system_report, write_artifact
from trading_core.forward_dry_run.day1_continuation_common import NEXT_VERSION, read_json_file
from trading_core.storage.file_paths import ProjectPaths


def reclassify_day1_continuation_artifacts_v0631(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    audit = read_json_file(system_json(paths, "forward_dry_run_day1_continuation_artifact_audit.json"))
    gap_resolved = audit.get("overall_passed") is True
    payload: dict[str, Any] = {
        "reclassification_id": "DAY1-CONTINUATION-RECLASSIFICATION-V0631",
        "day1_core_execution_passed": True,
        "continuation_artifact_gap_resolved": gap_resolved,
        "remaining_continuation_artifact_gap_count": 0 if gap_resolved else 1,
        "day2_blocker_count": 0 if gap_resolved else 1,
        "day2_executed": False,
        "recommended_next_version": NEXT_VERSION,
        "boundary": {
            "reclassification_only": True,
            "day2_executed": False,
            "run_daily_called": False,
            "main_ledger_written": False,
            "real_trading": False,
            "broker_connected": False,
        },
    }
    return write_artifact(system_json(paths, "day1_continuation_reclassification_v0631.json"), payload, system_report(paths, "DAY1_CONTINUATION_RECLASSIFICATION_V0631.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day1 Continuation Reclassification V0631",
        "",
        f"- continuation_artifact_gap_resolved: {str(payload['continuation_artifact_gap_resolved']).lower()}",
        f"- remaining_continuation_artifact_gap_count: {payload['remaining_continuation_artifact_gap_count']}",
        f"- day2_blocker_count: {payload['day2_blocker_count']}",
        f"- recommended_next_version: {payload['recommended_next_version']}",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)

