from __future__ import annotations

import pandas as pd

from trading_core.equity_benchmarks.benchmark_returns import returns_from_price_frame


def test_benchmark_daily_return_math() -> None:
    frame = pd.DataFrame(
        [
            {"benchmark_id": "CSI300", "date": "2026-06-25", "close": 100.0, "is_placeholder": False},
            {"benchmark_id": "CSI300", "date": "2026-06-26", "close": 110.0, "is_placeholder": False},
        ]
    )
    records = returns_from_price_frame(frame)
    assert records[0]["daily_return"] == 0.0
    assert round(records[1]["daily_return"], 6) == 0.1
