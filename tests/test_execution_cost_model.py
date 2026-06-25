from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.execution.execution_cost_contract import build_execution_cost_contract
from trading_core.execution.cost_model import calculate_trade_cost


def test_execution_cost_model_and_contract(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    buy = calculate_trade_cost(10, 100, "BUY", "A_SHARE")
    sell = calculate_trade_cost(10, 100, "SELL", "A_SHARE")
    assert buy.commission >= 5
    assert sell.commission >= 5
    assert sell.tax > 0
    assert buy.slippage > 0
    assert buy.net_amount > buy.gross_amount
    assert sell.net_amount < sell.gross_amount
    result = build_execution_cost_contract(paths=paths)
    assert result["costs_enter_cash_accounting"] is True
    assert result["costs_enter_trade_record"] is True
    assert result["costs_enter_replay_evaluation"] is True
    assert_no_protected_paths(paths)


def test_execution_cost_contract_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["ashare-execution-cost-contract"]) == 0

