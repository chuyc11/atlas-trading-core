from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.execution.execution_aware_replay_smoke import run_execution_aware_replay_smoke


def test_execution_aware_replay_smoke(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    result = run_execution_aware_replay_smoke(paths=paths)
    assert result["overall_passed"] is True
    assert result["included_scenarios"] >= 6
    assert result["execution_mode"] == "isolated"
    assert result["ledger_invariant_audit_passed"] is True
    assert result["boundary"]["forward_dry_run_started"] is False
    assert_no_protected_paths(paths)


def test_execution_aware_replay_smoke_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["execution-aware-replay-smoke"]) == 0

