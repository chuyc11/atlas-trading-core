"""Build A-share trading calendar foundation."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import TRADING_CALENDAR_COLUMNS, latest_weekday, markdown_boundary, utc_now, write_frame
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


OFFICIAL_ASHARE_HOLIDAYS = {
    2025: {
        "2025-01-01", "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31",
        "2025-02-03", "2025-02-04", "2025-04-04", "2025-05-01", "2025-05-02",
        "2025-05-05", "2025-06-02", "2025-10-01", "2025-10-02", "2025-10-03",
        "2025-10-06", "2025-10-07", "2025-10-08",
    },
    2026: {
        "2026-01-01", "2026-01-02", "2026-02-16", "2026-02-17", "2026-02-18",
        "2026-02-19", "2026-02-20", "2026-02-23", "2026-04-06", "2026-05-01",
        "2026-05-04", "2026-05-05", "2026-06-19", "2026-09-25", "2026-10-01",
        "2026-10-02", "2026-10-05", "2026-10-06", "2026-10-07",
    },
}
OFFICIAL_CALENDAR_SOURCE = "official_exchange_holiday_schedule_v1"
OFFICIAL_SOURCE_TIMESTAMPS = {2025: "2024-12-23", 2026: "2025-12-22"}


def build_a_share_trading_calendar(
    *,
    paths: ProjectPaths | None = None,
    end_date: str | None = None,
    lookback_days: int = 730,
    forward_days: int = 120,
    project_unsupported_horizon: bool = True,
) -> dict[str, Any]:
    paths = default_paths(paths)
    end = date.fromisoformat(end_date or latest_weekday())
    first_supported = date(min(OFFICIAL_ASHARE_HOLIDAYS), 1, 1)
    last_supported = date(max(OFFICIAL_ASHARE_HOLIDAYS), 12, 31)
    if end.year not in OFFICIAL_ASHARE_HOLIDAYS:
        raise ValueError(
            "Official A-share holiday coverage is required; missing years: "
            + ", ".join(str(year) for year in sorted({end.year} - set(OFFICIAL_ASHARE_HOLIDAYS)))
        )
    start = max(end - timedelta(days=lookback_days), first_supported)
    requested_end = end + timedelta(days=forward_days)
    missing_years = sorted(
        {year for year in range(end.year, requested_end.year + 1) if year not in OFFICIAL_ASHARE_HOLIDAYS}
    )
    horizon_end = requested_end if project_unsupported_horizon else min(requested_end, last_supported)
    horizon_clamped = (not project_unsupported_horizon) and requested_end > last_supported
    projected_years = sorted(year for year in missing_years if year > max(OFFICIAL_ASHARE_HOLIDAYS)) if project_unsupported_horizon else []
    warnings: list[str] = []
    if horizon_clamped:
        warnings.append(
            "forward planning horizon clamped to the last officially supported year "
            f"({last_supported.isoformat()}); official A-share holiday coverage required for: "
            + ", ".join(str(year) for year in missing_years)
        )
    if projected_years:
        warnings.append(
            "years beyond official holiday coverage use weekday projection "
            "(source=weekday_projection_v1); unknown 2027+ holidays (New Year, Spring Festival, ...) "
            "are NOT excluded until the official schedule is published: "
            + ", ".join(str(year) for year in projected_years)
        )
    dates = [
        start + timedelta(days=offset)
        for offset in range((horizon_end - start).days + 1)
    ]
    official_days = [item for item in dates if item.year in OFFICIAL_ASHARE_HOLIDAYS]
    projected_days = [item for item in dates if item.year not in OFFICIAL_ASHARE_HOLIDAYS]
    trading_days = [
        item for item in official_days
        if item.weekday() < 5 and item.isoformat() not in OFFICIAL_ASHARE_HOLIDAYS[item.year]
    ]
    if project_unsupported_horizon:
        trading_days.extend(item for item in projected_days if item.weekday() < 5)
    rows = []
    for exchange in ["SSE", "SZSE", "BSE"]:
        for index, day in enumerate(trading_days):
            previous_day = trading_days[index - 1].isoformat() if index > 0 else ""
            next_day = trading_days[index + 1].isoformat() if index + 1 < len(trading_days) else ""
            projected = day.year not in OFFICIAL_ASHARE_HOLIDAYS
            rows.append(
                {
                    "date": day.isoformat(),
                    "exchange": exchange,
                    "is_trading_day": True,
                    "previous_trading_day": previous_day,
                    "next_trading_day": next_day,
                    "source": "weekday_projection_v1" if projected else OFFICIAL_CALENDAR_SOURCE,
                    "source_timestamp": utc_now().split("T")[0] if projected else OFFICIAL_SOURCE_TIMESTAMPS[day.year],
                }
            )
    frame = pd.DataFrame(rows, columns=TRADING_CALENDAR_COLUMNS)
    parquet_path = paths.data_dir / "equity_universe" / "trading_calendar.parquet"
    json_path = paths.data_dir / "equity_universe" / "trading_calendar.json"
    write_frame(frame, parquet_path, json_path)
    report_path = paths.outputs_dir / "equity_universe" / "A_SHARE_TRADING_CALENDAR.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown(frame, requested_end, horizon_end, horizon_clamped, warnings), encoding="utf-8")
    return {
        "artifact_id": "A-SHARE-TRADING-CALENDAR",
        "target_version": "v0.7.1-a-share-full-market-data-ingestion",
        "trading_days": int(frame["date"].nunique()) if not frame.empty else 0,
        "min_date": str(frame["date"].min()) if not frame.empty else "",
        "max_date": str(frame["date"].max()) if not frame.empty else "",
        "forward_days_requested": forward_days,
        "forward_horizon_end": requested_end.isoformat(),
        "calendar_horizon_end": horizon_end.isoformat(),
        "horizon_clamped": horizon_clamped,
        "projected_years": projected_years,
        "warnings": warnings,
        "parquet_path": str(parquet_path),
        "json_path": str(json_path),
        "report_path": str(report_path),
    }


def _markdown(
    frame: pd.DataFrame,
    requested_end: date,
    horizon_end: date,
    horizon_clamped: bool,
    warnings: list[str],
) -> str:
    lines = [
        "# A-Share Trading Calendar",
        "",
        f"- source: {OFFICIAL_CALENDAR_SOURCE}",
        "- source_url: https://www.sse.com.cn/disclosure/dealinstruc/closed/",
        f"- exchanges: {', '.join(sorted(frame['exchange'].unique().tolist())) if not frame.empty else ''}",
        f"- trading_days: {frame['date'].nunique() if not frame.empty else 0}",
        f"- min_date: {frame['date'].min() if not frame.empty else ''}",
        f"- max_date: {frame['date'].max() if not frame.empty else ''}",
        f"- forward_horizon_end: {requested_end.isoformat()}",
        f"- calendar_horizon_end: {horizon_end.isoformat()}",
        f"- horizon_clamped: {str(horizon_clamped).lower()}",
        *warnings,
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return "\n".join(lines)
