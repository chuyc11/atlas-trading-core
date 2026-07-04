from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from trading_core.backtest.batch_runner import _metrics, run_backtest_batch
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json


def _write_price_csv(path: Path, days: int = 70) -> None:
    current = date(2026, 1, 1)
    rows = ["date,symbol,open,high,low,close,volume,source,quality"]
    business_days = 0
    while business_days < days:
        if current.weekday() < 5:
            idx = business_days
            for symbol, base, slope in [
                ("510300.SH", 4.0, 0.01),
                ("159915.SZ", 2.0, 0.015),
                ("000300.SH", 5000.0, 5.0),
            ]:
                open_price = base + idx * slope
                close_price = open_price + slope / 2
                rows.append(
                    f"{current.isoformat()},{symbol},{open_price:.4f},{close_price:.4f},{open_price:.4f},{close_price:.4f},100000,test,fresh"
                )
            business_days += 1
        current += timedelta(days=1)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_backtest_batch_runner_writes_standard_outputs(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    _write_price_csv(csv_path)

    result = run_backtest_batch(
        "2026-01-01",
        "2026-04-08",
        csv_path,
        paths=project_paths(tmp_path),
        timestamp="TESTBATCH",
    )

    output_dir = Path(result["output_dir"])
    assert output_dir.name == "batch-TESTBATCH"
    for name in [
        "batch_config.json",
        "data_validation.json",
        "strategy_results.json",
        "benchmark_results.json",
        "admission_results.json",
        "leaderboard.json",
        "BACKTEST_BATCH_REPORT.md",
    ]:
        assert (output_dir / name).exists()

    strategy_results = read_json(output_dir / "strategy_results.json")
    admission_results = read_json(output_dir / "admission_results.json")
    leaderboard = read_json(output_dir / "leaderboard.json")
    report = (output_dir / "BACKTEST_BATCH_REPORT.md").read_text(encoding="utf-8")

    assert result["passed"] is True
    assert set(strategy_results) == {"hold_strategy", "macro_etf_strategy_v1", "momentum_strategy_v1"}
    assert "macro_etf_strategy_v1" in admission_results
    assert leaderboard["items"]
    assert result["best_strategy"] in strategy_results
    assert result["worst_strategy"] in strategy_results
    assert "Data Coverage" in report
    assert "excess_return vs EQUAL_ETF" in report


def test_backtest_batch_runner_stops_on_failed_validation(tmp_path: Path) -> None:
    csv_path = tmp_path / "dirty.csv"
    csv_path.write_text(
        "date,symbol,open,high,low,close,volume,source,quality\n"
        "2026-01-01,510300.SH,4,3,4,4,100,test,bad\n",
        encoding="utf-8",
    )

    result = run_backtest_batch(
        "2026-01-01",
        "2026-01-02",
        csv_path,
        paths=project_paths(tmp_path),
        timestamp="BADBATCH",
    )

    output_dir = Path(result["output_dir"])
    assert result["passed"] is False
    assert result["strategy_results"] == {}
    assert read_json(output_dir / "data_validation.json")["passed"] is False
    assert "data_validation_failed" in (output_dir / "BACKTEST_BATCH_REPORT.md").read_text(encoding="utf-8")


def test_batch_metrics_use_period_cumulative_excess_return_not_last_daily_excess() -> None:
    portfolios = [
        {"date": "2026-01-01", "total_asset": 100000, "daily_return": 0.0},
        {"date": "2026-01-02", "total_asset": 110000, "daily_return": 0.10},
        {"date": "2026-01-05", "total_asset": 121000, "daily_return": 0.10},
    ]
    benchmark = {
        "benchmarks": {"EQUAL_ETF": {"return": 0.99, "cumulative_return": 0.10}},
        "benchmark_cumulative_return": {"EQUAL_ETF": 0.10},
        "excess_return": {"EQUAL_ETF": 0.99},
    }

    result = _metrics("golden_strategy", portfolios, [], benchmark)

    assert result["cumulative_return"] == pytest.approx(0.21)
    assert result["excess_return_equal_etf"] == pytest.approx(0.11)
    assert result["admission_metrics"]["excess_return"] == pytest.approx(0.11)
