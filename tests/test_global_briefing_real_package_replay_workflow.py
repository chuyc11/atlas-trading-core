from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, real_fixture_path, write_text
from trading_core.global_briefing.real_package_replay_workflow import run_global_briefing_real_package_replay


def _run(paths, **kwargs):
    options = {
        "start_date": "2024-01-02",
        "end_date": "2024-01-08",
        "package_id": "GB-REAL-FIXTURE",
        "source": "global_briefing",
        "version": "v1",
        "allow_carry_forward": True,
        "min_coverage": 0.60,
        "execution_mode": "isolated",
        "paths": paths,
    }
    options.update(kwargs)
    return run_global_briefing_real_package_replay(
        real_fixture_path(paths, "real_package_aliases.csv"),
        real_fixture_path(paths, "prices_valid.csv"),
        **options,
    )


def test_valid_package_workflow_success(tmp_path: Path) -> None:
    result = _run(make_paths(tmp_path))

    assert result["overall_status"] == "research_review_ready"
    assert Path(result["json_path"]).exists()


def test_normalization_failure_stops_workflow(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "bad.csv", "date,market\n2024-01-02,CN\n")
    result = run_global_briefing_real_package_replay("bad.csv", real_fixture_path(paths, "prices_valid.csv"), start_date="2024-01-02", end_date="2024-01-08", strict=True, paths=paths)

    assert result["overall_status"] == "needs_attention"
    assert "validation" not in result


def test_validation_failure_stops_workflow(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = run_global_briefing_real_package_replay(real_fixture_path(paths, "real_package_future.jsonl"), real_fixture_path(paths, "prices_valid.csv"), start_date="2024-01-03", end_date="2024-01-03", paths=paths)

    assert result["overall_status"] == "needs_attention"
    assert "bundle" not in result


def test_coverage_failure_strict_stops_workflow(tmp_path: Path) -> None:
    result = _run(make_paths(tmp_path), min_coverage=0.90, strict=True)

    assert result["overall_status"] == "needs_attention"
    assert "bundle" not in result


def test_workflow_summary_records_outputs_and_isolated_ledger(tmp_path: Path) -> None:
    result = _run(make_paths(tmp_path))

    for key in ["normalized_signals", "validation", "coverage_audit", "bundle", "replay", "evaluation"]:
        assert key in result
    assert result["boundary"]["isolated_replay_ledger_written"] is True


def test_workflow_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = _run(paths)

    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["network_access"] is False
    assert result["boundary"]["labels_used"] is False
    assert result["boundary"]["ml_shadow_used"] is False
    assert result["boundary"]["experiments_used"] is False
    assert_no_protected_paths(paths)


def test_workflow_markdown_contains_not_forward(tmp_path: Path) -> None:
    result = _run(make_paths(tmp_path))

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "not forward dry-run validation" in report


def test_workflow_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main([
        "run-global-briefing-real-package-replay",
        "--input", real_fixture_path(paths, "real_package_aliases.csv"),
        "--prices", real_fixture_path(paths, "prices_valid.csv"),
        "--start-date", "2024-01-02",
        "--end-date", "2024-01-08",
        "--package-id", "GB-REAL-FIXTURE",
        "--source", "global_briefing",
        "--version", "v1",
        "--allow-carry-forward",
        "--min-coverage", "0.60",
        "--execution-mode", "isolated",
    ]) == 0
