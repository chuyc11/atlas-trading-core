from __future__ import annotations

from pathlib import Path

import pytest

from day0_test_utils import build_day0_stack, make_day0_paths
from trading_core.forward_dry_run.day0_readiness_report import build_day0_readiness_report


def test_day0_readiness_report_ready_for_manual_confirmation(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    build_day0_stack(paths)
    result = build_day0_readiness_report(paths=paths)
    assert result["overall_status"] == "ready_for_manual_confirmation"
    assert result["sections"]["manual_confirmation"]["manual_confirmation_complete"] is False
    assert result["can_start_forward_dry_run_without_manual_confirmation"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert "Day-0 Readiness Report" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_day0_readiness_report_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day0_paths(tmp_path)
    build_day0_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["day0-readiness-report"]) == 0
