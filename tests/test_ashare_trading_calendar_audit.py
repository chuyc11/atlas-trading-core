from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.execution.trading_calendar_audit import audit_trading_calendar


def test_calendar_audit_passes(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    result = audit_trading_calendar(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert "A-Share Trading Calendar Audit" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_calendar_audit_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["ashare-trading-calendar-audit"]) == 0

