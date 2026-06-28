"""Trading-day date resolution for A-share data refresh."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from trading_core.equity_data_refresh.data_refresh_config import DEFAULT_AS_OF_DATE, DEFAULT_TIMEZONE, TARGET_VERSION
from trading_core.equity_data_refresh.dataset_contracts import dataset_contracts, load_dataset_frame, resolve_column
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def resolve_data_refresh_date(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str | None = DEFAULT_AS_OF_DATE,
    resolve_latest_completed_trading_day: bool = False,
    allow_intraday_research_refresh: bool = False,
    allow_non_trading_day: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    contract = dataset_contracts()["trading_calendar"]
    frame = load_dataset_frame(paths, contract)
    date_col = resolve_column(frame, contract, "trade_date")
    is_open_col = resolve_column(frame, contract, "is_open")
    trading_dates = _trading_dates(frame, date_col, is_open_col)
    requested_mode = "latest_completed_trading_day" if resolve_latest_completed_trading_day else "explicit_as_of_date"
    requested = "latest_available" if resolve_latest_completed_trading_day else str(as_of_date or "")
    blocking: list[str] = []
    warnings: list[str] = []
    if not trading_dates:
        blocking.append("trading_calendar_unavailable")
        resolved = str(as_of_date or "")
    elif resolve_latest_completed_trading_day:
        resolved = _latest_completed(trading_dates, allow_intraday_research_refresh=allow_intraday_research_refresh, now=now)
        if not resolved:
            blocking.append("no_completed_trading_day_available")
    else:
        resolved = str(as_of_date or "")
        if resolved not in trading_dates and not allow_non_trading_day:
            blocking.append("as_of_date_is_not_trading_day")
    previous = max([day for day in trading_dates if day < resolved], default="")
    next_day = min([day for day in trading_dates if day > resolved], default="")
    is_trading_day = resolved in trading_dates
    if not is_trading_day and allow_non_trading_day:
        warnings.append("non_trading_day_allowed_explicitly")
    return {
        "resolution_id": "A-SHARE-DATA-REFRESH-DATE-RESOLUTION",
        "target_version": TARGET_VERSION,
        "requested_date": requested,
        "resolved_as_of_date": resolved,
        "requested_date_mode": requested_mode,
        "is_trading_day": is_trading_day,
        "is_completed_trading_day": is_trading_day and resolved <= _current_local_date(now),
        "calendar_source": relative(contract.source_path(paths), paths.project_root),
        "previous_completed_trading_day": previous,
        "next_trading_day": next_day,
        "allow_intraday_research_refresh": allow_intraday_research_refresh,
        "allow_non_trading_day": allow_non_trading_day,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }


def _trading_dates(frame: pd.DataFrame, date_col: str | None, is_open_col: str | None) -> list[str]:
    if frame.empty or date_col is None:
        return []
    rows = frame
    if is_open_col is not None:
        rows = rows[rows[is_open_col].astype(bool)]
    return sorted(set(rows[date_col].astype(str).str[:10]))


def _latest_completed(trading_dates: list[str], *, allow_intraday_research_refresh: bool, now: datetime | None) -> str:
    current_date = _current_local_date(now)
    candidates = [day for day in trading_dates if day <= current_date]
    if not candidates:
        return ""
    latest = max(candidates)
    current_dt = now.astimezone(ZoneInfo(DEFAULT_TIMEZONE)) if now is not None else datetime.now(ZoneInfo(DEFAULT_TIMEZONE))
    if latest == current_date and not allow_intraday_research_refresh and current_dt.time() < time(15, 30):
        previous = [day for day in candidates if day < latest]
        return max(previous) if previous else ""
    return latest


def _current_local_date(now: datetime | None) -> str:
    current = now.astimezone(ZoneInfo(DEFAULT_TIMEZONE)) if now is not None else datetime.now(ZoneInfo(DEFAULT_TIMEZONE))
    return current.date().isoformat()
