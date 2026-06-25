from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.execution.price_status_contract import build_price_status_contract


def test_price_status_contract_outputs(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    result = build_price_status_contract(paths=paths)
    assert result["suspension_missing_limit_handled"] is True
    assert result["st_new_listing_handled"] is True
    assert result["scenarios"]["limit_up_buy"]["allowed"] is False
    assert result["scenarios"]["limit_down_sell"]["allowed"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)


def test_price_status_contract_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["ashare-price-status-contract"]) == 0

