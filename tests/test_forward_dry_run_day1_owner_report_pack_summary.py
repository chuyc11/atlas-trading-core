from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_owner_report_test_utils import build_owner_report_pack, make_day1_owner_report_paths
from trading_core.forward_dry_run.day1_owner_report_pack_summary import build_day1_owner_report_pack_summary


def test_day1_owner_report_pack_summary_requires_all_reports(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    build_owner_report_pack(paths)
    result = build_day1_owner_report_pack_summary(paths=paths)
    assert result["reports_total"] == 7
    assert result["reports_complete"] == 7
    assert result["missing_reports"] == []
    assert result["owner_report_pack_complete"] is True
    assert result["recommended_next_version"] == "v0.6.3.3-forward-dry-run-data-horizon-extension"


def test_day1_owner_report_pack_summary_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_owner_report_paths(tmp_path)
    build_owner_report_pack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-owner-report-pack-summary"]) == 0
