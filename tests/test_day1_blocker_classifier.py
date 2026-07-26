from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, write_json
from planning_test_utils import build_planning_stack, make_planning_paths
from trading_core.planning.day1_blocker_classifier import classify_day1_blockers


def test_day1_blocker_classifier_extracts_blockers(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    build_planning_stack(paths)
    result = classify_day1_blockers(paths=paths)
    assert result["day1_allowed"] is False
    assert result["blocking_count"] > 0
    assert any(item["blocker_id"] == "missing_limit_up_down_handling" for item in result["blockers"])
    assert any(item["requirement_id"] == "R022" for item in result["deferred_non_blocking"])
    assert result["boundary"]["run_daily_called"] is False
    assert "Day-1 Blocker Classification" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_day1_blocker_classifier_keeps_day1_disallowed_without_manual_confirmation(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    payload = {
        "requirements": [
            {"requirement_id": "R001", "name": "trading_calendar_correct", "status": "passed", "day1_blocker": False, "rationale": ""},
            {"requirement_id": "R022", "name": "no_rl_llm_trading_decision_boundary", "status": "deferred", "day1_blocker": False, "rationale": ""},
        ]
    }
    path = paths.data_dir / "system" / "custom_gap.json"
    write_json(path, payload)
    result = classify_day1_blockers(mvp_gap_classification_path=str(path), paths=paths)
    assert result["blocking_count"] == 0
    assert result["day1_allowed"] is False
    assert result["manual_confirmation_complete"] is False


def test_day1_blocker_classifier_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    build_planning_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["classify-day1-blockers"]) == 0

