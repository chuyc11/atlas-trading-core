from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.planning.artifact_coverage_scanner import build_artifact_coverage_scan


def test_artifact_coverage_scanner_records_metadata_only(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    result = build_artifact_coverage_scan(paths=paths)
    assert result["counts"]["modules"] > 0
    assert result["counts"]["tests"] > 0
    assert result["counts"]["docs"] > 0
    assert result["read_policy"]["large_file_content_read"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert "Artifact Coverage Scan" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_artifact_coverage_scanner_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["artifact-coverage-scanner"]) == 0

