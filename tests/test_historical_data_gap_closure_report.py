from __future__ import annotations

import pytest

from global_briefing_test_utils import make_paths
from test_historical_data_gap_closure_workflow import _seed_fixture_manifest
from trading_core.global_briefing.historical_data_gap_closure_report import build_historical_data_gap_closure_report
from trading_core.global_briefing.historical_data_gap_closure_workflow import close_historical_data_gaps


def test_gap_closure_report_json_markdown_and_cli(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _seed_fixture_manifest(paths)
    close_historical_data_gaps(start_date="2024-01-02", end_date="2024-01-08", replay_start_date="2024-01-02", replay_end_date="2024-01-08", min_coverage=0.60, paths=paths)
    result = build_historical_data_gap_closure_report(paths=paths)
    assert result["overall_status"] == "passed"
    assert result["available_packages"]["current"] >= 8
    assert result["grouped_warning_output_enabled"] is True
    assert "Historical Data Gap Closure Report" in open(result["report_path"], encoding="utf-8").read()
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False

    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["historical-data-gap-closure-report"]) == 0
