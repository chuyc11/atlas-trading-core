from pathlib import Path

import pytest

from daily_workflow_test_utils import AS_OF, make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.daily_workflow.daily_isolated_execution_preview import build_daily_isolated_execution_preview


def test_daily_isolated_execution_preview(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    result = build_daily_isolated_execution_preview(as_of_date=AS_OF, execution_mode="isolated", paths=paths)
    assert result["execution_mode"] == "isolated_preview"
    assert result["preview_only"] is True
    assert result["executed"] is False
    assert result["state_updated"] is False
    assert result["cost_summary"]["estimated_cost"] > 0
    assert "rejects" in result
    assert result["ledger_invariants"]["passed"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_daily_isolated_execution_preview_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["daily-isolated-execution-preview", "--as-of-date", AS_OF, "--execution-mode", "isolated"]) == 0

