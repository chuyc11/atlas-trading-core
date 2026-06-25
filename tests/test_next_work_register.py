from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, write_json
from planning_test_utils import build_planning_stack, make_planning_paths
from trading_core.planning.next_work_register import build_next_work_register


def test_next_work_register_recommends_execution_hardening(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    build_planning_stack(paths)
    result = build_next_work_register(paths=paths)
    assert result["recommended_next_version"] == "v0.5.9-ashare-execution-rules-hardening"
    assert result["boundary"]["run_daily_called"] is False
    assert "Next Work Register" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_next_work_register_version_rules(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    gap = {"requirements": [{"requirement_id": "R016", "name": "baseline_rule_strategies", "status": "partial"}]}
    day1 = {"blockers": []}
    gap_path = paths.data_dir / "system" / "gap.json"
    day1_path = paths.data_dir / "system" / "day1.json"
    write_json(gap_path, gap)
    write_json(day1_path, day1)
    assert build_next_work_register(mvp_gap_classification_path=str(gap_path), day1_blocker_classification_path=str(day1_path), paths=paths)["recommended_next_version"] == "v0.6.0-baseline-strategy-pack"
    gap["requirements"] = [{"requirement_id": "R016", "name": "baseline_rule_strategies", "status": "passed"}, {"requirement_id": "R017", "name": "daily_report_generation", "status": "missing"}]
    write_json(gap_path, gap)
    assert build_next_work_register(mvp_gap_classification_path=str(gap_path), day1_blocker_classification_path=str(day1_path), paths=paths)["recommended_next_version"] == "v0.6.1-daily-workflow-binding"
    gap["requirements"] = [{"requirement_id": "R016", "name": "baseline_rule_strategies", "status": "passed"}, {"requirement_id": "R017", "name": "daily_report_generation", "status": "passed"}]
    write_json(gap_path, gap)
    assert build_next_work_register(mvp_gap_classification_path=str(gap_path), day1_blocker_classification_path=str(day1_path), paths=paths)["recommended_next_version"] == "v0.6.2-forward-dry-run-start-authorization-pack"


def test_next_work_register_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    build_planning_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["next-work-register"]) == 0

