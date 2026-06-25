from __future__ import annotations

from pathlib import Path

import json
import pytest

from day0_test_utils import build_day0_stack, make_day0_paths
from trading_core.forward_dry_run.day0_run_daily_preflight import build_day0_run_daily_preflight


def test_day0_run_daily_preflight_preview_only(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    build_day0_stack(paths)
    result = build_day0_run_daily_preflight(paths=paths)
    assert result["overall_passed"] is True
    assert result["run_daily_command_preview"]["preview_only"] is True
    assert result["run_daily_command_preview"]["executed"] is False
    assert result["manual_confirmation_required"] is True
    assert "Day-0 Run-Daily Preflight Checklist" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_day0_run_daily_preflight_fails_when_conditions_block(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    build_day0_stack(paths)
    conditions_path = paths.data_dir / "system" / "day0_blocking_conditions.json"
    conditions = json.loads(conditions_path.read_text(encoding="utf-8"))
    conditions["current_blocking_count"] = 1
    conditions_path.write_text(json.dumps(conditions), encoding="utf-8")
    result = build_day0_run_daily_preflight(paths=paths)
    assert result["overall_passed"] is False


def test_day0_run_daily_preflight_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day0_paths(tmp_path)
    build_day0_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["day0-run-daily-preflight"]) == 0
