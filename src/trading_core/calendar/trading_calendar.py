"""Trading calendar helpers with explicit A-share calendar degradation."""

from __future__ import annotations

from datetime import date as Date, datetime, timedelta
from pathlib import Path
from typing import Any
import json
import warnings

from trading_core.storage.file_paths import ProjectPaths, project_paths


def parse_date(value: str | Date) -> Date:
    if isinstance(value, Date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def format_date(value: Date) -> str:
    return value.isoformat()


def is_trading_day(
    date: str | Date,
    market: str = "A_SHARE",
    *,
    paths: ProjectPaths | None = None,
    calendar_path: Path | str | None = None,
    allow_degraded: bool = True,
) -> bool:
    status = calendar_status(date, market=market, paths=paths, calendar_path=calendar_path)
    if status["status"] == "degraded":
        if not allow_degraded:
            raise RuntimeError(status["warning"])
        warnings.warn(status["warning"], RuntimeWarning, stacklevel=2)
    return bool(status["is_trading_day"])


def calendar_status(date: str | Date, market: str = "A_SHARE", *, paths: ProjectPaths | None = None, calendar_path: Path | str | None = None) -> dict[str, Any]:
    current = parse_date(date)
    if market != "A_SHARE":
        return {"date": current.isoformat(), "market": market, "is_trading_day": current.weekday() < 5, "status": "weekday_fallback", "warning": None}

    calendar = _load_external_calendar(paths=paths, calendar_path=calendar_path)
    if calendar is not None:
        value = calendar.get(current.isoformat())
        if value is not None:
            return {"date": current.isoformat(), "market": market, "is_trading_day": value, "status": "calendar_file", "warning": None}
        if calendar and min(calendar) <= current.isoformat() <= max(calendar):
            return {
                "date": current.isoformat(),
                "market": market,
                "is_trading_day": False,
                "status": "calendar_file_inferred_closed_date",
                "warning": None,
            }
        return {
            "date": current.isoformat(),
            "market": market,
            "is_trading_day": False,
            "status": "calendar_file_missing_date",
            "warning": f"A-share trading calendar loaded but date {current.isoformat()} is absent",
        }
    return {
        "date": current.isoformat(),
        "market": market,
        "is_trading_day": current.weekday() < 5,
        "status": "degraded",
        "warning": "A-share trading calendar file unavailable; using weekday fallback only",
    }


def require_a_share_calendar(
    *,
    paths: ProjectPaths | None = None,
    calendar_path: Path | str | None = None,
    market: str = "A_SHARE",
    as_of_date: str | Date | None = None,
    minimum_forward_days: int = 0,
) -> dict[str, Any]:
    if market != "A_SHARE":
        return {"passed": True, "market": market, "status": "not_required", "warning": None}
    calendar = _load_external_calendar(paths=paths, calendar_path=calendar_path)
    if not calendar:
        return {
            "passed": False,
            "market": market,
            "status": "missing_calendar",
            "warning": "formal A-share backtest requires an exchange trading calendar file; weekday fallback is degraded only",
        }
    minimum_date = min(calendar)
    maximum_date = max(calendar)
    coverage_warning: str | None = None
    coverage_days: int | None = None
    if as_of_date is not None:
        requested = parse_date(as_of_date)
        coverage_days = (parse_date(maximum_date) - requested).days
        if requested.isoformat() < minimum_date or requested.isoformat() > maximum_date:
            coverage_warning = (
                f"A-share trading calendar does not cover {requested.isoformat()}; "
                f"available range is {minimum_date} through {maximum_date}"
            )
        elif coverage_days < minimum_forward_days:
            coverage_warning = (
                f"A-share trading calendar has only {coverage_days} forward calendar days "
                f"from {requested.isoformat()}; at least {minimum_forward_days} are required"
            )
    return {
        "passed": coverage_warning is None,
        "market": market,
        "status": "calendar_file" if coverage_warning is None else "calendar_coverage_insufficient",
        "trading_day_count": sum(1 for value in calendar.values() if value),
        "closed_day_count": sum(1 for value in calendar.values() if not value),
        "minimum_date": minimum_date,
        "maximum_date": maximum_date,
        "forward_calendar_days": coverage_days,
        "warning": coverage_warning,
    }


def next_trading_day(
    date: str | Date,
    market: str = "A_SHARE",
    *,
    paths: ProjectPaths | None = None,
    calendar_path: Path | str | None = None,
    allow_degraded: bool = True,
) -> str:
    current = parse_date(date) + timedelta(days=1)
    for _attempt in range(370):
        status = calendar_status(current, market=market, paths=paths, calendar_path=calendar_path)
        if status["status"] == "calendar_file_missing_date":
            raise ValueError(status["warning"])
        if is_trading_day(current, market, paths=paths, calendar_path=calendar_path, allow_degraded=allow_degraded):
            return format_date(current)
        current += timedelta(days=1)
    raise ValueError(f"No next trading day found within 370 calendar days after {format_date(parse_date(date))}")


def previous_trading_day(
    date: str | Date,
    market: str = "A_SHARE",
    *,
    paths: ProjectPaths | None = None,
    calendar_path: Path | str | None = None,
    allow_degraded: bool = True,
) -> str:
    current = parse_date(date) - timedelta(days=1)
    for _attempt in range(370):
        status = calendar_status(current, market=market, paths=paths, calendar_path=calendar_path)
        if status["status"] == "calendar_file_missing_date":
            raise ValueError(status["warning"])
        if is_trading_day(current, market, paths=paths, calendar_path=calendar_path, allow_degraded=allow_degraded):
            return format_date(current)
        current -= timedelta(days=1)
    raise ValueError(f"No previous trading day found within 370 calendar days before {format_date(parse_date(date))}")


def _load_external_calendar(*, paths: ProjectPaths | None, calendar_path: Path | str | None) -> dict[str, bool] | None:
    candidates: list[Path]
    if calendar_path is not None:
        candidates = [Path(calendar_path)]
    else:
        active_paths = paths or project_paths()
        candidates = [
            active_paths.data_dir / "equity_universe" / "trading_calendar.json",
            active_paths.data_dir / "equity_universe" / "trading_calendar.csv",
            active_paths.data_dir / "equity_universe" / "trading_calendar.parquet",
            active_paths.data_dir / "calendar" / "a_share_trading_calendar.json",
        ]
    for candidate in candidates:
        if candidate.exists():
            return _read_calendar_file(candidate)
    return None


def _read_calendar_file(path: Path) -> dict[str, bool]:
    if path.suffix.lower() == ".parquet":
        import pandas as pd

        frame = pd.read_parquet(path)
        return _calendar_from_rows(frame.to_dict("records"))
    if path.suffix.lower() == ".csv":
        import csv

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return _calendar_from_rows(csv.DictReader(handle))
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", payload) if isinstance(payload, dict) else payload
    return _calendar_from_rows(rows)


def _calendar_from_rows(rows: Any) -> dict[str, bool]:
    result: dict[str, bool] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        date_value = row.get("date") or row.get("trade_date")
        if date_value is None:
            continue
        key = str(date_value)[:10]
        raw = row.get("is_trading_day", row.get("is_open", row.get("open", row.get("trading"))))
        result[key] = _as_bool(raw)
    return result


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "open", "trading"}
