from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import make_authorization_paths
from trading_core.forward_dry_run.current_daily_workflow_readiness_snapshot import build_current_daily_workflow_readiness_snapshot


def test_current_daily_workflow_readiness_snapshot(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    result = build_current_daily_workflow_readiness_snapshot(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["historical_daily_workflow_fixture_passed"] is True
    assert result["current_production_daily_workflow_authorized"] is False
    assert result["real_time_market_data_downloaded"] is False
    assert result["external_api_called"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_current_daily_workflow_readiness_snapshot_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["current-daily-workflow-readiness-snapshot"]) == 0

