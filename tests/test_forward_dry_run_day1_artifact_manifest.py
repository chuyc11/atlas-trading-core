from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_continuation_test_utils import make_day1_continuation_paths
from trading_core.forward_dry_run.day1_artifact_manifest import build_day1_artifact_manifest


def test_day1_artifact_manifest_records_required_artifacts_and_hashes(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    result = build_day1_artifact_manifest(paths=paths)
    assert result["overall_passed"] is True
    assert result["required_artifacts_total"] == 11
    assert result["required_artifacts_present"] == 11
    assert result["missing_required_artifacts"] == []
    assert len(result["artifacts"]) >= 12
    assert "v064_blocking_preflight" in [item["name"] for item in result["artifacts"]]
    assert all(item["sha256"] for item in result["artifacts"] if item["exists"])
    assert result["boundary"]["day2_executed"] is False
    assert result["boundary"]["run_daily_called"] is False


def test_day1_artifact_manifest_blocks_missing_required_artifact(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    (paths.data_dir / "forward_dry_run" / "day_001" / "day1_operator_report.json").unlink()
    result = build_day1_artifact_manifest(paths=paths)
    assert result["overall_passed"] is False
    assert "data/forward_dry_run/day_001/day1_operator_report.json" in result["missing_required_artifacts"]


def test_day1_artifact_manifest_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_continuation_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-artifact-manifest"]) == 0

