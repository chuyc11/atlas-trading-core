"""Tests for usability audit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trading_core.system.usability_audit import RELEASE_CANDIDATE, run_usability_audit
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def usability_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    _write_text(project / "outputs/system/FINAL_HANDOFF_REVIEW_REPORT.md", "381 passed, 1 skipped\nno eligible shadow candidate\n")
    _write_json(project / "data/system/report_index.json", {"reports": []})
    _write_text(project / "outputs/system/REPORT_INDEX.md", "FINAL_HANDOFF_REVIEW_REPORT.md\nSYSTEM_INTEGRITY_AUDIT.md\n")
    _write_json(project / "data/system/latest_artifact.json", {"latest": {"path": "outputs/system/FINAL_HANDOFF_REVIEW_REPORT.md"}})
    _write_text(project / "outputs/system/LATEST_ARTIFACT.md", "FINAL_HANDOFF_REVIEW_REPORT.md\n")
    _write_json(project / "data/system/artifact_browser.json", {"ok": True})
    _write_text(project / "outputs/system/ARTIFACT_BROWSER.md", "## 5. Not Trading Authorization\n")
    _write_json(project / "data/system/quick_status.json", {"known_limitations": ["forward 30d dry-run not completed", "not live trading ready"]})
    _write_text(project / "outputs/system/QUICK_STATUS.md", "forward 30d dry-run not completed\nnot live trading ready\n")
    _write_text(project / "docs/COMMAND_COOKBOOK.md", "Resume project\nFind reports\nCheck safety\nWhat not to do\n")
    return ProjectPaths(workspace_root=workspace)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_usability_audit_generates_json_and_markdown(usability_paths: ProjectPaths) -> None:
    result = run_usability_audit(usability_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["overall_passed"] is True


def test_missing_report_index_blocking(usability_paths: ProjectPaths) -> None:
    (usability_paths.data_dir / "system" / "report_index.json").unlink()

    result = run_usability_audit(usability_paths)

    assert result["overall_passed"] is False
    assert any("report_index" in reason for reason in result["blocking_reasons"])


def test_missing_artifact_browser_blocking(usability_paths: ProjectPaths) -> None:
    (usability_paths.data_dir / "system" / "artifact_browser.json").unlink()

    result = run_usability_audit(usability_paths)

    assert result["overall_passed"] is False
    assert any("artifact_browser" in reason for reason in result["blocking_reasons"])


def test_missing_quick_status_blocking(usability_paths: ProjectPaths) -> None:
    (usability_paths.data_dir / "system" / "quick_status.json").unlink()

    result = run_usability_audit(usability_paths)

    assert result["overall_passed"] is False
    assert any("quick_status" in reason for reason in result["blocking_reasons"])


def test_bad_final_handoff_wording_blocking(usability_paths: ProjectPaths) -> None:
    (usability_paths.outputs_dir / "system" / "FINAL_HANDOFF_REVIEW_REPORT.md").write_text("parameter sweep has shadow candidates\n", encoding="utf-8")

    result = run_usability_audit(usability_paths)

    assert result["overall_passed"] is False
    assert any("final_handoff_wording" in reason for reason in result["blocking_reasons"])


def test_usability_report_contains_recommended_tag_and_boundary(usability_paths: ProjectPaths) -> None:
    result = run_usability_audit(usability_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert RELEASE_CANDIDATE in report
    assert "No trading functionality was added." in report


def test_usability_audit_does_not_write_protected_ledgers(usability_paths: ProjectPaths) -> None:
    run_usability_audit(usability_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = usability_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_usability_audit_cli_smoke(usability_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: usability_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["usability-audit"]) == 0
