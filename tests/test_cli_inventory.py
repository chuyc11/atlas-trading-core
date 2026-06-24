"""Tests for CLI inventory."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.system.cli_inventory import build_cli_inventory
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def system_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    (workspace / "work" / "trading-core").mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def test_cli_inventory_generates_json_and_markdown(system_paths: ProjectPaths) -> None:
    result = build_cli_inventory(system_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    commands = {item["command"] for item in result["commands"]}
    assert "run-daily" in commands
    assert "build-features" in commands
    assert "build-labels" in commands
    assert "run-research-pipeline" in commands
    assert all(item["safety"] for item in result["commands"])


def test_cli_inventory_does_not_write_protected_ledgers(system_paths: ProjectPaths) -> None:
    build_cli_inventory(system_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = system_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_cli_inventory_cli_smoke(system_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: system_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["cli-inventory"]) == 0
    assert (system_paths.outputs_dir / "system" / "CLI_INVENTORY.md").exists()
