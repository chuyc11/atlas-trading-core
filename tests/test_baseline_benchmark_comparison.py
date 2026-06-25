from pathlib import Path

import pytest

from baseline_strategy_test_utils import TEST_END, TEST_START, make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.strategies.baseline_benchmark_comparison import compare_baseline_strategy_benchmarks
from trading_core.strategies.common import DEFAULT_BENCHMARKS, STRATEGY_IDS


def test_baseline_benchmark_comparison(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    result = compare_baseline_strategy_benchmarks(strategy="all", start_date=TEST_START, end_date=TEST_END, paths=paths)
    assert set(result["benchmarks"]) == set(DEFAULT_BENCHMARKS)
    for benchmark in result["benchmarks"].values():
        assert benchmark.get("available") is True or benchmark.get("missing_reason")
    for strategy_id in STRATEGY_IDS:
        metrics = result["strategies"][strategy_id]
        assert "cumulative_return" in metrics
        assert "max_drawdown" in metrics
        assert "turnover" in metrics
        assert "cost_drag" in metrics
        assert "rejected_order_count" in metrics
        assert metrics["promotion_triggered"] is False
        assert metrics["strategy_effectiveness_proven"] is False
    assert result["promotion_triggered"] is False
    assert result["strategy_effectiveness_proven"] is False
    assert result["live_trading_ready"] is False
    assert_no_protected_paths(paths)


def test_baseline_benchmark_comparison_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["compare-baseline-strategy-benchmarks", "--strategy", "all", "--start-date", TEST_START, "--end-date", TEST_END]) == 0

