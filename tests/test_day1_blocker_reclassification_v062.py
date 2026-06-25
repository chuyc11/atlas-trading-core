from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import build_authorization_pack, make_authorization_paths
from trading_core.planning.day1_blocker_reclassification_v062 import reclassify_day1_blockers_after_start_authorization


def test_day1_blocker_reclassification_v062(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    result = reclassify_day1_blockers_after_start_authorization(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["technical_day1_blocker_count"] == 0
    assert result["authorization_blocker_count"] == 2
    assert "manual_confirmation_complete=false" in result["authorization_blockers"]
    assert "forward_dry_run_start_authorized=false" in result["authorization_blockers"]
    assert result["updated_day1_blocker_count"] == 2
    assert result["day1_start_allowed"] is False
    assert result["recommended_next_action"] == "owner_manual_confirmation"
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_day1_blocker_reclassification_v062_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["reclassify-day1-blockers-after-start-authorization"]) == 0

