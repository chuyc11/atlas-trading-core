from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import build_authorization_pack, make_authorization_paths
from trading_core.forward_dry_run.updated_owner_authorization_packet import update_forward_dry_run_owner_authorization_packet


def test_updated_owner_authorization_packet(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    result = update_forward_dry_run_owner_authorization_packet(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["forward_dry_run_start_authorized"] is True
    assert result["authorization_status"] == "authorized_for_day1_prompt_generation"
    assert result["day1_execution_authorized"] is False
    assert result["day1_execution_requires_separate_prompt"] is True
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_updated_owner_authorization_packet_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["update-forward-dry-run-owner-authorization-packet"]) == 0

