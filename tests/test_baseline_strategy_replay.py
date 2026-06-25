from pathlib import Path

import pytest

from baseline_strategy_test_utils import TEST_END, TEST_START, make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.storage.jsonl_store import read_jsonl
from trading_core.strategies.baseline_strategy_replay import replay_baseline_strategy
from trading_core.strategies.common import STRATEGY_IDS


def test_baseline_strategy_replay_uses_isolated_virtual_execution(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    result = replay_baseline_strategy(strategy="all", start_date=TEST_START, end_date=TEST_END, execution_mode="isolated", paths=paths)
    assert result["all_replays_complete"] is True
    for strategy_id in STRATEGY_IDS:
        replay = result["paths"][strategy_id]
        assert replay["execution_mode"] == "isolated"
        assert replay["orders_path"].startswith(f"data/replays/strategies/{strategy_id}/")
        assert replay["trades"] > 0
        assert replay["daily_valuation_rows"] > 0
        assert replay["no_trade_fallback"] is False
        assert replay["strategy_effectiveness_proven"] is False
        trades = read_jsonl(paths.project_root / replay["trades_path"])
        assert all({"commission", "tax", "slippage"} <= set(trade) for trade in trades)
    assert sum(result["paths"][strategy_id]["rejected_orders"] for strategy_id in STRATEGY_IDS) >= 1
    assert_no_protected_paths(paths)


def test_baseline_strategy_replay_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["replay-baseline-strategy", "--strategy", "all", "--start-date", TEST_START, "--end-date", TEST_END, "--execution-mode", "isolated"]) == 0

