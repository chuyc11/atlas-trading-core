from __future__ import annotations

from pathlib import Path

import pytest

from day0_test_utils import make_day0_paths
from trading_core.forward_dry_run.operating_calendar import build_forward_dry_run_operating_calendar


def test_forward_dry_run_operating_calendar_template_only(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    result = build_forward_dry_run_operating_calendar(paths=paths)
    assert result["calendar_status"] == "template_only"
    assert len(result["days"]) == 30
    assert all(day["status"] == "not_started" for day in result["days"])
    assert all(day["run_daily_called"] is False for day in result["days"])
    assert result["boundary"]["forward_dry_run_started"] is False
    assert Path(result["daily_log_template_path"]).exists()
    assert "Forward Dry-Run Operating Calendar" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_forward_dry_run_operating_calendar_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day0_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-operating-calendar"]) == 0
