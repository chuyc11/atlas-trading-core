from __future__ import annotations

from pathlib import Path

from trading_core import cli
from trading_core.reports.acceptance_report import VERSION, build_acceptance_report, write_acceptance_materials
from trading_core.storage.file_paths import project_paths


def test_acceptance_report_contains_release_boundaries() -> None:
    report = build_acceptance_report(test_count=83)

    assert VERSION in report
    assert "83 tests passed" in report
    assert "No broker connection" in report
    assert "No live trading" in report
    assert "No ML" in report
    assert "No RL" in report
    assert "No LLM trading decision" in report


def test_acceptance_report_command_output_file(tmp_path: Path) -> None:
    result = write_acceptance_materials(project_paths(tmp_path), test_count=83)
    path = Path(result["report_path"])

    assert path.name == "SYSTEM_ACCEPTANCE_REPORT.md"
    assert path.exists()
    assert "v0.1.0-core-hardened" in path.read_text(encoding="utf-8")


def test_acceptance_report_cli_writes_freeze_report(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cli, "project_paths", lambda: project_paths(tmp_path))

    assert cli.main(["acceptance-report"]) == 0

    report_path = tmp_path / "work" / "trading-core" / "outputs" / "SYSTEM_ACCEPTANCE_REPORT.md"
    assert report_path.exists()
    assert "83 tests passed" in report_path.read_text(encoding="utf-8")
