from __future__ import annotations

from trading_core.equity_benchmarks.benchmark_config import BenchmarkConfig
from trading_core.equity_benchmarks.cash_benchmark import build_cash_benchmark_returns


def test_cash_benchmark_uses_zero_return() -> None:
    records, availability = build_cash_benchmark_returns(["2026-06-25", "2026-06-26"], config=BenchmarkConfig())
    assert [row["daily_return"] for row in records] == [0.0, 0.0]
    assert availability["status"] == "available"
    assert availability["is_placeholder"] is False
