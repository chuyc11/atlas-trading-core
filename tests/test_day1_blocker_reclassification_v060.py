from pathlib import Path

import pytest

from baseline_strategy_test_utils import TEST_END, TEST_START, build_baseline_strategy_stack, make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.planning.day1_blocker_reclassification_v060 import reclassify_day1_blockers_after_baseline_strategies


def test_day1_blocker_reclassification_v060(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    build_baseline_strategy_stack(paths)
    result = reclassify_day1_blockers_after_baseline_strategies(paths=paths)
    assert result["baseline_strategy_blocker_closed"] is True
    assert result["updated_day1_blocker_count"] == 0
    assert result["recommended_next_version"] == "v0.6.1-daily-workflow-binding"
    assert result["day1_start_allowed"] is False
    assert result["run_daily_called"] is False
    assert result["forward_dry_run_started"] is False
    assert result["main_ledger_written"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_day1_blocker_reclassification_v060_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    build_baseline_strategy_stack(paths, start_date="2024-01-02", end_date="2024-12-31")
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["reclassify-day1-blockers-after-baseline-strategies"]) == 0

