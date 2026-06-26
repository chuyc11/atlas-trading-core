from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_owner_report_test_utils import build_owner_report_pack, make_day1_owner_report_paths
from trading_core.forward_dry_run.day1_owner_report_audit import audit_day1_owner_report_pack


def test_day1_owner_report_audit_passes_complete_pack(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    build_owner_report_pack(paths)
    result = audit_day1_owner_report_pack(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["warnings"] == []
    assert result["summary"]["owner_report_pack_complete"] is True
    assert result["summary"]["day1_completed"] is True
    assert result["summary"]["day2_executed"] is False
    assert result["boundary"]["live_trading_ready"] is False


def test_day1_owner_report_audit_blocks_forbidden_positive_claim(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    build_owner_report_pack(paths)
    report = paths.outputs_dir / "forward_dry_run" / "day_001" / "reports" / "DAY1_OWNER_SUMMARY_REPORT.md"
    report.write_text(report.read_text(encoding="utf-8") + "\nstrategy effectiveness proven\n", encoding="utf-8")
    result = audit_day1_owner_report_pack(paths=paths)
    assert result["overall_passed"] is False
    assert any("forbidden positive wording" in item for item in result["blocking_reasons"])


def test_day1_owner_report_audit_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_owner_report_paths(tmp_path)
    build_owner_report_pack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-forward-dry-run-day1-owner-report-pack"]) == 0
