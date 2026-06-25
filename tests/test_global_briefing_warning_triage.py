from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, real_fixture_path, write_json
from trading_core.global_briefing.real_package_integration_audit import audit_global_briefing_real_package_integration
from trading_core.global_briefing.real_package_integration_report import build_global_briefing_real_package_report
from trading_core.global_briefing.real_package_manifest import build_global_briefing_package_manifest
from trading_core.global_briefing.real_package_replay_workflow import run_global_briefing_real_package_replay
from trading_core.global_briefing.warning_triage import build_global_briefing_warning_triage


def _stack(paths):
    build_global_briefing_package_manifest(root="tests/fixtures/global_briefing_real", paths=paths)
    run_global_briefing_real_package_replay(
        real_fixture_path(paths, "real_package_aliases.csv"),
        real_fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        package_id="GB-REAL-FIXTURE",
        source="global_briefing",
        version="v1",
        allow_carry_forward=True,
        min_coverage=0.60,
        paths=paths,
    )
    build_global_briefing_real_package_report(paths=paths)
    audit_global_briefing_real_package_integration(paths=paths)


def test_warning_triage_json_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_warning_triage(paths=paths)

    assert Path(result["json_path"]).exists()
    assert result["warning_count"] > 0


def test_warning_triage_markdown_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_warning_triage(paths=paths)

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "# Global Briefing Warning Triage" in report
    assert "GB-REAL-FIXTURE is not a production global-briefing package." in report


def test_coverage_warning_categorized_as_coverage_gap(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    coverage = write_json(paths.project_root / "coverage.json", {"warnings": ["missing signal dates: ['2024-01-04']"], "coverage": {"coverage_ratio": 0.6}})
    result = build_global_briefing_warning_triage(coverage_path=str(coverage), workflow_path=str(write_json(paths.project_root / "workflow.json", {"warnings": []})), report_path=str(write_json(paths.project_root / "report.json", {"warnings": [], "selected_package": "GB-REAL-FIXTURE"})), audit_path=str(write_json(paths.project_root / "audit.json", {"warnings": []})), paths=paths)

    assert result["warnings"][0]["category"] == "coverage_gap"


def test_adapter_warning_categorized_as_adapter_limitation(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    workflow = write_json(paths.project_root / "workflow.json", {"warnings": ["2024-01-02: missing price for 512880.SH; no order generated"]})
    result = build_global_briefing_warning_triage(coverage_path=str(write_json(paths.project_root / "coverage.json", {"warnings": [], "coverage": {"coverage_ratio": 1.0}})), workflow_path=str(workflow), report_path=str(write_json(paths.project_root / "report.json", {"warnings": [], "selected_package": "GB-REAL-FIXTURE"})), audit_path=str(write_json(paths.project_root / "audit.json", {"warnings": []})), paths=paths)

    assert result["warnings"][0]["category"] == "adapter_limitation"


def test_generated_at_warning_categorized_as_pit_ambiguity(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    coverage = write_json(paths.project_root / "coverage.json", {"warnings": ["row 1 generated_at timezone ambiguity"], "coverage": {"coverage_ratio": 1.0}})
    result = build_global_briefing_warning_triage(coverage_path=str(coverage), workflow_path=str(write_json(paths.project_root / "workflow.json", {"warnings": []})), report_path=str(write_json(paths.project_root / "report.json", {"warnings": [], "selected_package": "GB-REAL-FIXTURE"})), audit_path=str(write_json(paths.project_root / "audit.json", {"warnings": []})), paths=paths)

    assert result["warnings"][0]["category"] == "pit_ambiguity"
    assert result["warnings"][0]["severity"] == "high"


def test_unknown_warning_categorized_as_unknown(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    workflow = write_json(paths.project_root / "workflow.json", {"warnings": ["unmapped warning text"]})
    result = build_global_briefing_warning_triage(coverage_path=str(write_json(paths.project_root / "coverage.json", {"warnings": [], "coverage": {"coverage_ratio": 1.0}})), workflow_path=str(workflow), report_path=str(write_json(paths.project_root / "report.json", {"warnings": [], "selected_package": "GB-REAL-FIXTURE"})), audit_path=str(write_json(paths.project_root / "audit.json", {"warnings": []})), paths=paths)

    assert result["warnings"][0]["category"] == "unknown"
    assert result["warnings"][0]["severity"] == "medium"


def test_coverage_ratio_06_is_production_blocker_but_not_fixture_warning_blocker(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_warning_triage(paths=paths)

    assert result["coverage_ratio"] == 0.6
    assert result["production_blockers"]
    assert all(item["blocking"] is False for item in result["warnings"])


def test_future_leakage_warning_becomes_production_blocker(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    coverage = write_json(paths.project_root / "coverage.json", {"warnings": ["future signal leakage detected"], "coverage": {"coverage_ratio": 1.0}})
    result = build_global_briefing_warning_triage(coverage_path=str(coverage), workflow_path=str(write_json(paths.project_root / "workflow.json", {"warnings": []})), report_path=str(write_json(paths.project_root / "report.json", {"warnings": [], "selected_package": "GB-REAL-FIXTURE"})), audit_path=str(write_json(paths.project_root / "audit.json", {"warnings": []})), paths=paths)

    assert any("future signal leakage" in item for item in result["production_blockers"])


def test_warning_triage_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_warning_triage(paths=paths)

    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["network_access"] is False
    assert_no_protected_paths(paths)


def test_warning_triage_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["global-briefing-warning-triage"]) == 0
