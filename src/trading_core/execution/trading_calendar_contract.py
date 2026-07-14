"""Trading calendar contract for SSE, SZSE, and HKEX."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from trading_core.execution.common import HARDENING_NOTICE, MARKETS, paths_or_default, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


DEFAULT_HOLIDAYS = {
    "SSE": {
        "2024-01-01", "2024-02-12", "2024-02-13", "2024-04-04", "2024-05-01", "2024-10-01",
        "2025-01-01", "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31", "2025-02-03", "2025-02-04",
        "2025-04-04", "2025-05-01", "2025-05-02", "2025-05-05", "2025-06-02", "2025-10-01", "2025-10-02",
        "2025-10-03", "2025-10-06", "2025-10-07", "2025-10-08",
        "2026-01-01", "2026-01-02", "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",
        "2026-02-23", "2026-04-06", "2026-05-01", "2026-05-04", "2026-05-05", "2026-06-19", "2026-09-25",
        "2026-10-01", "2026-10-02", "2026-10-05", "2026-10-06", "2026-10-07",
    },
    "SZSE": set(),
    "HKEX": {
        "2024-01-01", "2024-02-12", "2024-04-04", "2024-07-01", "2024-10-01", "2024-12-25",
        "2025-01-01", "2025-01-29", "2025-01-30", "2025-01-31", "2025-04-04", "2025-04-18", "2025-04-21",
        "2025-05-01", "2025-05-05", "2025-07-01", "2025-10-01", "2025-10-07", "2025-10-29", "2025-12-25", "2025-12-26",
        "2026-01-01", "2026-02-17", "2026-02-18", "2026-02-19", "2026-04-03", "2026-04-06", "2026-04-07",
        "2026-05-01", "2026-05-25", "2026-06-19", "2026-07-01", "2026-10-01", "2026-10-19", "2026-12-25",
    },
}
DEFAULT_HOLIDAYS["SZSE"] = set(DEFAULT_HOLIDAYS["SSE"])


@dataclass(frozen=True)
class TradingCalendarContract:
    holidays: dict[str, set[str]] = field(default_factory=lambda: {k: set(v) for k, v in DEFAULT_HOLIDAYS.items()})
    version: str = "ASHARE-TRADING-CALENDAR-CONTRACT-V2"
    source: str = "official_exchange_holiday_schedules_through_2026"

    def market_for_symbol(self, symbol: str) -> str:
        value = symbol.upper()
        if value.endswith(".SH") or value.startswith("SH"):
            return "SSE"
        if value.endswith(".SZ") or value.startswith("SZ"):
            return "SZSE"
        if value.endswith(".HK") or value.startswith("HK"):
            return "HKEX"
        if value.startswith(("510", "511", "512", "513", "515", "516", "588")):
            return "SSE"
        if value.startswith(("15", "16", "18")):
            return "SZSE"
        return "SSE"

    def is_trading_day(self, day: str | date, market: str) -> bool:
        parsed = _parse_date(day)
        market = _normalize_market(market)
        return parsed.weekday() < 5 and parsed.isoformat() not in self.holidays.get(market, set())

    def next_trading_day(self, day: str | date, market: str) -> str:
        current = _parse_date(day) + timedelta(days=1)
        while not self.is_trading_day(current, market):
            current += timedelta(days=1)
        return current.isoformat()

    def previous_trading_day(self, day: str | date, market: str) -> str:
        current = _parse_date(day) - timedelta(days=1)
        while not self.is_trading_day(current, market):
            current -= timedelta(days=1)
        return current.isoformat()

    def coverage(self) -> dict[str, Any]:
        return {market: {"holiday_count": len(self.holidays.get(market, set())), "weekend_handling": True} for market in MARKETS}


def default_calendar() -> TradingCalendarContract:
    return TradingCalendarContract()


def build_trading_calendar_contract(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    contract = default_calendar()
    payload: dict[str, Any] = {
        "contract_id": contract.version,
        "created_at": timestamp_id("ASHARE-TRADING-CALENDAR-CONTRACT")[1],
        "markets": MARKETS,
        "supports_market_symbol_resolution": True,
        "supports_next_trading_day": True,
        "supports_previous_trading_day": True,
        "weekend_handling": True,
        "explicit_holiday_list": {market: sorted(days) for market, days in contract.holidays.items()},
        "hkex_and_ashare_can_differ": True,
        "weekday_assumption_forbidden": True,
        "calendar_source": contract.source,
        "calendar_version": contract.version,
        "coverage": contract.coverage(),
        "boundary": standard_boundary("calendar_contract_only"),
    }
    json_path = paths.data_dir / "system" / "ashare_trading_calendar_contract.json"
    md_path = paths.outputs_dir / "system" / "ASHARE_TRADING_CALENDAR_CONTRACT.md"
    write_json_markdown(json_path, payload, md_path, build_calendar_contract_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def _normalize_market(market: str) -> str:
    market = market.upper()
    if market in {"A_SHARE", "SH", "SSE"}:
        return "SSE"
    if market in {"SZ", "SZSE"}:
        return "SZSE"
    if market in {"HK", "HKEX"}:
        return "HKEX"
    raise ValueError(f"Unsupported market: {market}")


def build_calendar_contract_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# A-Share Trading Calendar Contract",
        "",
        "## Scope",
        "This contract defines trading calendar behavior for SSE, SZSE, and HKEX.",
        HARDENING_NOTICE,
        "",
        "## Markets",
        ", ".join(payload["markets"]),
        "",
        "## Boundary",
        "- calendar contract only",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "",
    ]
    return "\n".join(lines)
