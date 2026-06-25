"""Audit the A-share trading calendar contract."""

from __future__ import annotations

from typing import Any

from trading_core.execution.common import MARKETS, paths_or_default, read_dict, standard_boundary
from trading_core.execution.trading_calendar_contract import build_trading_calendar_contract, default_calendar
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def audit_trading_calendar(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    contract_path = paths.data_dir / "system" / "ashare_trading_calendar_contract.json"
    contract = read_dict(contract_path) or build_trading_calendar_contract(paths=paths)
    calendar = default_calendar()
    checks = [
        ("sse_weekday_trading_day", calendar.is_trading_day("2024-01-02", "SSE")),
        ("szse_weekday_trading_day", calendar.is_trading_day("2024-01-02", "SZSE")),
        ("hkex_weekday_trading_day", calendar.is_trading_day("2024-01-02", "HKEX")),
        ("weekend_non_trading", not calendar.is_trading_day("2024-01-06", "SSE")),
        ("explicit_holiday_non_trading", not calendar.is_trading_day("2024-10-01", "SSE")),
        ("next_trading_day_skips_weekend", calendar.next_trading_day("2024-01-05", "SSE") == "2024-01-08"),
        ("next_trading_day_skips_holiday", calendar.next_trading_day("2024-09-30", "SSE") == "2024-10-02"),
        ("previous_trading_day", calendar.previous_trading_day("2024-01-08", "SSE") == "2024-01-05"),
        ("hkex_and_ashare_differ", calendar.is_trading_day("2024-07-01", "SSE") and not calendar.is_trading_day("2024-07-01", "HKEX")),
        ("weekday_assumption_forbidden", contract.get("weekday_assumption_forbidden") is True),
    ]
    sections = [{"check_id": name, "passed": bool(passed)} for name, passed in checks]
    blocking = [item["check_id"] for item in sections if not item["passed"]]
    audit_id, created_at = timestamp_id("ASHARE-TRADING-CALENDAR-AUDIT")
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "markets": MARKETS,
        "contract_path": "data/system/ashare_trading_calendar_contract.json",
        "coverage": contract.get("coverage", {}),
        "sections": sections,
        "boundary": standard_boundary("calendar_audit_only"),
    }
    json_path = paths.data_dir / "system" / "ashare_trading_calendar_audit.json"
    md_path = paths.outputs_dir / "audit" / "ASHARE_TRADING_CALENDAR_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_calendar_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_calendar_audit_markdown(payload: dict[str, Any]) -> str:
    lines = ["# A-Share Trading Calendar Audit", "", "## Overall Verdict", f"- overall_passed={str(payload['overall_passed']).lower()}", "", "## Checks"]
    lines.extend(f"- {item['check_id']}: {str(item['passed']).lower()}" for item in payload["sections"])
    lines.extend(["", "## Boundary", "- calendar audit only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

