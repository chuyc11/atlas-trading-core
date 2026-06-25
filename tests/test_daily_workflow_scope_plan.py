from pathlib import Path

import pytest

from daily_workflow_test_utils import make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.daily_workflow.daily_workflow_scope_plan import build_daily_workflow_scope_plan


def test_daily_workflow_scope_plan(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    result = build_daily_workflow_scope_plan(paths=paths)
    assert result["target_version"] == "v0.6.1-daily-workflow-binding-audited"
    assert result["baseline_strategy_pack_complete"] is True
    assert result["workflow_components"]
    assert result["forward_dry_run_day1_allowed"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_daily_workflow_scope_plan_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["daily-workflow-scope-plan"]) == 0

