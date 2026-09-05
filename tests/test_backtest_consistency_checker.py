from __future__ import annotations

from pathlib import Path

from trading_core.accounting.consistency_checker import check_consistency_range
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json, write_jsonl
import pytest

pytestmark = pytest.mark.smoke


START = "2026-01-02"
END = "2026-01-05"
STRATEGY = "test_strategy"


def _seed_backtest_artifacts(root: Path) -> tuple[Path, Path]:
    paths = project_paths(root)
    artifact_dir = paths.outputs_dir / "backtests" / "batch-TEST"
    portfolio_path = paths.data_dir / "backtests" / f"backtest_portfolio-{START}-{END}-{STRATEGY}.jsonl"
    trades_path = paths.data_dir / "backtests" / f"backtest_trades-{START}-{END}-{STRATEGY}.jsonl"
    benchmark_path = paths.data_dir / "backtests" / f"backtest_benchmark-{START}-{END}-{STRATEGY}.json"
    metrics = {
        "backtest_days": 2,
        "trades": 1,
        "excess_return": 0.0,
        "max_drawdown": 0.0,
        "mistake_rate": 0.0,
        "cost_ratio": 0.00005,
        "benchmark_comparison": True,
        "future_data_flag": False,
    }
    write_jsonl(
        portfolio_path,
        [
            {
                "date": START,
                "account_id": "CHINA_PAPER",
                "cash": 100000.0,
                "market_value": 0.0,
                "total_asset": 100000.0,
                "daily_return": 0.0,
                "positions": [],
                "strategy_id": STRATEGY,
            },
            {
                "date": END,
                "account_id": "CHINA_PAPER",
                "cash": 95000.0,
                "market_value": 5000.0,
                "total_asset": 100000.0,
                "daily_return": 0.0,
                "positions": [
                    {
                        "symbol": "510300.SH",
                        "market": "A_SHARE",
                        "quantity": 1000,
                        "available_quantity": 0,
                        "current_price": 5.0,
                        "market_value": 5000.0,
                    }
                ],
                "strategy_id": STRATEGY,
            },
        ],
    )
    write_jsonl(
        trades_path,
        [
            {
                "trade_id": "TRD-20260105-001",
                "order_id": "ORD-20260105-001",
                "signal_id": "BT-SIG-20260102-test_strategy-510300.SH",
                "signal_date": START,
                "date": END,
                "side": "BUY",
                "symbol": "510300.SH",
                "market": "A_SHARE",
                "filled_quantity": 1000,
                "filled_price": 5.0,
                "gross_amount": 5000.0,
                "commission": 5.0,
                "tax": 0.0,
                "net_amount": 5005.0,
            }
        ],
    )
    write_json(
        benchmark_path,
        {
            "date": END,
            "portfolio_return": 0.0,
            "benchmarks": {"EQUAL_ETF": {"symbol": "EQUAL_ETF", "name": "ETF", "return": 0.0}},
            "excess_return": {"EQUAL_ETF": 0.0},
        },
    )
    write_json(artifact_dir / "batch_config.json", {"start_date": START, "end_date": END})
    write_json(
        artifact_dir / "strategy_results.json",
        {
            STRATEGY: {
                "start_date": START,
                "end_date": END,
                "strategy_id": STRATEGY,
                "days": 2,
                "final_asset": 100000.0,
                "cumulative_return": 0.0,
                "trade_count": 1,
                "portfolio_path": str(portfolio_path),
                "trades_path": str(trades_path),
                "benchmark_path": str(benchmark_path),
                "admission_metrics": metrics,
            }
        },
    )
    write_json(
        artifact_dir / "benchmark_results.json",
        {STRATEGY: {"EQUAL_ETF": {"symbol": "EQUAL_ETF", "name": "ETF", "return": 0.0}}},
    )
    write_json(
        artifact_dir / "admission_results.json",
        {STRATEGY: {"strategy_id": STRATEGY, "status": "rejected", "passed": False, "metrics": metrics}},
    )
    write_json(artifact_dir / "leaderboard.json", {"items": [{"strategy_id": STRATEGY, "rank": 1}]})
    return artifact_dir, portfolio_path


def _seed_daily_portfolio(root: Path, day: str) -> None:
    paths = project_paths(root)
    write_json(
        paths.dated_json("portfolios", "portfolio", day),
        {
            "date": day,
            "cash": 100000.0,
            "market_value": 0.0,
            "total_asset": 100000.0,
            "daily_return": 0.0,
            "positions": [],
        },
    )


