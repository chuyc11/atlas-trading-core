from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, real_fixture_path
from trading_core.global_briefing.evidence_quality_report import build_global_briefing_evidence_quality_report
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
    build_global_briefing_warning_triage(paths=paths)


def test_evidence_quality_json_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_evidence_quality_report(paths=paths)

    assert Path(result["json_path"]).exists()


def test_evidence_quality_markdown_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_evidence_quality_report(paths=paths)

    assert "# Global Briefing Evidence Quality Report" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_fixture_and_coverage_quality_levels(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_evidence_quality_report(paths=paths)

    assert any("GB-REAL-FIXTURE" in item for item in result["evidence_levels"]["fixture_validated"])
    assert any("0.6" in item for item in result["evidence_levels"]["insufficient_for_production"])


def test_audit_passed_marked_engineering_validated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_evidence_quality_report(paths=paths)

    assert "Integration audit passed." in result["evidence_levels"]["engineering_validated"]


def test_strategy_forward_live_not_validated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_evidence_quality_report(paths=paths)
    not_validated = " ".join(result["evidence_levels"]["not_validated"])

    assert "Strategy effectiveness" in not_validated
    assert "Forward dry-run" in not_validated
    assert "Live trading readiness" in not_validated


def test_recommended_min_coverage_and_not_production_text(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_evidence_quality_report(paths=paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["production_readiness"]["recommended_min_coverage"] >= 0.8
    assert "does not validate production global-briefing historical coverage" in report


def test_evidence_quality_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_global_briefing_evidence_quality_report(paths=paths)

    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["network_access"] is False
    assert_no_protected_paths(paths)


def test_evidence_quality_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["global-briefing-evidence-quality-report"]) == 0
