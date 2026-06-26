"""Build A-share trading calendar foundation."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import TRADING_CALENDAR_COLUMNS, latest_weekday, markdown_boundary, utc_now, write_frame
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_a_share_trading_calendar(*, paths: ProjectPaths | None = None, end_date: str | None = None, lookback_days: int = 365) -> dict[str, Any]:
    paths = default_paths(paths)
    end = date.fromisoformat(end_date or latest_weekday())
    start = end - timedelta(days=lookback_days)
    dates = [start + timedelta(days=offset) for offset in range((end - start).days + 31)]
    trading_days = [item for item in dates if item.weekday() < 5]
    rows = []
    for exchange in ["SSE", "SZSE", "BSE"]:
        for index, day in enumerate(trading_days):
            previous_day = trading_days[index - 1].isoformat() if index > 0 else ""
            next_day = trading_days[index + 1].isoformat() if index + 1 < len(trading_days) else ""
            rows.append(
                {
                    "date": day.isoformat(),
                    "exchange": exchange,
                    "is_trading_day": True,
                    "previous_trading_day": previous_day,
                    "next_trading_day": next_day,
                    "source": "weekday_calendar_v1",
                    "source_timestamp": utc_now(),
                }
            )
    frame = pd.DataFrame(rows, columns=TRADING_CALENDAR_COLUMNS)
    parquet_path = paths.data_dir / "equity_universe" / "trading_calendar.parquet"
    json_path = paths.data_dir / "equity_universe" / "trading_calendar.json"
    write_frame(frame, parquet_path, json_path)
    report_path = paths.outputs_dir / "equity_universe" / "A_SHARE_TRADING_CALENDAR.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown(frame), encoding="utf-8")
    return {
        "artifact_id": "A-SHARE-TRADING-CALENDAR",
        "target_version": "v0.7.1-a-share-full-market-data-ingestion",
        "trading_days": int(frame["date"].nunique()) if not frame.empty else 0,
        "min_date": str(frame["date"].min()) if not frame.empty else "",
        "max_date": str(frame["date"].max()) if not frame.empty else "",
        "parquet_path": str(parquet_path),
        "json_path": str(json_path),
        "report_path": str(report_path),
    }


def _markdown(frame: pd.DataFrame) -> str:
    lines = [
        "# A-Share Trading Calendar",
        "",
        "- source: weekday_calendar_v1",
        f"- exchanges: {', '.join(sorted(frame['exchange'].unique().tolist())) if not frame.empty else ''}",
        f"- trading_days: {frame['date'].nunique() if not frame.empty else 0}",
        f"- min_date: {frame['date'].min() if not frame.empty else ''}",
        f"- max_date: {frame['date'].max() if not frame.empty else ''}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return "\n".join(lines)

