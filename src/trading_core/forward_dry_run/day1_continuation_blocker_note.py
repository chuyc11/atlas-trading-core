"""Build the day1 continuation blocker note."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_owner_report_common import DAY1_AS_OF_DATE, LATEST_COMMON_LOCAL_DATA_DATE, build_simple_markdown, load_day1_owner_report_context, paths_or_default, report_boundary, write_report_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_day1_continuation_blocker_note(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    context = load_day1_owner_report_context(paths)
    warnings = []
    if not context["day2_input_readiness_evidence_found"]:
        warnings.append("day2 input readiness evidence not found")
    payload: dict[str, Any] = {
        "note_id": "FORWARD-DRY-RUN-DAY1-CONTINUATION-BLOCKER-NOTE",
        "day1_completed": True,
        "day2_executed": False,
        "blocker_type": "local_data_horizon_insufficient",
        "latest_common_local_data_date": LATEST_COMMON_LOCAL_DATA_DATE,
        "day1_as_of_date": DAY1_AS_OF_DATE,
        "blocker_not_caused_by": ["strategy", "ledger", "authorization", "boundary"],
        "next_required_action": "extend_local_authorized_data_horizon_before_retrying_day2",
        "warnings": warnings,
        "boundary": {
            **report_boundary("note_only"),
            "note_only": True,
            "day2_executed": False,
            "run_daily_called": False,
            "external_api_called": False,
            "real_time_market_data_downloaded": False,
            "main_ledger_written": False,
        },
    }
    lines = [
        "- day1_completed: true",
        "- day2_executed: false",
        "- blocker_type: local_data_horizon_insufficient",
        f"- latest_common_local_data_date: {LATEST_COMMON_LOCAL_DATA_DATE}",
        f"- day1_as_of_date: {DAY1_AS_OF_DATE}",
        "- blocker_not_caused_by: strategy, ledger, authorization, or boundary",
        "- next_required_action: extend_local_authorized_data_horizon_before_retrying_day2",
    ]
    return write_report_artifact(paths, "day1_continuation_blocker_note.json", payload, "DAY1_CONTINUATION_BLOCKER_NOTE.md", build_simple_markdown("Day1 Continuation Blocker Note", lines, payload))
