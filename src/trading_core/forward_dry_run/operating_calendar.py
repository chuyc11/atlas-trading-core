"""Forward dry-run operating calendar and daily log template."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from trading_core.forward_dry_run.common import DAY0_NOTICE, TRADING_AUTHORIZATION_NOTICE, paths_or_default, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_forward_dry_run_operating_calendar(*, start_date: str | None = None, trading_days: int = 30, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    calendar_id, created_at = timestamp_id("FWD-DRY-RUN-CALENDAR")
    dates = _trading_dates(start_date, trading_days) if start_date else [None] * trading_days
    days = [
        {
            "day_index": index + 1,
            "date": day,
            "status": "not_started",
            "run_daily_called": False,
            "expected_checks": ["data refresh check", "run-daily command preview", "output artifacts", "protected path check", "warning log", "manual note"],
            "expected_artifacts": [],
            "manual_note_required": True,
        }
        for index, day in enumerate(dates)
    ]
    payload: dict[str, Any] = {
        "calendar_id": calendar_id,
        "created_at": created_at,
        "calendar_status": "scheduled_template" if start_date else "template_only",
        "forward_dry_run_started": False,
        "trading_days_required": trading_days,
        "start_date": start_date,
        "days": days,
        "weekly_review_slots": [5, 10, 15, 20, 25, 30],
        "fail_closed_conditions": ["missing data", "consistency failure", "unexpected protected path mutation", "run-daily import boundary breach", "manual stop"],
        "interruption_rules": ["stop on blocker", "record manual note", "do not backfill without explicit review"],
        "restart_rules": ["restart only after new preflight and manual confirmation"],
        "forbidden_actions": ["broker connection", "real orders", "promotion", "live trading", "RL or LLM trading decisions"],
        "boundary": standard_boundary("calendar_only"),
    }
    json_path = paths.data_dir / "system" / "forward_dry_run_operating_calendar.json"
    md_path = paths.outputs_dir / "system" / "FORWARD_DRY_RUN_OPERATING_CALENDAR.md"
    log_path = paths.outputs_dir / "system" / "FORWARD_DRY_RUN_DAILY_LOG_TEMPLATE.md"
    write_json_markdown(json_path, payload, md_path, build_operating_calendar_markdown(payload))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(build_daily_log_template(payload), encoding="utf-8")
    return {**payload, "json_path": str(json_path), "report_path": str(md_path), "daily_log_template_path": str(log_path)}


def _trading_dates(start_date: str, trading_days: int) -> list[str]:
    current = date.fromisoformat(start_date)
    dates = []
    while len(dates) < trading_days:
        if current.weekday() < 5:
            dates.append(current.isoformat())
        current += timedelta(days=1)
    return dates


def build_operating_calendar_markdown(payload: dict[str, Any]) -> str:
    first = payload["days"][0] if payload["days"] else {}
    return "\n".join(
        [
            "# Forward Dry-Run Operating Calendar",
            "",
            "## Scope",
            "This is a calendar/template for a future 30 trading-day forward dry-run.",
            "It does not start the forward dry-run.",
            TRADING_AUTHORIZATION_NOTICE,
            "",
            "## Day Template",
            f"- status={first.get('status')}",
            "- expected checks: data refresh, command preview, artifacts, protected paths, warning log, manual note",
            "",
            "## Weekly Review",
            *[f"- day {day}" for day in payload["weekly_review_slots"]],
            "",
            "## Fail-Closed Rules",
            *[f"- {item}" for item in payload["fail_closed_conditions"]],
            "",
            "## Boundary",
            "- calendar only",
            "- forward dry-run not started",
            "- run-daily not called",
            "",
        ]
    )


def build_daily_log_template(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Forward Dry-Run Daily Log Template",
            "",
            "## Scope",
            DAY0_NOTICE,
            "",
            "## Daily Fields",
            "- date:",
            "- day_index:",
            "- data_refresh_check:",
            "- run_daily_command:",
            "- run_daily_called: false",
            "- output_artifacts:",
            "- protected_path_check:",
            "- warning_log:",
            "- manual_note:",
            "- stop_condition_triggered:",
            "",
            "## Boundary",
            "- template only",
            "- forward dry-run not started",
            "- run-daily not called",
            "",
        ]
    )
