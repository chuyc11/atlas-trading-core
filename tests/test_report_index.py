"""Tests for report index."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.system.report_index import TRUST_LEVELS, build_report_index
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def report_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    for path in [
        "outputs/system/FINAL_HANDOFF_REVIEW_REPORT.md",
        "outputs/audit/SYSTEM_INTEGRITY_AUDIT.md",
        "outputs/experiments/EXPERIMENT_DASHBOARD.md",
        "outputs/reports/WEEKLY_RESEARCH_REPORT-2026-06-17-2026-06-23.md",
    ]:
        file = project / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("# report", encoding="utf-8")
    return ProjectPaths(workspace_root=workspace)


def test_report_index_generates_json_and_markdown(report_paths: ProjectPaths) -> None:
    result = build_report_index(True, True, True, report_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["reports"]


def test_report_index_missing_reports_dir_does_not_crash(tmp_path: Path) -> None:
    result = build_report_index(paths=ProjectPaths(workspace_root=tmp_path))

    assert Path(result["json_path"]).exists()
    assert result["warnings"]


def test_report_index_recognizes_categories_and_trust(report_paths: ProjectPaths) -> None:
    result = build_report_index(True, True, True, report_paths)
    categories = {item["category"] for item in result["reports"]}

    assert {"system", "audit", "experiments"}.issubset(categories)
    assert all(item["trust_level"] in TRUST_LEVELS for item in result["reports"])


def test_report_index_does_not_write_protected_ledgers(report_paths: ProjectPaths) -> None:
    build_report_index(True, True, True, report_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = report_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_report_index_cli_smoke(report_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: report_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["report-index", "--include-audit", "--include-experiments", "--include-system"]) == 0
