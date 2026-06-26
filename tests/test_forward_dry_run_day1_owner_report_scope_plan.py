from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_owner_report_test_utils import make_day1_owner_report_paths
from trading_core.forward_dry_run.day1_owner_report_scope_plan import build_day1_owner_report_scope_plan


def test_day1_owner_report_scope_plan_is_report_only(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    result = build_day1_owner_report_scope_plan(paths=paths)
    assert result["scope_plan_id"] == "FORWARD-DRY-RUN-DAY1-OWNER-REPORT-SCOPE-PLAN"
    assert result["target_version"] == "v0.6.3.2-forward-dry-run-day1-owner-report-pack"
    assert result["report_only"] is True
    assert result["day2_execution_allowed"] is False
    assert result["boundary"]["run_daily_called"] is False


def test_day1_owner_report_scope_plan_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_owner_report_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-owner-report-scope-plan"]) == 0
