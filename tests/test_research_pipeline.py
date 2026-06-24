"""Tests for v0.5 research pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.reports.research_common import snapshot_diff, snapshot_protected
from trading_core.reports.research_pipeline import run_research_pipeline
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def pipeline_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project_root = workspace / "work" / "trading-core"
    for directory in ["data/orders", "data/trades", "data/portfolios", "data/shadow", "data/experiments"]:
        (project_root / directory).mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def test_research_pipeline_runs_all_reports_without_ledger_writes(pipeline_paths: ProjectPaths) -> None:
    before = snapshot_protected(pipeline_paths)

    result = run_research_pipeline("2026-06-01", "2026-06-30", paths=pipeline_paths)

    assert result["overall_status"] == "success"
    assert {step["status"] for step in result["steps"]} == {"success"}
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["boundary"]["run_daily_called"] is False
    assert snapshot_diff(before, snapshot_protected(pipeline_paths)) == []
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "no run-daily" in report
    assert "no orders/trades/portfolio/accounts" in report


def test_research_pipeline_skip_flags(pipeline_paths: ProjectPaths) -> None:
    result = run_research_pipeline("2026-06-01", "2026-06-30", skip_weekly=True, skip_dashboard=True, paths=pipeline_paths)

    statuses = {step["step"]: step["status"] for step in result["steps"]}
    assert statuses["weekly_research_report"] == "skipped"
    assert statuses["system_dashboard"] == "skipped"
    assert statuses["monthly_research_report"] == "success"


def test_research_pipeline_cli_smoke(pipeline_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: pipeline_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    exit_code = cli.main(["run-research-pipeline", "--start-date", "2026-06-01", "--end-date", "2026-06-30"])

    assert exit_code == 0
    assert (pipeline_paths.outputs_dir / "system" / "RESEARCH_PIPELINE_REPORT-2026-06-01-2026-06-30.md").exists()
