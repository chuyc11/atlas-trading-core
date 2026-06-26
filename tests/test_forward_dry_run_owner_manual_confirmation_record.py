from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import build_authorization_pack, make_authorization_paths
from trading_core.forward_dry_run.owner_manual_confirmation_record import build_owner_manual_confirmation_record


def test_owner_manual_confirmation_record(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    result = build_owner_manual_confirmation_record(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["owner_confirmation_recorded"] is True
    assert result["owner_authorized_next_step"] is True
    assert result["owner_authorized_day1_execution"] is False
    assert result["day1_execution_requires_separate_prompt"] is True
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_owner_manual_confirmation_record_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-owner-manual-confirmation-record"]) == 0

