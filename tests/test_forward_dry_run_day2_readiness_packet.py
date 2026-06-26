from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_continuation_test_utils import make_day1_continuation_paths
from trading_core.forward_dry_run.day2_readiness_packet import build_day2_readiness_packet


def test_day2_readiness_packet_materializes_without_starting_day2(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    result = build_day2_readiness_packet(paths=paths)
    assert result["overall_passed"] is True
    assert result["day1_passed"] is True
    assert result["day1_artifacts_complete"] is True
    assert result["next_day_index"] == 2
    assert result["operator_review_required"] is True
    assert result["day2_prompt_eligible_after_operator_review"] is True
    assert result["day2_executed"] is False
    assert result["boundary"]["forward_dry_run_day2_started"] is False
    assert result["boundary"]["run_daily_called_for_day2"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_day2_readiness_packet_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_continuation_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day2-readiness-packet"]) == 0

