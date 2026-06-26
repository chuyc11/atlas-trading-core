from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.external_intake.project_catalog import PROJECTS
from trading_core.external_intake.report import build_external_project_intake
from trading_core.storage.file_paths import ProjectPaths


def make_paths(tmp_path: Path) -> ProjectPaths:
    root = tmp_path / "workspace"
    project = root / "work" / "trading-core"
    for relative in ["data/system", "outputs/system", "outputs/audit", "docs", "external_research"]:
        (project / relative).mkdir(parents=True, exist_ok=True)
    return ProjectPaths(root)


def write_fake_external_repos(paths: ProjectPaths, *, skip: set[str] | None = None) -> None:
    skip = skip or set()
    root = paths.project_root / "external_research"
    for project in PROJECTS:
        if project["repo_name"] in skip:
            continue
        repo = root / project["local_dir"]
        repo.mkdir(parents=True, exist_ok=True)
        (repo / "README.md").write_text(f"# {project['repo_name']}\n\nfixture\n", encoding="utf-8")
        (repo / "LICENSE").write_text("MIT License\n", encoding="utf-8")
        (repo / "src").mkdir(exist_ok=True)
        (repo / "src" / "fixture.py").write_text("VALUE = 1\n", encoding="utf-8")


def test_external_project_intake_generates_report_docs_and_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_fake_external_repos(paths)
    result = build_external_project_intake(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["projects_downloaded"] == len(PROJECTS)
    assert result["top_priority_repos"] == ["AlphaSift", "qstock", "daily_stock_analysis", "guiwzh/stock"]
    assert result["recommended_next_version"] == "v0.7.1-a-share-full-market-data-ingestion"
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["broker_connected"] is False
    assert all(project["can_import_directly"] is False for project in result["projects"])
    for relative in [
        "docs/A_SHARE_FULL_MARKET_AI_STOCK_SELECTION_PLAN.md",
        "docs/EXTERNAL_PROJECT_INTAKE.md",
        "docs/EXTERNAL_PROJECT_REUSE_MATRIX.md",
        "docs/V0_7_ARCHITECTURE.md",
        "outputs/system/V0_7_ROADMAP_SUMMARY.md",
    ]:
        assert (paths.project_root / relative).exists()


def test_external_project_intake_blocks_missing_required_repo(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_fake_external_repos(paths, skip={"qstock"})
    result = build_external_project_intake(paths=paths)
    assert result["overall_passed"] is False
    assert "missing_required_external_repo: qstock" in result["blocking_reasons"]


def test_external_project_intake_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    write_fake_external_repos(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["external-project-intake"]) == 0
