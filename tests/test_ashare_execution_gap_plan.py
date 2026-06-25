from pathlib import Path

import pytest

from execution_test_utils import make_execution_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.execution.ashare_execution_gap_plan import build_ashare_execution_gap_plan


def test_ashare_execution_gap_plan_reads_blockers(tmp_path: Path) -> None:
    paths = make_execution_paths(tmp_path)
    result = build_ashare_execution_gap_plan(paths=paths)
    assert result["baseline_day1_blocker_count"] == 3
    assert result["target_day1_blocker_count"] == 0
    assert result["work_items"]
    assert result["boundary"]["run_daily_called"] is False
    assert "A-Share Execution Gap Plan" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_ashare_execution_gap_plan_missing_input_blocks(tmp_path: Path) -> None:
    paths = make_execution_paths(tmp_path)
    (paths.data_dir / "system" / "day1_blocker_classification.json").unlink()
    result = build_ashare_execution_gap_plan(paths=paths)
    assert result["overall_passed"] is False
    assert result["warnings"]


def test_ashare_execution_gap_plan_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_execution_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["ashare-execution-gap-plan"]) == 0

