from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_continuation_test_utils import make_day1_continuation_paths
from trading_core.forward_dry_run.day1_artifact_manifest import build_day1_artifact_manifest
from trading_core.forward_dry_run.day1_reproducibility_manifest import build_day1_reproducibility_manifest


def test_day1_reproducibility_manifest_records_sources_and_boundaries(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    build_day1_artifact_manifest(paths=paths)
    result = build_day1_reproducibility_manifest(paths=paths)
    assert result["overall_passed"] is True
    assert result["baseline_tag"] == "v0.6.3-forward-dry-run-day1-executed-audited"
    assert result["day1_as_of_date"] == "2026-06-25"
    assert result["source_hashes"]["market_data"]["sha256"]
    assert result["artifact_hashes"]["day1_post_execution_audit"]
    assert result["determinism_policy"]["hashes_exclude_generated_at"] is True
    assert result["external_api_called"] is False
    assert result["real_time_market_data_downloaded"] is False
    assert result["boundary"]["day2_executed"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_day1_reproducibility_manifest_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_continuation_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-reproducibility-manifest"]) == 0

