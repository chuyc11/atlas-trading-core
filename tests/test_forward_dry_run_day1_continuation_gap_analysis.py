from __future__ import annotations

import json
from pathlib import Path

import pytest

from forward_dry_run_day1_continuation_test_utils import make_day1_continuation_paths
from trading_core.forward_dry_run.day1_continuation_gap_analysis import build_day1_continuation_gap_analysis


def test_day1_continuation_gap_analysis_detects_derivable_gap(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    result = build_day1_continuation_gap_analysis(paths=paths)
    assert result["overall_passed"] is True
    assert result["day1_core_execution_passed"] is True
    assert result["v064_preflight_blocked"] is True
    assert len(result["missing_artifacts"]) == 4
    assert result["missing_artifacts_derivable"] is True
    assert result["day2_execution_allowed_in_this_stage"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_day1_continuation_gap_analysis_handles_missing_preflight(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    (paths.data_dir / "system" / "forward_dry_run_day2_continuation_preflight.json").unlink()
    result = build_day1_continuation_gap_analysis(paths=paths)
    assert result["overall_passed"] is False
    assert "v064_blocking_preflight_missing" in result["blocking_reasons"]


def test_day1_continuation_gap_analysis_blocks_failed_day1_audit(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    audit_path = paths.data_dir / "forward_dry_run" / "day_001" / "day1_post_execution_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit["overall_passed"] = False
    audit["blocking_reasons"] = ["forced"]
    audit_path.write_text(json.dumps(audit), encoding="utf-8")
    result = build_day1_continuation_gap_analysis(paths=paths)
    assert result["overall_passed"] is False
    assert "day1_post_execution_audit_passed=false" in result["blocking_reasons"]


def test_day1_continuation_gap_analysis_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_continuation_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-continuation-gap-analysis"]) == 0

