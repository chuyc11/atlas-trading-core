from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.execution.ashare_lot_position_contract import build_lot_position_contract


def test_lot_position_contract_output(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    result = build_lot_position_contract(paths=paths)
    assert result["default_board_lot"] == 100
    assert result["t_day_buy_available_same_day"] is False
    assert result["t_plus_1_available_after_settlement"] is True
    assert result["negative_cash_allowed"] is False
    assert result["negative_position_allowed"] is False
    assert_no_protected_paths(paths)


def test_lot_position_contract_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["ashare-lot-and-position-contract"]) == 0

