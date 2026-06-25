from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, write_json
from planning_test_utils import make_planning_paths
from trading_core.planning.artifact_coverage_scanner import build_artifact_coverage_scan
from trading_core.planning.mvp_gap_classifier import classify_mvp_gaps
from trading_core.planning.mvp_requirement_map import build_mvp_requirement_map
from trading_core.planning.plan_checklist_extractor import build_plan_checklist


def test_mvp_gap_classifier_generates_statuses_and_blockers(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    build_plan_checklist(paths=paths)
    build_mvp_requirement_map(paths=paths)
    build_artifact_coverage_scan(paths=paths)
    result = classify_mvp_gaps(paths=paths)
    assert result["summary"]["requirements_total"] == 24
    assert all(item["status"] in {"passed", "partial", "missing", "deferred", "not_applicable"} for item in result["requirements"])
    by_id = {item["requirement_id"]: item for item in result["requirements"]}
    assert by_id["R008"]["day1_blocker"] is True
    assert by_id["R022"]["day1_blocker"] is False
    assert by_id["R023"]["day1_blocker"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert "MVP Gap Classification" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_mvp_gap_classifier_marks_critical_missing_as_day1_blocker(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    checklist = build_plan_checklist(paths=paths)
    requirement_map = build_mvp_requirement_map(paths=paths)
    for item in requirement_map["requirements"]:
        if item["requirement_id"] == "R001":
            item["candidate_evidence"] = []
    map_path = paths.data_dir / "system" / "custom_map.json"
    write_json(map_path, requirement_map)
    result = classify_mvp_gaps(checklist_path=checklist["json_path"], requirement_map_path=str(map_path), paths=paths)
    by_id = {item["requirement_id"]: item for item in result["requirements"]}
    assert by_id["R001"]["status"] == "missing"
    assert by_id["R001"]["day1_blocker"] is True


def test_mvp_gap_classifier_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    build_plan_checklist(paths=paths)
    build_mvp_requirement_map(paths=paths)
    build_artifact_coverage_scan(paths=paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["classify-mvp-gaps"]) == 0
