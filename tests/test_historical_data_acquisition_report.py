from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.full_historical_proxy_workflow import run_full_historical_proxy_replay
from trading_core.global_briefing.historical_data_acquisition_report import build_historical_data_acquisition_report
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_data_quality_audit import audit_historical_data_quality
from trading_core.global_briefing.historical_package_normalizer import normalize_historical_data_packages


def _stack(paths):
    download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)
    normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    audit_historical_data_quality(paths=paths)
    run_full_historical_proxy_replay(start_date="2024-01-02", end_date="2024-01-08", paths=paths)


def test_acquisition_report_generated_and_complete(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = build_historical_data_acquisition_report(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert "HIST-ETF-OHLCV-CN-HK-V1" in result["packages"]
    assert result["known_limitations"]


def test_acquisition_report_boundaries_and_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["historical-data-acquisition-report"]) == 0
    result = build_historical_data_acquisition_report(paths=paths)
    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)
