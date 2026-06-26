from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_owner_report_test_utils import make_day1_owner_report_paths
from trading_core.forward_dry_run.day1_continuation_blocker_note import build_day1_continuation_blocker_note


def test_day1_continuation_blocker_note_identifies_data_horizon(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    result = build_day1_continuation_blocker_note(paths=paths)
    assert result["day1_completed"] is True
    assert result["day2_executed"] is False
    assert result["blocker_type"] == "local_data_horizon_insufficient"
    assert result["latest_common_local_data_date"] == "2026-06-25"
    assert result["day1_as_of_date"] == "2026-06-25"
    assert result["boundary"]["external_api_called"] is False


def test_day1_continuation_blocker_note_warns_when_v064_evidence_missing(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    (paths.data_dir / "system" / "forward_dry_run_day2_input_readiness_audit.json").unlink()
    result = build_day1_continuation_blocker_note(paths=paths)
    assert "day2 input readiness evidence not found" in result["warnings"]


def test_day1_continuation_blocker_note_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_owner_report_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-continuation-blocker-note"]) == 0
