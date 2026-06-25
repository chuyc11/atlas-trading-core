from pathlib import Path

import pytest

from daily_workflow_test_utils import build_daily_workflow_stack, make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.planning.day1_blocker_reclassification_v061 import reclassify_day1_blockers_after_daily_workflow


def test_day1_blocker_reclassification_v061(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    build_daily_workflow_stack(paths)
    result = reclassify_day1_blockers_after_daily_workflow(paths=paths)
    assert result["daily_workflow_blocker_closed"] is True
    assert result["updated_day1_blocker_count"] == 0
    assert result["recommended_next_version"] == "v0.6.2-forward-dry-run-start-authorization-pack"
    assert result["day1_start_allowed"] is False
    assert result["manual_confirmation_complete"] is False
    assert result["forward_dry_run_start_authorized"] is False
    assert result["run_daily_called"] is False
    assert result["forward_dry_run_started"] is False
    assert result["main_ledger_written"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_day1_blocker_reclassification_v061_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    build_daily_workflow_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["reclassify-day1-blockers-after-daily-workflow"]) == 0