def test_backtest_consistency_passes_clean_artifacts(tmp_path: Path) -> None:
    artifact_dir, _portfolio_path = _seed_backtest_artifacts(tmp_path)

    result = check_consistency_range(START, END, project_paths(tmp_path), mode="backtest", artifact_dir=artifact_dir)

    assert result["passed"] is True
    assert result["mode"] == "backtest"
    assert result["strategies_checked"] == 1
    assert result["days_checked"] == 2
    assert result["trades_checked"] == 1
    assert result["benchmark_checked"] == 1
    assert Path(result["json_path"]).name == f"backtest_consistency-{START}-{END}.json"
    assert Path(result["report_path"]).name == f"BACKTEST_CONSISTENCY-{START}-{END}.md"


def test_backtest_consistency_requires_artifact_dir(tmp_path: Path) -> None:
    result = check_consistency_range(START, END, project_paths(tmp_path), mode="backtest")

    assert result["passed"] is False
    assert any("artifact-dir is required" in error for error in result["critical_errors"])


def test_backtest_consistency_flags_final_asset_mismatch(tmp_path: Path) -> None:
    artifact_dir, _portfolio_path = _seed_backtest_artifacts(tmp_path)
    path = artifact_dir / "strategy_results.json"
    payload = read_json(path)
    payload[STRATEGY]["final_asset"] = 999.0
    write_json(path, payload)

    result = check_consistency_range(START, END, project_paths(tmp_path), mode="backtest", artifact_dir=artifact_dir)

    assert result["passed"] is False
    assert any("final_asset mismatch" in error for error in result["critical_errors"])


def test_backtest_consistency_flags_negative_cash(tmp_path: Path) -> None:
    artifact_dir, portfolio_path = _seed_backtest_artifacts(tmp_path)
    rows = read_jsonl(portfolio_path)
    rows[-1]["cash"] = -1.0
    rows[-1]["market_value"] = 100001.0
    rows[-1]["total_asset"] = 100000.0
    write_jsonl(portfolio_path, rows)

    result = check_consistency_range(START, END, project_paths(tmp_path), mode="backtest", artifact_dir=artifact_dir)

    assert result["passed"] is False
    assert any("cash is negative" in error for error in result["critical_errors"])


def test_backtest_consistency_flags_total_asset_mismatch(tmp_path: Path) -> None:
    artifact_dir, portfolio_path = _seed_backtest_artifacts(tmp_path)
    rows = read_jsonl(portfolio_path)
    rows[-1]["total_asset"] = 100001.0
    write_jsonl(portfolio_path, rows)

    result = check_consistency_range(START, END, project_paths(tmp_path), mode="backtest", artifact_dir=artifact_dir)

    assert result["passed"] is False
    assert any("total_asset does not equal" in error for error in result["critical_errors"])


def test_backtest_consistency_flags_same_day_t_plus_one(tmp_path: Path) -> None:
    artifact_dir, _portfolio_path = _seed_backtest_artifacts(tmp_path)
    strategy_results = read_json(artifact_dir / "strategy_results.json")
    trades_path = Path(strategy_results[STRATEGY]["trades_path"])
    rows = read_jsonl(trades_path)
    rows[0]["signal_date"] = END
    write_jsonl(trades_path, rows)

    result = check_consistency_range(START, END, project_paths(tmp_path), mode="backtest", artifact_dir=artifact_dir)

    assert result["passed"] is False
    assert any("T+1 violation" in error for error in result["critical_errors"])


def test_consistency_range_daily_mode_keeps_existing_behavior(tmp_path: Path) -> None:
    _seed_daily_portfolio(tmp_path, START)
    _seed_daily_portfolio(tmp_path, END)

    result = check_consistency_range(START, END, project_paths(tmp_path), mode="daily")

    assert result["mode"] == "daily"
    assert len(result["items"]) == 2
    assert result["critical_errors"] == []


def test_consistency_range_auto_uses_backtest_when_artifact_dir_is_given(tmp_path: Path) -> None:
    artifact_dir, _portfolio_path = _seed_backtest_artifacts(tmp_path)

    result = check_consistency_range(START, END, project_paths(tmp_path), mode="auto", artifact_dir=artifact_dir)

    assert result["mode"] == "backtest"
    assert result["passed"] is True
