"""Cash benchmark construction."""

from __future__ import annotations

from typing import Any

from trading_core.equity_benchmarks.benchmark_config import BenchmarkConfig


def build_cash_benchmark_returns(dates: list[str], *, config: BenchmarkConfig) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not dates:
        dates = [config.as_of_date]
    records = [
        {
            "benchmark_id": "CASH",
            "date": day,
            "daily_return": float(config.cash_benchmark_daily_return),
            "source_type": "cash_assumption_zero_return",
            "is_placeholder": False,
        }
        for day in sorted(set(dates))
        if day <= config.as_of_date
    ]
    availability = {
        "benchmark_id": "CASH",
        "status": "available",
        "source_type": "cash_assumption_zero_return",
        "source_path": None,
        "symbol_or_index_code": "CNY_CASH_0_RETURN",
        "first_available_date": records[0]["date"],
        "last_available_date": records[-1]["date"],
        "as_of_date_available": any(row["date"] == config.as_of_date for row in records),
        "trading_days_available": len(records),
        "missing_reason": None,
        "is_placeholder": False,
    }
    return records, availability
