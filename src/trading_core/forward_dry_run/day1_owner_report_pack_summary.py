"""Summarize the day1 owner report pack."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_owner_report_common import RECOMMENDED_NEXT_VERSION, REPORT_ARTIFACTS, build_simple_markdown, load_day1_owner_report_context, paths_or_default, project_path, report_boundary, write_report_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_day1_owner_report_pack_summary(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    context = load_day1_owner_report_context(paths)
    report_paths = {name: relative for name, relative in REPORT_ARTIFACTS.items() if name != "owner_report_pack_summary"}
    missing = [relative for relative in report_paths.values() if not project_path(paths, relative).exists()]
    payload: dict[str, Any] = {
        "summary_id": "FORWARD-DRY-RUN-DAY1-OWNER-REPORT-PACK-SUMMARY",
        "day_index": 1,
        "reports_total": 7,
        "reports_complete": 7 - len(missing),
        "missing_reports": missing,
        "owner_report_pack_complete": not missing,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "day2_input_readiness_evidence_found": context["day2_input_readiness_evidence_found"],
        "boundary": {
            **report_boundary("report_pack_only"),
            "report_pack_only": True,
            "day2_executed": False,
            "run_daily_called": False,
            "main_ledger_written": False,
            "broker_connected": False,
            "real_orders_placed": False,
        },
    }
    lines = [
        f"- reports_total: {payload['reports_total']}",
        f"- reports_complete: {payload['reports_complete']}",
        f"- missing_reports: {payload['missing_reports']}",
        f"- owner_report_pack_complete: {str(payload['owner_report_pack_complete']).lower()}",
        f"- recommended_next_version: {RECOMMENDED_NEXT_VERSION}",
    ]
    return write_report_artifact(paths, "day1_owner_report_pack_summary.json", payload, "DAY1_OWNER_REPORT_PACK_SUMMARY.md", build_simple_markdown("Day1 Owner Report Pack Summary", lines, payload))
