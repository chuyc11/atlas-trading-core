from __future__ import annotations

import pytest

from trading_core.benchmarks.benchmark_engine import build_benchmark
from trading_core.storage.file_paths import project_paths


@pytest.mark.parametrize(
    ("change_pct", "expected"),
    [
        (0.63, 0.0063),
        (-1.25, -0.0125),
        (0, 0.0),
    ],
)
def test_change_pct_percent_units(change_pct: float, expected: float, tmp_path) -> None:
    benchmark = build_benchmark(
        "2026-06-23",
        {"account_id": "CHINA_PAPER", "daily_return": 0.0},
        {"000300.SH": {"change_pct": change_pct}},
        paths=project_paths(tmp_path),
    )

    assert benchmark["benchmarks"]["CSI300"]["return"] == pytest.approx(expected)


def test_price_math_takes_priority_over_change_pct(tmp_path) -> None:
    benchmark = build_benchmark(
        "2026-06-23",
        {"account_id": "CHINA_PAPER", "daily_return": 0.0},
        {"000300.SH": {"price": 101.0, "previous_close": 100.0, "change_pct": 99.0}},
        paths=project_paths(tmp_path),
    )

    assert benchmark["benchmarks"]["CSI300"]["return"] == pytest.approx(0.01)
