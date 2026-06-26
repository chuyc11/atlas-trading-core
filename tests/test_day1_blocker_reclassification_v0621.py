from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import build_authorization_materialization_stack, make_authorization_paths
from trading_core.planning.day1_blocker_reclassification_v0621 import reclassify_day1_blockers_after_authorization_materialization


def test_day1_blocker_reclassification_v0621(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_materialization_stack(paths)
    result = reclassify_day1_blockers_after_authorization_materialization(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["technical_day1_blocker_count"] == 0
    assert result["authorization_blocker_count"] == 0
    assert result["updated_day1_blocker_count"] == 0
    assert result["day1_prompt_eligible"] is True
    assert result["day1_start_allowed"] is False
    assert result["recommended_next_action"] == "owner_requests_day1_prompt"
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_day1_blocker_reclassification_v0621_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_authorization_materialization_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["reclassify-day1-blockers-after-authorization-materialization"]) == 0

