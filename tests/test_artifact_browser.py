"""Tests for artifact browser."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trading_core.system.artifact_browser import build_artifact_browser
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def browser_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    (project / "outputs" / "system").mkdir(parents=True)
    (project / "outputs" / "system" / "FINAL_HANDOFF_REVIEW_REPORT.md").write_text("# handoff", encoding="utf-8")
    _write_json(project / "data" / "system" / "artifact_inventory.json", {"artifacts": [{"artifact": "x.json", "path": "data/system/x.json", "exists": True}]})
    _write_json(project / "data" / "system" / "report_index.json", {"reports": [{"title": "Final Handoff Review Report", "path": "outputs/system/FINAL_HANDOFF_REVIEW_REPORT.md", "trust_level": "engineering_audit"}]})
    return ProjectPaths(workspace_root=workspace)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_artifact_browser_generates_json_and_markdown(browser_paths: ProjectPaths) -> None:
    result = build_artifact_browser(paths=browser_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()


def test_artifact_browser_missing_inventory_does_not_crash(tmp_path: Path) -> None:
    result = build_artifact_browser(paths=ProjectPaths(workspace_root=tmp_path))

    assert Path(result["json_path"]).exists()
    assert result["warnings"]


def test_artifact_browser_start_here_and_not_trading_section(browser_paths: ProjectPaths) -> None:
    result = build_artifact_browser(paths=browser_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "FINAL_HANDOFF_REVIEW_REPORT" in report
    assert "## 5. Not Trading Authorization" in report


def test_artifact_browser_does_not_write_protected_ledgers(browser_paths: ProjectPaths) -> None:
    build_artifact_browser(paths=browser_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = browser_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_artifact_browser_cli_smoke(browser_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: browser_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["artifact-browser"]) == 0
