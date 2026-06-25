from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, real_fixture_path, write_json
from trading_core.global_briefing.real_package_integration_report import build_global_briefing_real_package_report
from trading_core.global_briefing.real_package_manifest import build_global_briefing_package_manifest
from trading_core.global_briefing.real_package_replay_workflow import run_global_briefing_real_package_replay


def _workflow_stack(paths):
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
    return manifest, workflow


def test_report_json_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _workflow_stack(paths)
    result = build_global_briefing_real_package_report(paths=paths)

    assert Path(result["json_path"]).exists()
    assert result["overall_status"] == "research_review_ready"


def test_report_markdown_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _workflow_stack(paths)
    result = build_global_briefing_real_package_report(paths=paths)

    assert "# Global Briefing Real Package Integration Report" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_missing_manifest_warning(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = build_global_briefing_real_package_report(paths=paths)

    assert any("missing manifest" in item for item in result["warnings"])


def test_missing_workflow_warning(tmp_path: Path) -> None:
    result = build_global_briefing_real_package_report(paths=make_paths(tmp_path))

    assert any("missing workflow" in item for item in result["warnings"])


def test_failed_workflow_needs_attention(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    build_global_briefing_package_manifest(root="tests/fixtures/global_briefing_real", paths=paths)
    workflow = run_global_briefing_real_package_replay(
        real_fixture_path(paths, "real_package_aliases.csv"),
        real_fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        package_id="GB-REAL-FIXTURE",
        source="global_briefing",
        version="v1",
        min_coverage=0.90,
        strict=True,
        paths=paths,
    )

    result = build_global_briefing_real_package_report(workflow_path=workflow["json_path"], paths=paths)

    assert result["overall_status"] == "needs_attention"


def test_coverage_ratio_and_limitations_recorded(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _workflow_stack(paths)
    result = build_global_briefing_real_package_report(paths=paths)

    assert result["coverage_ratio"] == 0.6
    assert "This does not validate forward dry-run." in result["known_limitations"]


def test_report_contains_limitations(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _workflow_stack(paths)
    result = build_global_briefing_real_package_report(paths=paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "This does not validate forward dry-run." in report
    assert "This does not prove strategy effectiveness." in report


def test_report_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _workflow_stack(paths)
    result = build_global_briefing_real_package_report(paths=paths)

    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)


def test_report_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _workflow_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["global-briefing-real-package-report"]) == 0
