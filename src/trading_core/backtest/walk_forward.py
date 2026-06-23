"""Walk-forward runner for rule strategies."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from trading_core.backtest.event_backtester import run_event_backtest
from trading_core.calendar.trading_calendar import parse_date
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import write_json


def run_walk_forward(
    start_date: str,
    end_date: str,
    window_days: int = 5,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    if window_days <= 0:
        raise ValueError("window_days must be positive")
    start = parse_date(start_date)
    end = parse_date(end_date)
    windows = []
    current = start
    while current <= end:
        window_end = min(current + timedelta(days=window_days - 1), end)
        result = run_event_backtest(current.isoformat(), window_end.isoformat(), workspace_root)
        windows.append(
            {
                "start_date": current.isoformat(),
                "end_date": window_end.isoformat(),
                "days": result["days"],
                "total_return": result["total_return"],
                "end_asset": result["end_asset"],
            }
        )
        current = window_end + timedelta(days=1)
    summary = {
        "start_date": start_date,
        "end_date": end_date,
        "window_days": window_days,
        "windows": windows,
        "strategy_scope": "first-stage rule strategies only",
    }
    paths = project_paths(workspace_root)
    write_json(paths.outputs_dir / "backtests" / f"walk-forward-{start_date}-to-{end_date}.json", summary)
    return summary
