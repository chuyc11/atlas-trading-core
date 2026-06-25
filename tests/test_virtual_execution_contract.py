from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.execution.virtual_execution_contract import build_virtual_execution_contract


def test_virtual_execution_contract_output(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    result = build_virtual_execution_contract(paths=paths)
    assert result["calendar_required"] is True
    assert result["protected_path_guard"] is True
    assert result["rejected_orders_require_reason"] is True
    assert_no_protected_paths(paths)


def test_virtual_execution_contract_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["virtual-execution-contract"]) == 0

