from pathlib import Path
import subprocess

import pytest

from forward_dry_run_authorization_test_utils import make_authorization_paths
from trading_core.forward_dry_run.run_daily_command_preview_metadata import build_forward_dry_run_run_daily_command_preview


def test_run_daily_command_preview_metadata_does_not_execute(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = make_authorization_paths(tmp_path)
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("subprocess called")))
    result = build_forward_dry_run_run_daily_command_preview(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["preview_only"] is True
    assert result["executed"] is False
    assert result["run_daily_called"] is False
    assert result["requires_start_gate_allowed"] is True
    assert result["requires_owner_confirmation"] is True
    assert result["boundary"]["main_ledger_written"] is False


def test_run_daily_command_preview_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-run-daily-command-preview"]) == 0

