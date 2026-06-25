from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, real_fixture_path, write_json
from trading_core.global_briefing.evidence_quality_audit import RELEASE_CANDIDATE, audit_global_briefing_evidence_quality
from trading_core.global_briefing.evidence_quality_report import build_global_briefing_evidence_quality_report
from trading_core.global_briefing.production_package_acceptance import build_global_briefing_production_acceptance_criteria
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
    build_global_briefing_evidence_quality_report(paths=paths)
    build_global_briefing_production_acceptance_criteria(paths=paths)


def test_evidence_quality_audit_json_and_markdown_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = audit_global_briefing_evidence_quality(paths=paths)

    assert Path(result["json_path"]).exists()
    assert "# Global Briefing Evidence Quality Audit" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_missing_warning_triage_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    (paths.data_dir / "system" / "global_briefing_warning_triage.json").unlink()

    result = audit_global_briefing_evidence_quality(paths=paths)

    assert any("warning_triage" in item for item in result["blocking_reasons"])


def test_missing_evidence_quality_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    (paths.data_dir / "system" / "global_briefing_evidence_quality.json").unlink()

    result = audit_global_briefing_evidence_quality(paths=paths)

    assert any("evidence_quality" in item for item in result["blocking_reasons"])


def test_missing_acceptance_criteria_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    (paths.data_dir / "system" / "global_briefing_production_acceptance_criteria.json").unlink()

    result = audit_global_briefing_evidence_quality(paths=paths)

    assert any("production_acceptance_criteria" in item for item in result["blocking_reasons"])


def test_production_ready_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    evidence_path = paths.data_dir / "system" / "global_briefing_evidence_quality.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["production_readiness"]["ready"] = True
    write_json(evidence_path, payload)

    result = audit_global_briefing_evidence_quality(paths=paths)

    assert any("production_readiness.ready" in item for item in result["blocking_reasons"])


def test_low_coverage_thresholds_block(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    criteria_path = paths.data_dir / "system" / "global_briefing_production_acceptance_criteria.json"
    payload = json.loads(criteria_path.read_text(encoding="utf-8"))
    payload["required"]["min_coverage"] = 0.7
    payload["required"]["target_coverage"] = 0.8
    write_json(criteria_path, payload)

    result = audit_global_briefing_evidence_quality(paths=paths)

    assert any("min_coverage" in item for item in result["blocking_reasons"])
    assert any("target_coverage" in item for item in result["blocking_reasons"])


def test_forbidden_wording_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    (paths.outputs_dir / "system" / "GLOBAL_BRIEFING_EVIDENCE_QUALITY_REPORT.md").write_text("production global-briefing package validated\nlive trading ready\n", encoding="utf-8")

    result = audit_global_briefing_evidence_quality(paths=paths)

    assert any("wording" in item for item in result["blocking_reasons"])


def test_boundary_true_values_block(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    triage_path = paths.data_dir / "system" / "global_briefing_warning_triage.json"
    payload = json.loads(triage_path.read_text(encoding="utf-8"))
    payload["boundary"]["main_ledger_written"] = True
    payload["boundary"]["run_daily_called"] = True
    payload["boundary"]["network_access"] = True
    write_json(triage_path, payload)

    result = audit_global_briefing_evidence_quality(paths=paths)

    assert any("main_ledger_written" in item for item in result["blocking_reasons"])
    assert any("run_daily_called" in item for item in result["blocking_reasons"])
    assert any("network_access" in item for item in result["blocking_reasons"])


def test_report_contains_production_readiness_false_and_recommends_tag(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = audit_global_briefing_evidence_quality(paths=paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is True
    assert "Production readiness: false" in report
    assert RELEASE_CANDIDATE in report


def test_failed_audit_does_not_recommend_tag(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    (paths.data_dir / "system" / "global_briefing_warning_triage.json").unlink()
    result = audit_global_briefing_evidence_quality(paths=paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is False
    assert RELEASE_CANDIDATE not in report


def test_evidence_quality_audit_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = audit_global_briefing_evidence_quality(paths=paths)

    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["network_access"] is False
    assert_no_protected_paths(paths)


def test_evidence_quality_audit_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["audit-global-briefing-evidence-quality"]) == 0
