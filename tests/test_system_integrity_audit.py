"""Tests for system integrity audit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trading_core.system.system_integrity_audit import DOCS, RELEASE_CANDIDATE, run_system_integrity_audit
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def integrity_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    project.mkdir(parents=True)
    for doc in DOCS:
        path = project / doc
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# ok\nresearch-only\n", encoding="utf-8")
    _write_json(project / "data" / "system" / "cli_inventory.json", {"commands": [{"command": "run-daily", "safety": ["virtual"]}, {"command": "run-research-pipeline", "safety": ["research"]}]})
    (project / "outputs" / "system").mkdir(parents=True, exist_ok=True)
    (project / "outputs" / "system" / "CLI_INVENTORY.md").write_text("# CLI", encoding="utf-8")
    _write_json(project / "data" / "system" / "artifact_inventory.json", {"artifacts": [{"path": "data/experiments"}, {"path": "data/system"}, {"path": "outputs/audit"}]})
    (project / "outputs" / "system" / "ARTIFACT_INVENTORY.md").write_text("# Artifacts", encoding="utf-8")
    _write_json(project / "data" / "system" / "system_smoke_test.json", {"passed": True})
    (project / "outputs" / "system" / "SYSTEM_SMOKE_TEST.md").write_text("# Smoke", encoding="utf-8")
    _write_json(project / "data" / "system" / "boundary_regression_audit.json", {"passed": True})
    (project / "outputs" / "audit").mkdir(parents=True, exist_ok=True)
    (project / "outputs" / "audit" / "BOUNDARY_REGRESSION_AUDIT.md").write_text("# Boundary", encoding="utf-8")
    return ProjectPaths(workspace_root=workspace)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_system_integrity_audit_generates_json_and_markdown(integrity_paths: ProjectPaths) -> None:
    result = run_system_integrity_audit(integrity_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["overall_passed"] is True


def test_missing_readme_blocking(integrity_paths: ProjectPaths) -> None:
    (integrity_paths.project_root / "README.md").unlink()

    result = run_system_integrity_audit(integrity_paths)

    assert result["overall_passed"] is False
    assert any("README.md" in reason for reason in result["blocking_reasons"])


def test_missing_cli_inventory_blocking(integrity_paths: ProjectPaths) -> None:
    (integrity_paths.data_dir / "system" / "cli_inventory.json").unlink()

    result = run_system_integrity_audit(integrity_paths)

    assert result["overall_passed"] is False
    assert any("cli_inventory" in reason for reason in result["blocking_reasons"])


def test_failed_smoke_test_blocking(integrity_paths: ProjectPaths) -> None:
    _write_json(integrity_paths.data_dir / "system" / "system_smoke_test.json", {"passed": False})

    result = run_system_integrity_audit(integrity_paths)

    assert result["overall_passed"] is False
    assert any("smoke_test" in reason for reason in result["blocking_reasons"])


def test_failed_boundary_regression_blocking(integrity_paths: ProjectPaths) -> None:
    _write_json(integrity_paths.data_dir / "system" / "boundary_regression_audit.json", {"passed": False})

    result = run_system_integrity_audit(integrity_paths)

    assert result["overall_passed"] is False
    assert any("boundary_regression" in reason for reason in result["blocking_reasons"])


def test_forbidden_wording_live_trading_ready_blocking(integrity_paths: ProjectPaths) -> None:
    (integrity_paths.project_root / "docs" / "RUNBOOK.md").write_text("live trading ready\n", encoding="utf-8")

    result = run_system_integrity_audit(integrity_paths)

    assert result["overall_passed"] is False
    assert any("live trading ready" in reason for reason in result["blocking_reasons"])


def test_integrity_report_contains_recommended_tag_and_forward_boundary(integrity_paths: ProjectPaths) -> None:
    result = run_system_integrity_audit(integrity_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert RELEASE_CANDIDATE in report
    assert "This does not validate forward 30d dry-run." in report


def test_system_integrity_cli_smoke(integrity_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: integrity_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["system-integrity-audit"]) == 0
