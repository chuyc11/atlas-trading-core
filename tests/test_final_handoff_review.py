"""Tests for final handoff review report."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trading_core.system.final_handoff_review import build_final_handoff_review
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def handoff_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    project.mkdir(parents=True)
    _write_text(project / "VERSION", "v0.5.1-system-integrity-and-documentation")
    for path in [
        "RELEASE_NOTES.md",
        "README.md",
        "docs/ARCHITECTURE.md",
        "docs/SAFETY_BOUNDARY.md",
        "docs/RELEASE_MATRIX.md",
        "docs/CLI_REFERENCE.md",
        "docs/ARTIFACT_MAP.md",
        "docs/RUNBOOK.md",
        "docs/FORWARD_DRY_RUN_RUNBOOK.md",
        "outputs/audit/SYSTEM_INTEGRITY_AUDIT.md",
        "outputs/audit/BOUNDARY_REGRESSION_AUDIT.md",
    ]:
        _write_text(project / path, "# ok")
    _write_json(project / "data/system/system_integrity_audit.json", {"overall_passed": True})
    _write_json(project / "data/system/boundary_regression_audit.json", {"passed": True})
    _write_json(project / "data/system/cli_inventory.json", {"commands": []})
    _write_json(project / "data/system/artifact_inventory.json", {"artifacts": []})
    _write_json(project / "data/system/reporting_system_audit.json", {"overall_passed": True})
    _write_json(project / "data/experiments/experiment_system_audit.json", {"overall_passed": True})
    _write_json(project / "data/experiments/mistake_pattern_library.json", {"patterns": [{"pattern_id": "PATTERN-1"}]})
    _write_json(project / "data/system/project_status_summary.json", {"status": "watch"})
    _write_json(project / "data/system/system_dashboard.json", {"safety_boundary": {"live_trading": False}})
    _write_json(project / "data/experiments/promotion_simulation-test.json", {"summary": {"shadow_candidate": 0, "active_small_candidate": 0}})
    _write_json(project / "data/experiments/strategy_comparison-test.json", {"items": []})
    _write_json(project / "data/experiments/parameter_sweep-test.json", {"best_shadow_candidate": None})
    _write_json(project / "data/shadow/ml_shadow_leaderboard-test.json", {"shadow_recommendation": "watch"})
    return ProjectPaths(workspace_root=workspace)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_final_handoff_generates_json_and_markdown(handoff_paths: ProjectPaths) -> None:
    result = build_final_handoff_review(handoff_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["current_tag"] == "v0.5.1-system-integrity-and-documentation"
    assert result["latest_pytest_result"] == "381 passed, 1 skipped"


def test_missing_artifact_does_not_crash(tmp_path: Path) -> None:
    paths = ProjectPaths(workspace_root=tmp_path)

    result = build_final_handoff_review(paths)

    assert Path(result["json_path"]).exists()
    assert result["warnings"]


def test_integrity_passed_sets_research_workbench_ready(handoff_paths: ProjectPaths) -> None:
    result = build_final_handoff_review(handoff_paths)

    assert result["overall_status"] == "research_workbench_ready"


def test_missing_system_integrity_audit_warns(handoff_paths: ProjectPaths) -> None:
    (handoff_paths.data_dir / "system" / "system_integrity_audit.json").unlink()

    result = build_final_handoff_review(handoff_paths)

    assert result["overall_status"] == "needs_attention"
    assert any("system_integrity_audit" in warning for warning in result["warnings"])


def test_report_contains_required_boundaries(handoff_paths: ProjectPaths) -> None:
    result = build_final_handoff_review(handoff_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "not live trading ready" in report
    assert "forward 30d dry-run not completed" in report
    assert "strategy effectiveness not proven" in report
    assert "Shadow signals are not trading instructions." in report
    assert "Promotion simulation is not promotion." in report
    assert "Research reports are not admission gates." in report


def test_report_uses_latest_pytest_and_correct_sweep_candidate_wording(handoff_paths: ProjectPaths) -> None:
    result = build_final_handoff_review(handoff_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "381 passed, 1 skipped" in report
    assert "374 passed, 1 skipped" not in report
    assert "parameter sweep produced no eligible shadow candidate in the latest validated artifacts" in report
    assert "parameter sweep has shadow candidates" not in report


def test_handoff_does_not_write_protected_ledgers(handoff_paths: ProjectPaths) -> None:
    build_final_handoff_review(handoff_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = handoff_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_final_handoff_cli_smoke(handoff_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: handoff_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["final-handoff-review"]) == 0
    assert (handoff_paths.outputs_dir / "system" / "FINAL_HANDOFF_REVIEW_REPORT.md").exists()
