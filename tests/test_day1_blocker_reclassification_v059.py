from pathlib import Path

import pytest

from execution_test_utils import build_execution_stack, make_execution_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.planning.day1_blocker_reclassification import reclassify_day1_blockers_after_execution_hardening


def test_day1_blocker_reclassification_v059(tmp_path: Path) -> None:
    paths = make_execution_paths(tmp_path)
    build_execution_stack(paths)
    result = reclassify_day1_blockers_after_execution_hardening(paths=paths)
    assert result["baseline_day1_blocker_count"] == 3
    assert result["updated_day1_blocker_count"] == 0
    assert len(result["closed_blockers"]) == 3
    assert result["day1_start_allowed"] is False
    assert result["recommended_next_version"]
    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)


def test_day1_blocker_reclassification_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_execution_paths(tmp_path)
    build_execution_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["reclassify-day1-blockers-after-execution-hardening"]) == 0

