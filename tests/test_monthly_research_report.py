"""Tests for v0.5 monthly research reporting."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trading_core.reports.monthly_research_report import build_monthly_research_report, month_range
from trading_core.reports.weekly_research_report import build_weekly_research_report
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def monthly_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project_root = workspace / "work" / "trading-core"
    for directory in ["data/reports", "data/shadow", "data/experiments", "outputs/reports"]:
        (project_root / directory).mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_month_range_handles_calendar_month() -> None:
    assert month_range("2026-06") == ("2026-06-01", "2026-06-30")
    assert month_range("2026-12") == ("2026-12-01", "2026-12-31")


def test_monthly_report_generates_from_weekly_artifacts(monthly_paths: ProjectPaths) -> None:
    build_weekly_research_report("2026-06-17", "2026-06-23", paths=monthly_paths)
    _write_json(monthly_paths.data_dir / "shadow" / "ml_shadow_leaderboard-test.json", {"shadow_recommendation": "watch"})
    _write_json(monthly_paths.data_dir / "experiments" / "experiment_registry.json", {"experiments": [{"experiment_id": "EXP-test"}]})
    _write_json(monthly_paths.data_dir / "experiments" / "parameter_sweep-EXP-test.json", {"experiment_id": "EXP-test"})

    result = build_monthly_research_report("2026-06-01", "2026-06-30", include_weekly=True, include_experiments=True, include_ml_shadow=True, paths=monthly_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["weekly_reports"]["count"] == 1
    assert result["experiments"]["experiment_count"] == 1
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "not an admission gate" in report
    assert "no active promotion" in report
    assert "does not validate forward 30d dry-run" in report


def test_monthly_report_missing_weekly_does_not_crash(monthly_paths: ProjectPaths) -> None:
    result = build_monthly_research_report(month="2026-06", include_weekly=True, paths=monthly_paths)

    assert result["weekly_reports"]["count"] == 0
    assert "No weekly research summaries found for this period." in result["warnings"]


def test_monthly_research_cli_smoke(monthly_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: monthly_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    exit_code = cli.main(["monthly-research-report", "--month", "2026-06"])

    assert exit_code == 0
    assert (monthly_paths.outputs_dir / "reports" / "MONTHLY_RESEARCH_REPORT-2026-06-01-2026-06-30.md").exists()
