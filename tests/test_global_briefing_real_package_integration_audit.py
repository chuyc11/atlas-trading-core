from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import make_paths, real_fixture_path, write_json
from trading_core.global_briefing.real_package_integration_audit import RELEASE_CANDIDATE, audit_global_briefing_real_package_integration
from trading_core.global_briefing.real_package_integration_report import build_global_briefing_real_package_report
from trading_core.global_briefing.real_package_manifest import build_global_briefing_package_manifest
from trading_core.global_briefing.real_package_replay_workflow import run_global_briefing_real_package_replay


def _stack(paths):
    manifest = build_global_briefing_package_manifest(root="tests/fixtures/global_briefing_real", paths=paths)
    workflow = run_global_briefing_real_package_replay(
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
    report = build_global_briefing_real_package_report(paths=paths)
    return {"manifest": manifest, "workflow": workflow, "report": report}


def test_audit_json_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = audit_global_briefing_real_package_integration(paths=paths)

    assert Path(result["json_path"]).exists()
    assert result["overall_passed"] is True


def test_audit_markdown_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = audit_global_briefing_real_package_integration(paths=paths)

    assert "# Global Briefing Real Package Integration Audit" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_missing_manifest_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    (paths.data_dir / "system" / "global_briefing_package_manifest.json").unlink()

    result = audit_global_briefing_real_package_integration(paths=paths)

    assert any("manifest" in item for item in result["blocking_reasons"])


def test_validation_failed_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _stack(paths)
    validation_path = Path(artifacts["workflow"]["validation"])
    write_json(validation_path, {"overall_passed": False})

    result = audit_global_briefing_real_package_integration(paths=paths)

    assert any("validation" in item for item in result["blocking_reasons"])


def test_future_signal_leakage_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _stack(paths)
    coverage_path = Path(artifacts["workflow"]["coverage_audit"])
    coverage = __import__("json").loads(coverage_path.read_text(encoding="utf-8"))
    coverage["point_in_time"]["future_signal_rows"] = 1
    write_json(coverage_path, coverage)

    result = audit_global_briefing_real_package_integration(paths=paths)

    assert any("coverage" in item for item in result["blocking_reasons"])


def test_workflow_boundary_true_values_block(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _stack(paths)
    workflow_path = Path(artifacts["workflow"]["json_path"])
    workflow = __import__("json").loads(workflow_path.read_text(encoding="utf-8"))
    for key in ["main_ledger_written", "run_daily_called", "network_access", "labels_used", "ml_shadow_used", "experiments_used", "promotion_triggered"]:
        workflow["boundary"][key] = True
    write_json(workflow_path, workflow)

    result = audit_global_briefing_real_package_integration(paths=paths)

    for key in ["main_ledger_written", "run_daily_called", "network_access", "labels_used", "ml_shadow_used", "experiments_used", "promotion_triggered"]:
        assert any(key in item for item in result["blocking_reasons"])


def test_report_missing_limitations_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _stack(paths)
    report_path = Path(artifacts["report"]["json_path"])
    report = __import__("json").loads(report_path.read_text(encoding="utf-8"))
    report["known_limitations"] = []
    write_json(report_path, report)

    result = audit_global_briefing_real_package_integration(paths=paths)

    assert any("integration_report" in item for item in result["blocking_reasons"])


def test_forbidden_wording_live_trading_ready_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _stack(paths)
    Path(artifacts["workflow"]["report_path"]).write_text("live trading ready\n", encoding="utf-8")

    result = audit_global_briefing_real_package_integration(paths=paths)

    assert any("wording" in item for item in result["blocking_reasons"])


def test_protected_path_snapshot_unchanged(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = audit_global_briefing_real_package_integration(paths=paths)

    assert result["sections"]["protected_paths"]["passed"] is True


def test_overall_passed_recommends_v056_tag(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = audit_global_briefing_real_package_integration(paths=paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is True
    assert RELEASE_CANDIDATE in report


def test_overall_failed_does_not_recommend_tag(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    (paths.data_dir / "system" / "global_briefing_package_manifest.json").unlink()
    result = audit_global_briefing_real_package_integration(paths=paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is False
    assert RELEASE_CANDIDATE not in report


def test_integration_audit_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["audit-global-briefing-real-package-integration"]) == 0
