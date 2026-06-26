from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_continuation_test_utils import build_day1_continuation_stack, make_day1_continuation_paths
from trading_core.planning.day1_continuation_reclassification_v0631 import reclassify_day1_continuation_artifacts_v0631


def test_day1_continuation_reclassification_v0631(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    build_day1_continuation_stack(paths)
    result = reclassify_day1_continuation_artifacts_v0631(paths=paths)
    assert result["reclassification_id"] == "DAY1-CONTINUATION-RECLASSIFICATION-V0631"
    assert result["continuation_artifact_gap_resolved"] is True
    assert result["remaining_continuation_artifact_gap_count"] == 0
    assert result["day2_blocker_count"] == 0
    assert result["day2_executed"] is False
    assert result["recommended_next_version"] == "v0.6.4-forward-dry-run-day2-continuation"
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()


def test_day1_continuation_reclassification_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_continuation_paths(tmp_path)
    build_day1_continuation_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["reclassify-day1-continuation-artifacts-v0631"]) == 0

