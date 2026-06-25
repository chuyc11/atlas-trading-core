from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import build_planning_stack, make_planning_paths
from trading_core.planning.common import RELEASE_CANDIDATE
from trading_core.planning.plan_alignment_audit import audit_plan_alignment


def test_plan_alignment_audit_passes_and_recommends_tag(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    build_planning_stack(paths)
    result = audit_plan_alignment(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["summary"]["requirements_total"] == 24
    assert result["summary"]["recommended_next_version"]
    assert RELEASE_CANDIDATE in Path(result["report_path"]).read_text(encoding="utf-8")
    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)


def test_plan_alignment_audit_blocks_missing_artifacts_and_boundary_violations(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    build_planning_stack(paths)
    (paths.data_dir / "system" / "plan_checklist.json").unlink()
    classification_path = paths.data_dir / "system" / "mvp_gap_classification.json"
    classification = json.loads(classification_path.read_text(encoding="utf-8"))
    classification["requirements"] = classification["requirements"][:23]
    classification_path.write_text(json.dumps(classification), encoding="utf-8")
    next_work = paths.data_dir / "system" / "next_work_register.json"
    next_work_payload = json.loads(next_work.read_text(encoding="utf-8"))
    next_work_payload["recommended_next_version"] = ""
    next_work_payload["boundary"]["run_daily_called"] = True
    next_work_payload["boundary"]["forward_dry_run_started"] = True
    next_work_payload["boundary"]["main_ledger_written"] = True
    next_work.write_text(json.dumps(next_work_payload), encoding="utf-8")
    (paths.outputs_dir / "system" / "BAD.md").write_text(
        "ML approved for trading\nLLM approved for trading\nRL approved for trading\nlive trading ready\n",
        encoding="utf-8",
    )
    result = audit_plan_alignment(paths=paths)
    assert result["overall_passed"] is False
    joined = "\n".join(result["blocking_reasons"])
    for token in ["plan_checklist", "mvp_gap_classification", "next_work_register", "boundary", "wording"]:
        assert token in joined


def test_plan_alignment_audit_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    build_planning_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-plan-alignment"]) == 0

