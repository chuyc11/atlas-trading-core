"""Benchmark return calculations."""

from __future__ import annotations

from typing import Any

import pandas as pd


def returns_from_price_frame(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    records: list[dict[str, Any]] = []
    for benchmark_id, subset in frame.sort_values(["benchmark_id", "date"]).groupby("benchmark_id"):
        subset = subset.dropna(subset=["close"]).copy()
        previous = None
        for _, row in subset.iterrows():
            close = float(row["close"])
            daily_return = 0.0 if previous in (None, 0.0) else close / previous - 1.0
            records.append(
                {
                    "benchmark_id": str(benchmark_id),
                    "date": str(row["date"]),
                    "daily_return": daily_return,
                    "close": close,
                    "source_type": row.get("source_type"),
                    "is_placeholder": bool(row.get("is_placeholder", False)),
                }
            )
            previous = close
    return records


def cumulative_return(records: list[dict[str, Any]], benchmark_id: str) -> float | None:
    nav = 1.0
    found = False
    for row in sorted((r for r in records if r.get("benchmark_id") == benchmark_id), key=lambda item: item["date"]):
        nav *= 1.0 + float(row.get("daily_return") or 0.0)
        found = True
    return nav - 1.0 if found else None
