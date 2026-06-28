"""Benchmark NAV calculations."""

from __future__ import annotations

from typing import Any


def build_benchmark_nav_records(return_records: list[dict[str, Any]], *, base_nav: float = 1.0) -> list[dict[str, Any]]:
    nav_records: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in return_records:
        grouped.setdefault(str(row["benchmark_id"]), []).append(row)
    for benchmark_id, rows in grouped.items():
        nav = float(base_nav)
        for row in sorted(rows, key=lambda item: item["date"]):
            nav *= 1.0 + float(row.get("daily_return") or 0.0)
            nav_records.append(
                {
                    "benchmark_id": benchmark_id,
                    "date": row["date"],
                    "benchmark_nav": nav,
                    "benchmark_daily_return": float(row.get("daily_return") or 0.0),
                    "benchmark_cumulative_return": nav / base_nav - 1.0,
                    "first_day_nav": float(base_nav),
                    "is_placeholder": bool(row.get("is_placeholder", False)),
                }
            )
    return nav_records


def as_of_nav_snapshot(nav_records: list[dict[str, Any]], as_of_date: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in nav_records:
        if str(row.get("date")) <= as_of_date:
            result[str(row["benchmark_id"])] = row
    return result
