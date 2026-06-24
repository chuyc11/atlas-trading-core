"""Tests for latest artifact locator."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.system.latest_artifact import locate_latest_artifact
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def artifact_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    for path in [
        "outputs/reports/WEEKLY_RESEARCH_REPORT-old.md",
        "outputs/audit/SYSTEM_INTEGRITY_AUDIT.md",
        "outputs/system/FINAL_HANDOFF_REVIEW_REPORT.md",
        "data/experiments/strategy_comparison-test.json",
        "data/shadow/ml_shadow_leaderboard-test.json",
    ]:
        file = project / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("{}", encoding="utf-8")
    return ProjectPaths(workspace_root=workspace)


def test_latest_artifact_finds_report_audit_and_handoff(artifact_paths: ProjectPaths) -> None:
    assert locate_latest_artifact("report", paths=artifact_paths)["latest"]["category"] == "report"
    assert locate_latest_artifact("audit", paths=artifact_paths)["latest"]["path"].endswith("SYSTEM_INTEGRITY_AUDIT.md")
    assert locate_latest_artifact("handoff", paths=artifact_paths)["latest"]["path"].endswith("FINAL_HANDOFF_REVIEW_REPORT.md")


def test_latest_artifact_no_candidates_warns(tmp_path: Path) -> None:
    result = locate_latest_artifact("report", paths=ProjectPaths(workspace_root=tmp_path))

    assert result["latest"] is None
    assert result["warnings"]


def test_latest_artifact_all_returns_multiple_types(artifact_paths: ProjectPaths) -> None:
    result = locate_latest_artifact("all", paths=artifact_paths)

    assert "handoff" in result["latest_by_type"]
    assert "audit" in result["latest_by_type"]


def test_open_command_does_not_open_file(artifact_paths: ProjectPaths) -> None:
    result = locate_latest_artifact("handoff", open_command=True, paths=artifact_paths)

    assert result["open_command"]
    assert result["boundary"]["opened_file"] is False


def test_latest_artifact_does_not_write_protected_ledgers(artifact_paths: ProjectPaths) -> None:
    locate_latest_artifact("all", paths=artifact_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = artifact_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_latest_artifact_cli_smoke(artifact_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: artifact_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["latest-artifact", "--type", "handoff", "--open-command"]) == 0
