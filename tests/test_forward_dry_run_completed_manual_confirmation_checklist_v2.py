from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import build_authorization_pack, make_authorization_paths
from trading_core.forward_dry_run.completed_manual_confirmation_checklist_v2 import complete_forward_dry_run_manual_confirmation_checklist_v2


def test_completed_manual_confirmation_checklist_v2(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    result = complete_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["manual_confirmation_complete"] is True
    assert result["items"]
    assert all(item["confirmed"] is True for item in result["items"])
    assert result["day1_execution_authorized"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_completed_manual_confirmation_checklist_v2_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["complete-forward-dry-run-manual-confirmation-checklist-v2"]) == 0

