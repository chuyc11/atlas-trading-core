"""Tests for quick status."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.system.quick_status import build_quick_status
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def quick_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    project.mkdir(parents=True)
    (project / "VERSION").write_text("v0.5.1-system-integrity-and-documentation", encoding="utf-8")
    for path in ["outputs/system/FINAL_HANDOFF_REVIEW_REPORT.md", "outputs/system/SYSTEM_DASHBOARD.md", "outputs/audit/SYSTEM_INTEGRITY_AUDIT.md"]:
        file = project / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("# report", encoding="utf-8")
    return ProjectPaths(workspace_root=workspace)


def test_quick_status_generates_json_and_markdown(quick_paths: ProjectPaths) -> None:
    result = build_quick_status(quick_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["current_version"] == "v0.5.1-system-integrity-and-documentation"
    assert "forward 30d dry-run not completed" in result["known_limitations"]
    assert result["recommended_next_command"]


def test_command_cookbook_exists() -> None:
    assert Path("docs/COMMAND_COOKBOOK.md").exists()


def test_quick_status_does_not_write_protected_ledgers(quick_paths: ProjectPaths) -> None:
    build_quick_status(quick_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = quick_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_quick_status_cli_smoke(quick_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: quick_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["quick-status"]) == 0
