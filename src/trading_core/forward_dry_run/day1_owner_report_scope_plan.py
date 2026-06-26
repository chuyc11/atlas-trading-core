"""Build the v0.6.3.2 day1 owner report scope plan."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_owner_report_common import BASELINE_FROM, TARGET_VERSION, owner_non_claim_lines, paths_or_default, report_boundary, scope_plan_system_paths
from trading_core.forward_dry_run.day1_common import write_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_day1_owner_report_scope_plan(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    payload: dict[str, Any] = {
        "scope_plan_id": "FORWARD-DRY-RUN-DAY1-OWNER-REPORT-SCOPE-PLAN",
        "target_version": TARGET_VERSION,
        "baseline_from": BASELINE_FROM,
        "report_only": True,
        "day1_executed": True,
        "day2_execution_allowed": False,
        "day3_execution_allowed": False,
        "report_sections": [
            "owner_summary",
            "strategy_signal_explanation",
            "virtual_order_fill_report",
            "isolated_ledger_report",
            "risk_boundary_report",
            "data_reproducibility_appendix",
            "day2_blocker_note",
        ],
        "boundary": {
            "report_generation_only": True,
            "run_daily_called": False,
            "day2_executed": False,
            "main_ledger_written": False,
            "broker_connected": False,
            "real_orders_placed": False,
        },
    }
    json_path, report_path = scope_plan_system_paths(paths)
    lines = [
        "# Forward Dry-Run Day1 Owner Report Scope Plan",
        "",
        f"- target_version: {TARGET_VERSION}",
        f"- baseline_from: {BASELINE_FROM}",
        "- report_only: true",
        "- day2_execution_allowed: false",
        "",
        "## Sections",
        *[f"- {section}" for section in payload["report_sections"]],
        "",
        "## Boundary",
        *owner_non_claim_lines(),
        "",
    ]
    return write_artifact(json_path, payload, report_path, "\n".join(lines))
