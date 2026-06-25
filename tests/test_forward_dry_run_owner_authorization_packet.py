from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import make_authorization_paths
from trading_core.forward_dry_run.owner_authorization_packet import build_forward_dry_run_owner_authorization_packet


def test_owner_authorization_packet_defaults_not_authorized(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    result = build_forward_dry_run_owner_authorization_packet(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["authorization_status"] == "not_authorized"
    assert result["forward_dry_run_start_authorized"] is False
    assert result["authorized_by"] is None
    assert result["authorized_at"] is None
    assert result["day1_start_allowed"] is False
    assert "I explicitly authorize starting forward dry-run day 1" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_owner_authorization_packet_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-owner-authorization-packet"]) == 0

