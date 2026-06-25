from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.execution.execution_timeline_contract import build_execution_timeline_contract


def test_execution_timeline_contract_output(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    result = build_execution_timeline_contract(paths=paths)
    assert result["same_day_close_signal_execution_rejected"] is True
    assert result["future_price_rejected"] is True
    assert result["boundary"]["main_ledger_written"] is False
    assert_no_protected_paths(paths)


def test_execution_timeline_contract_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["execution-timeline-contract"]) == 0

