"""Tests for v0.5 system dashboard."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.reports.system_dashboard import build_system_dashboard
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def system_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project_root = workspace / "work" / "trading-core"
    (project_root / "VERSION").parent.mkdir(parents=True)
    (project_root / "VERSION").write_text("v0.4.0-strategy-experiment-system-audited", encoding="utf-8")
    (project_root / "data" / "experiments").mkdir(parents=True)
    (project_root / "outputs" / "validation").mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def test_system_dashboard_generates_artifact_inventory(system_paths: ProjectPaths) -> None:
    (system_paths.outputs_dir / "validation" / "real_data_validation_summary.json").write_text("{}", encoding="utf-8")

    result = build_system_dashboard(True, True, system_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["current_version"] == "v0.4.0-strategy-experiment-system-audited"
    assert result["artifact_inventory"]["real_data_validation"] is True
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "Known Limitations" in report
    assert "no live trading" in report


def test_system_dashboard_cli_smoke(system_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: system_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    exit_code = cli.main(["system-dashboard", "--include-artifact-inventory", "--include-release-status"])

    assert exit_code == 0
    assert (system_paths.outputs_dir / "system" / "SYSTEM_DASHBOARD.md").exists()
