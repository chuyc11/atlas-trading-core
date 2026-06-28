from __future__ import annotations

from trading_core.equity_benchmarks.benchmark_nav import as_of_nav_snapshot, build_benchmark_nav_records


def test_benchmark_nav_math() -> None:
    records = [
        {"benchmark_id": "CSI300", "date": "2026-06-25", "daily_return": 0.0},
        {"benchmark_id": "CSI300", "date": "2026-06-26", "daily_return": 0.10},
    ]
    nav = build_benchmark_nav_records(records)
    snapshot = as_of_nav_snapshot(nav, "2026-06-26")
    assert round(snapshot["CSI300"]["benchmark_nav"], 6) == 1.1
    assert round(snapshot["CSI300"]["benchmark_cumulative_return"], 6) == 0.1
