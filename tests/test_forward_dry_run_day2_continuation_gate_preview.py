from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_continuation_test_utils import make_day1_continuation_paths
from trading_core.forward_dry_run.day2_continuation_gate_preview import build_day2_continuation_gate_preview


def test_day2_continuation_gate_preview_is_structural_only(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    result = build_day2_continuation_gate_preview(paths=paths)
    assert result["overall_passed"] is True
    assert result["day2_continuation_structurally_eligible"] is True
    assert result["operator_review_required"] is True
    assert result["day2_execution_authorized_in_this_artifact"] is False
    assert result["day2_executed"] is False
    assert result["recommended_next_version"] == "v0.6.4-forward-dry-run-day2-continuation"
    assert result["boundary"]["run_daily_called_for_day2"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_day2_continuation_gate_preview_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_continuation_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day2-continuation-gate-preview"]) == 0

