"""Tests for boundary regression audit."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.system.boundary_regression_audit import run_boundary_regression_audit
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def boundary_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    (project / "src" / "trading_core" / "signals").mkdir(parents=True)
    (project / "src" / "trading_core" / "broker").mkdir(parents=True)
    (project / "src" / "trading_core" / "experiments").mkdir(parents=True)
    (project / "docs").mkdir(parents=True)
    (project / "tests").mkdir(parents=True)
    (project / "src" / "trading_core" / "daily_run.py").write_text("from trading_core.signals.signal_generator import x\n", encoding="utf-8")
    (project / "src" / "trading_core" / "signals" / "signal_generator.py").write_text("def generate(): pass\n", encoding="utf-8")
    (project / "src" / "trading_core" / "cli.py").write_text("def build_parser(): pass\n", encoding="utf-8")
    (project / "src" / "trading_core" / "broker" / "virtual_broker.py").write_text("# virtual only\n", encoding="utf-8")
    (project / "src" / "trading_core" / "experiments" / "experiment.py").write_text('BOUNDARY = {"write_main_ledger": False}\n', encoding="utf-8")
    return ProjectPaths(workspace_root=workspace)


def test_boundary_audit_generates_json_and_markdown(boundary_paths: ProjectPaths) -> None:
    result = run_boundary_regression_audit(paths=boundary_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["passed"] is True


def test_run_daily_import_labels_is_blocking(boundary_paths: ProjectPaths) -> None:
    (boundary_paths.project_root / "src" / "trading_core" / "daily_run.py").write_text("from trading_core.labels.label_store import build_label_matrix\n", encoding="utf-8")

    result = run_boundary_regression_audit(paths=boundary_paths)

    assert result["passed"] is False
    assert any("run_daily_label_import" in reason for reason in result["blocking_reasons"])


def test_run_daily_import_ml_is_blocking(boundary_paths: ProjectPaths) -> None:
    (boundary_paths.project_root / "src" / "trading_core" / "daily_run.py").write_text("from trading_core.ml.shadow_model import train_ml_shadow_model\n", encoding="utf-8")

    result = run_boundary_regression_audit(paths=boundary_paths)

    assert result["passed"] is False
    assert any("run_daily_ml_import" in reason for reason in result["blocking_reasons"])


def test_experimental_write_main_ledger_true_is_blocking(boundary_paths: ProjectPaths) -> None:
    (boundary_paths.project_root / "src" / "trading_core" / "experiments" / "bad.py").write_text('BOUNDARY = {"write_main_ledger": True}\n', encoding="utf-8")

    result = run_boundary_regression_audit(paths=boundary_paths)

    assert result["passed"] is False
    assert any("main_ledger_writes" in reason for reason in result["blocking_reasons"])


def test_docs_prohibited_live_trading_is_warning_not_blocking(boundary_paths: ProjectPaths) -> None:
    (boundary_paths.project_root / "docs" / "SAFETY_BOUNDARY.md").write_text("not live trading\n", encoding="utf-8")

    result = run_boundary_regression_audit(paths=boundary_paths)

    assert result["passed"] is True
    assert result["warnings"]


def test_tests_forbidden_keyword_is_warning_not_blocking(boundary_paths: ProjectPaths) -> None:
    (boundary_paths.project_root / "tests" / "test_negative.py").write_text('def test_x(): assert "live trading"\n', encoding="utf-8")

    result = run_boundary_regression_audit(paths=boundary_paths)

    assert result["passed"] is True
    assert result["warnings"]


def test_boundary_report_contains_research_only(boundary_paths: ProjectPaths) -> None:
    result = run_boundary_regression_audit(paths=boundary_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "This project remains research-only." in report


def test_boundary_cli_smoke(boundary_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: boundary_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["boundary-regression-audit"]) == 0
