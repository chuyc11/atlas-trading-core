"""Day-0 readiness summary report."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.common import TRADING_AUTHORIZATION_NOTICE, paths_or_default, read_dict, rel, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_day0_readiness_report(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    report_id, created_at = timestamp_id("DAY0-READINESS-REPORT")
    freeze_path = paths.data_dir / "system" / "day0_data_freeze_manifest.json"
    warning_path = paths.data_dir / "system" / "day0_accepted_warning_register.json"
    conditions_path = paths.data_dir / "system" / "day0_blocking_conditions.json"
    preflight_path = paths.data_dir / "system" / "day0_run_daily_preflight.json"
    manual_path = paths.data_dir / "system" / "day0_manual_confirmation_packet.json"
    calendar_path = paths.data_dir / "system" / "forward_dry_run_operating_calendar.json"
    freeze = read_dict(freeze_path)
    warning = read_dict(warning_path)
    conditions = read_dict(conditions_path)
    preflight = read_dict(preflight_path)
    manual = read_dict(manual_path)
    calendar = read_dict(calendar_path)
    sections = {
        "data_freeze": {"status": "passed" if freeze.get("overall_passed") else "missing_or_failed", "path": rel(freeze_path, paths)},
        "warning_register": {"status": "passed" if warning.get("blocking_count", 1) == 0 else "failed", "blocking_count": warning.get("blocking_count")},
        "blocking_conditions": {"status": "passed" if conditions.get("current_blocking_count", 1) == 0 else "failed", "current_blocking_count": conditions.get("current_blocking_count"), "manual_confirmation_required": conditions.get("manual_confirmation_still_required")},
        "preflight": {"status": "passed" if preflight.get("overall_passed") else "failed", "run_daily_executed": preflight.get("run_daily_command_preview", {}).get("executed")},
        "manual_confirmation": {"status": "pending_manual_confirmation", "manual_confirmation_complete": manual.get("manual_confirmation_complete", False)},
        "operating_calendar": {"status": calendar.get("calendar_status", "missing")},
    }
    payload: dict[str, Any] = {
        "report_id": report_id,
        "created_at": created_at,
        "overall_status": "ready_for_manual_confirmation",
        "forward_dry_run_started": False,
        "run_daily_called": False,
        "sections": sections,
        "can_start_forward_dry_run_without_manual_confirmation": False,
        "boundary": standard_boundary("report_only"),
    }
    json_path = paths.data_dir / "system" / "day0_readiness_report.json"
    md_path = paths.outputs_dir / "system" / "DAY0_READINESS_REPORT.md"
    write_json_markdown(json_path, payload, md_path, build_readiness_report_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_readiness_report_markdown(payload: dict[str, Any]) -> str:
    passed = [name for name, section in payload["sections"].items() if section.get("status") in {"passed", "template_only", "pending_manual_confirmation"}]
    return "\n".join(
        [
            "# Day-0 Readiness Report",
            "",
            "## Overall Status",
            payload["overall_status"],
            "",
            "## What Passed",
            *[f"- {item}" for item in passed],
            "",
            "## What Still Requires Manual Confirmation",
            "- manual confirmation remains incomplete by default",
            "- owner must explicitly confirm before any future day 1",
            "",
            "## Explicit Non-Claims",
            "- This does not start forward dry-run.",
            "- This does not validate forward dry-run.",
            "- This does not prove strategy effectiveness.",
            "- This is not live trading readiness.",
            f"- {TRADING_AUTHORIZATION_NOTICE}",
            "",
            "## Boundary",
            "- report only",
            "- run-daily not called",
            "- main ledger not written",
            "",
        ]
    )
