from __future__ import annotations

import json
from pathlib import Path

import pytest

from forward_dry_run_day1_test_utils import build_day1_authorized_stack, make_day1_paths
from trading_core.forward_dry_run.day1_pre_execution_gate import build_day1_pre_execution_gate


def test_day1_pre_execution_gate_passes_with_authorized_stack(tmp_path: Path) -> None:
    paths = make_day1_paths(tmp_path)
    build_day1_authorized_stack(paths)
    result = build_day1_pre_execution_gate(paths=paths, git_status_clean_override=True)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["checks"]["git_status_clean_before_execution"] is True
    assert result["checks"]["broker_live_config_absent"] is True
    assert result["checks"]["day1_data_eligible"] is True
    assert result["data_eligibility"]["as_of_date"] == "2026-06-25"


def test_day1_pre_execution_gate_blocks_dirty_git_and_prior_execution(tmp_path: Path) -> None:
    paths = make_day1_paths(tmp_path)
    build_day1_authorized_stack(paths)
    result = build_day1_pre_execution_gate(paths=paths, git_status_clean_override=False)
    assert result["overall_passed"] is False
    assert "git_status_clean_before_execution=false" in result["blocking_reasons"]

    execution_path = paths.data_dir / "forward_dry_run" / "day_001" / "day1_virtual_execution_result.json"
    execution_path.parent.mkdir(parents=True, exist_ok=True)
    execution_path.write_text(json.dumps({"executed": True}), encoding="utf-8")
    rerun = build_day1_pre_execution_gate(paths=paths, git_status_clean_override=True)
    assert "day_001_not_already_executed=false" in rerun["blocking_reasons"]


def test_day1_pre_execution_gate_blocks_missing_manual_confirmation(tmp_path: Path) -> None:
    paths = make_day1_paths(tmp_path)
    build_day1_authorized_stack(paths)
    checklist_path = paths.data_dir / "system" / "forward_dry_run_manual_confirmation_checklist_v2_completed.json"
    checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
    checklist["manual_confirmation_complete"] = False
    checklist_path.write_text(json.dumps(checklist), encoding="utf-8")
    result = build_day1_pre_execution_gate(paths=paths, git_status_clean_override=True)
    assert result["overall_passed"] is False
    assert "manual_confirmation_complete=false" in result["blocking_reasons"]


def test_day1_pre_execution_gate_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_paths(tmp_path)
    build_day1_authorized_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-pre-execution-gate"]) == 0
