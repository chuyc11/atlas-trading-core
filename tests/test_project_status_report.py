"""Tests for v0.5 project status reporting."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.reports.project_status_report import build_project_status_report
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def project_status_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    (workspace / "work" / "trading-core").mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def test_project_status_report_contains_boundaries(project_status_paths: ProjectPaths) -> None:
    result = build_project_status_report(True, True, project_status_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert "v0.4.0-strategy-experiment-system-audited" in result["completed_versions"]
    assert "forward 30d dry-run" in result["open_items"]
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "research-only" in report
    assert "no active promotion" in report


def test_project_status_cli_smoke(project_status_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: project_status_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    exit_code = cli.main(["project-status-report", "--include-next-steps", "--include-risk-register"])

    assert exit_code == 0
    assert (project_status_paths.outputs_dir / "system" / "PROJECT_STATUS_REPORT.md").exists()
