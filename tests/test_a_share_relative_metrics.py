from __future__ import annotations

from trading_core.equity_benchmarks.relative_metrics import correlation, information_ratio, tracking_error


def test_relative_metrics_require_history_and_compute_values() -> None:
    assert tracking_error([0.01]) is None
    assert information_ratio([0.01]) is None
    assert correlation([0.01], [0.02]) is None
    assert tracking_error([0.01, 0.03]) is not None
    assert correlation([0.01, 0.02, 0.03], [0.02, 0.04, 0.06]) == 1.0
