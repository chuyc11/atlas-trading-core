"""Tests for artifact inventory."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.system.artifact_inventory import build_artifact_inventory
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def inventory_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    (project / "data" / "experiments").mkdir(parents=True)
    (project / "outputs" / "audit").mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def test_artifact_inventory_generates_json_and_markdown(inventory_paths: ProjectPaths) -> None:
    result = build_artifact_inventory(inventory_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    paths = {item["path"] for item in result["artifacts"]}
    assert "data/experiments" in paths
    assert "outputs/audit" in paths


def test_artifact_inventory_missing_artifacts_do_not_crash(inventory_paths: ProjectPaths) -> None:
    result = build_artifact_inventory(inventory_paths)

    assert result["warnings"]
    assert any(item["exists"] is False for item in result["artifacts"])


def test_artifact_inventory_does_not_write_protected_ledgers(inventory_paths: ProjectPaths) -> None:
    build_artifact_inventory(inventory_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = inventory_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_artifact_inventory_cli_smoke(inventory_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: inventory_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["artifact-inventory"]) == 0
    assert (inventory_paths.outputs_dir / "system" / "ARTIFACT_INVENTORY.md").exists()
