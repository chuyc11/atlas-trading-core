from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.full_historical_proxy_workflow import run_full_historical_proxy_replay
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_package_normalizer import normalize_historical_data_packages


def _stack(paths):
    download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)
    normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)


def test_fixture_proxy_workflow_success(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = run_full_historical_proxy_replay(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    assert result["overall_status"] == "research_review_ready"
    assert result["boundary"]["isolated_replay_ledger_written"] is True


def test_missing_proxy_or_validation_failure_stops(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = run_full_historical_proxy_replay(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    assert result["overall_status"] == "needs_attention"
    bad = paths.project_root / "bad.jsonl"
    bad.write_text('{"as_of_date":"bad"}\n', encoding="utf-8")
    result = run_full_historical_proxy_replay(signals_path=str(bad), prices_path="tests/fixtures/historical_data/prices_valid.csv", start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    assert result["overall_status"] == "needs_attention"


def test_coverage_failure_strict_stops(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = run_full_historical_proxy_replay(prices_path="tests/fixtures/global_briefing_real/prices_valid.csv", start_date="2024-01-02", end_date="2024-01-08", min_coverage=1.1, strict=True, paths=paths)
    assert result["overall_status"] == "needs_attention"


def test_proxy_workflow_boundaries_and_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _stack(paths)
    result = run_full_historical_proxy_replay(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    assert result["boundary"]["main_ledger_written"] is False
    assert result["boundary"]["labels_used"] is False
    assert result["boundary"]["ml_shadow_used"] is False
    assert result["boundary"]["experiments_used"] is False
    assert result["boundary"]["promotion_triggered"] is False
    assert_no_protected_paths(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["run-full-historical-proxy-replay", "--start-date", "2024-01-02", "--end-date", "2024-01-08"]) == 0
