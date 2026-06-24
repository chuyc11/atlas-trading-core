"""Tests for project timezone configuration."""

from __future__ import annotations

from trading_core.config_loader import load_all_configs, load_config
from trading_core.reports.project_status_report import build_project_status_report
from trading_core.reports.system_dashboard import build_system_dashboard
from trading_core.storage.file_paths import ProjectPaths


def test_default_project_timezone_is_asia_shanghai() -> None:
    settings = load_config("settings.yaml")

    assert settings["project_timezone"] == "Asia/Shanghai"


def test_all_default_configs_do_not_use_asia_tokyo() -> None:
    configs = load_all_configs()

    assert "Asia/Tokyo" not in str(configs)


def test_system_reports_do_not_show_asia_tokyo(tmp_path) -> None:
    workspace = tmp_path
    project_root = workspace / "work" / "trading-core"
    project_root.mkdir(parents=True)
    (project_root / "VERSION").write_text("v0.5.1-validation-gap-remediation", encoding="utf-8")
    paths = ProjectPaths(workspace_root=workspace)

    dashboard = build_system_dashboard(True, True, paths)
    project_status = build_project_status_report(True, True, paths)

    assert "Asia/Tokyo" not in str(dashboard)
    assert "Asia/Tokyo" not in str(project_status)
