"""Tests for v0.5 reporting system audit."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.reports.reporting_system_audit import RELEASE_CANDIDATE, audit_reporting_system
from trading_core.reports.research_pipeline import run_research_pipeline
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def audit_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project_root = workspace / "work" / "trading-core"
    for directory in ["data/orders", "data/trades", "data/portfolios", "data/accounts", "outputs/audit"]:
        (project_root / directory).mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def test_reporting_system_audit_passes_after_pipeline(audit_paths: ProjectPaths) -> None:
    run_research_pipeline("2026-06-01", "2026-06-30", paths=audit_paths)

    result = audit_reporting_system(paths=audit_paths)

    assert result["release_candidate"] == RELEASE_CANDIDATE
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["boundary"]["orders_written"] is False
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "No strategy state was changed." in report
    assert "This does not validate forward 30d dry-run." in report


def test_reporting_system_audit_fails_when_reports_missing(audit_paths: ProjectPaths) -> None:
    result = audit_reporting_system(paths=audit_paths)

    assert result["overall_passed"] is False
    assert result["blocking_reasons"]


def test_reporting_system_audit_cli_smoke(audit_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    run_research_pipeline("2026-06-01", "2026-06-30", paths=audit_paths)
    monkeypatch.setattr(cli, "project_paths", lambda: audit_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    exit_code = cli.main(["audit-reporting-system"])

    assert exit_code == 0
    assert (audit_paths.outputs_dir / "audit" / "REPORTING_SYSTEM_AUDIT.md").exists()
