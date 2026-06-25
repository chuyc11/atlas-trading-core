from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.planning.common import VALID_EVIDENCE_TYPES
from trading_core.planning.mvp_requirement_map import build_mvp_requirement_map
from trading_core.planning.plan_checklist_extractor import build_plan_checklist


def test_mvp_requirement_map_covers_each_requirement(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    checklist = build_plan_checklist(paths=paths)
    result = build_mvp_requirement_map(paths=paths)
    assert len(result["requirements"]) == len(checklist["requirements"])
    for item in result["requirements"]:
        assert "manual_review_required" in item
        assert "missing_evidence" in item
        assert all(evidence["type"] in VALID_EVIDENCE_TYPES for evidence in item["candidate_evidence"])
    assert "MVP Requirement Map" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_mvp_requirement_map_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    build_plan_checklist(paths=paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["mvp-requirement-map"]) == 0

