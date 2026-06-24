"""Tests for system smoke test."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.system.system_smoke_test import DOCS, run_system_smoke_test
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def smoke_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    project.mkdir(parents=True)
    (project / "VERSION").write_text("v0.5.1-system-integrity-and-documentation", encoding="utf-8")
    (project / "README.md").write_text("# Trading Core", encoding="utf-8")
    for doc in DOCS:
        path = project / doc
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# doc", encoding="utf-8")
    return ProjectPaths(workspace_root=workspace)


def test_smoke_generates_json_and_markdown(smoke_paths: ProjectPaths) -> None:
    result = run_system_smoke_test(fast=True, paths=smoke_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["passed"] is True


def test_smoke_version_missing_failed(smoke_paths: ProjectPaths) -> None:
    (smoke_paths.project_root / "VERSION").unlink()

    result = run_system_smoke_test(fast=True, paths=smoke_paths)

    assert result["passed"] is False
    assert any("version_exists" in reason for reason in result["blocking_reasons"])


def test_smoke_readme_missing_failed(smoke_paths: ProjectPaths) -> None:
    (smoke_paths.project_root / "README.md").unlink()

    result = run_system_smoke_test(fast=True, paths=smoke_paths)

    assert result["passed"] is False
    assert any("readme_exists" in reason for reason in result["blocking_reasons"])


def test_smoke_missing_optional_artifact_warns(smoke_paths: ProjectPaths) -> None:
    result = run_system_smoke_test(fast=True, paths=smoke_paths)

    assert result["warnings"]
    assert any("optional artifact missing" in warning for warning in result["warnings"])


def test_smoke_does_not_write_protected_ledgers(smoke_paths: ProjectPaths) -> None:
    run_system_smoke_test(fast=True, paths=smoke_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = smoke_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_smoke_cli_smoke(smoke_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: smoke_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["system-smoke-test", "--fast"]) == 0
    assert (smoke_paths.outputs_dir / "system" / "SYSTEM_SMOKE_TEST.md").exists()
