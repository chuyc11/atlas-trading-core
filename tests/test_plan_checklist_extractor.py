from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.planning.plan_checklist_extractor import build_plan_checklist


def test_plan_checklist_generates_r001_r024(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    result = build_plan_checklist(paths=paths)
    ids = {item["requirement_id"] for item in result["requirements"]}
    assert {f"R{number:03d}" for number in range(1, 25)} <= ids
    assert all(item["category"] for item in result["requirements"])
    assert all("required_before_forward_day1" in item for item in result["requirements"])
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert "Plan Checklist" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_plan_checklist_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["plan-checklist"]) == 0

